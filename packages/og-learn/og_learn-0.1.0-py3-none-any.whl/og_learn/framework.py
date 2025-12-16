"""
OG Framework - Core implementation of Overfit-to-Generalization

This module provides the main OGModel class that wraps LV (low-variance) models
with OG training strategy using HV (high-variance) models for pseudo-label generation.
"""

import numpy as np
import pandas as pd
import torch
import os
import subprocess
import threading
import webbrowser
import time
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.metrics import r2_score


def launch_tensorboard(logdir='runs', port=6006, open_browser=True):
    """
    Launch TensorBoard in background and optionally open browser.
    
    Parameters
    ----------
    logdir : str
        Directory containing TensorBoard logs
    port : int
        Port to run TensorBoard on
    open_browser : bool
        Whether to open browser automatically
    
    Returns
    -------
    process : subprocess.Popen
        TensorBoard process (call process.terminate() to stop)
    
    Example
    -------
    >>> tb_process = launch_tensorboard('runs')
    >>> # ... training ...
    >>> tb_process.terminate()  # Stop when done
    """
    try:
        # Kill any existing TensorBoard on this port
        if os.name == 'nt':  # Windows
            os.system(f'taskkill /f /im tensorboard.exe 2>nul')
        else:  # Unix
            os.system(f'pkill -f "tensorboard.*--port.*{port}" 2>/dev/null')
        
        # Launch TensorBoard
        process = subprocess.Popen(
            ['tensorboard', '--logdir', logdir, '--port', str(port)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        print(f"📊 TensorBoard started at http://localhost:{port}")
        print(f"   Log directory: {logdir}")
        
        # Open browser after a short delay
        if open_browser:
            def open_browser_delayed():
                time.sleep(2)
                webbrowser.open(f'http://localhost:{port}')
            threading.Thread(target=open_browser_delayed, daemon=True).start()
        
        return process
    except FileNotFoundError:
        print("⚠️ TensorBoard not found. Install with: pip install tensorboard")
        return None


def set_seed(seed):
    """Set random seed for reproducibility."""
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


class OGModel(BaseEstimator, RegressorMixin):
    """
    Overfit-to-Generalization Model
    
    Combines a high-variance (HV) model for pseudo-label generation with a 
    low-variance (LV) model for generalization, using density-aware sampling.
    
    The OG framework works by:
    1. Training HV model (e.g., LightGBM) on original data
    2. Each epoch of LV training:
       - Sample data with density-aware weighting (prioritize sparse regions)
       - Add noise to features (oscillation)
       - Generate pseudo-labels from HV model
       - Train LV model on pseudo-labels
    
    Parameters
    ----------
    hv : str or object
        High-variance model. Can be:
        - str: 'lightgbm', 'xgboost', 'catboost' (uses preset config)
        - object: Custom model with fit/predict interface
    
    lv : str or object  
        Low-variance model. Can be:
        - str: 'mlp', 'resnet', 'transformer' (uses preset config)
        - object: Custom model with fit/predict interface
    
    oscillation : float, default=0.05
        Noise injection level for pseudo-labels (controls regularization)
    
    sampling_alpha : float, default=0.1
        Weight for density-aware sampling (0=uniform, higher=more sparse-focused)
    
    epochs : int, default=100
        Number of training epochs for LV model
    
    early_stopping : bool, default=True
        Whether to use early stopping
    
    patience : int, default=5
        Early stopping patience (epochs without improvement)
    
    verbose : bool, default=True
        Whether to print training progress
    
    Examples
    --------
    >>> # Preset OG
    >>> og = OGModel(hv='lightgbm', lv='mlp')
    >>> og.fit(X_train, y_train, density=density_values)
    >>> predictions = og.predict(X_test)
    
    >>> # Custom OG
    >>> from lightgbm import LGBMRegressor
    >>> custom_hv = LGBMRegressor(n_estimators=500, num_leaves=300)
    >>> og = OGModel(hv=custom_hv, lv='mlp', oscillation=0.03)
    >>> og.fit(X_train, y_train, density=density_values)
    """
    
    def __init__(
        self,
        hv='lightgbm',
        lv='mlp',
        oscillation=0.05,
        sampling_alpha=0.1,
        epochs=100,
        early_stopping=False,
        patience=5,
        eval_every_epochs=5,
        verbose=True,
        seed=42,
        tensorboard_dir=None,
        tensorboard_name=None
    ):
        self.hv = hv
        self.lv = lv
        self.oscillation = oscillation
        self.sampling_alpha = sampling_alpha
        self.epochs = epochs
        self.early_stopping = early_stopping
        self.tensorboard_dir = tensorboard_dir
        self.tensorboard_name = tensorboard_name
        self.patience = patience
        self.eval_every_epochs = eval_every_epochs
        self.verbose = verbose
        self.seed = seed
        
        self._hv_model = None
        self._lv_model = None
        self._is_fitted = False
    
    def _get_hv_model(self, hv):
        """Get HV model instance."""
        if isinstance(hv, str):
            # Map aliases
            hv_map = {'lgb': 'lightgbm', 'xgb': 'xgboost', 'cat': 'catboost'}
            hv_name = hv_map.get(hv, hv)
            from .presets import get_hv_model
            return get_hv_model(hv_name)
        else:
            # Custom model instance
            return hv
    
    def _get_lv_model(self, lv, num_features):
        """Get LV model instance."""
        if isinstance(lv, str):
            from .presets import get_lv_model
            return get_lv_model(lv, num_features, epochs=self.epochs)
        else:
            # Custom model instance - ensure num_features is set if needed
            if hasattr(lv, 'num_features') and lv.num_features is None:
                lv.num_features = num_features
            return lv
    
    def fit(self, X, y, density=None, X_valid=None, y_valid=None):
        """
        Fit the OG model.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training features
        
        y : array-like of shape (n_samples,)
            Training targets
        
        density : array-like of shape (n_samples,), optional
            Data density at each sample location. Higher values = denser areas.
            If None, uniform sampling is used (no density-aware weighting).
        
        X_valid : array-like, optional
            Validation features for early stopping
        
        y_valid : array-like, optional  
            Validation targets for early stopping
        
        Returns
        -------
        self
        """
        # Set random seed for reproducibility
        set_seed(self.seed)
        
        # Convert to DataFrame for OG functions
        if isinstance(X, np.ndarray):
            X_df = pd.DataFrame(X, columns=[f'f{i}' for i in range(X.shape[1])])
        else:
            X_df = X.copy()
        
        if isinstance(y, np.ndarray):
            y_series = pd.Series(y)
        else:
            y_series = y.copy()
        
        # Prepare density column
        if density is not None:
            density_col = pd.Series(density, index=X_df.index)
        else:
            density_col = None
        
        n_samples, n_features = X_df.shape
        
        if self.verbose:
            print("=" * 60)
            print("OGModel Training")
            print("=" * 60)
        
        # Initialize HV model
        self._hv_model = self._get_hv_model(self.hv)
        if self.verbose:
            hv_name = self.hv if isinstance(self.hv, str) else type(self.hv).__name__
            print(f"  HV Model: {hv_name}")
        
        # Initialize LV model
        self._lv_model = self._get_lv_model(self.lv, n_features)
        if self.verbose:
            lv_name = self.lv if isinstance(self.lv, str) else type(self.lv).__name__
            print(f"  LV Model: {lv_name}")
            print(f"  Oscillation: {self.oscillation}")
            print(f"  Sampling Alpha: {self.sampling_alpha}")
            print(f"  Epochs: {self.epochs}")
            print("-" * 60)
        
        # Check if LV model supports OG training natively
        lv_has_og = hasattr(self._lv_model, 'fit') and 'OG_componment' in str(self._lv_model.fit.__code__.co_varnames)
        
        if lv_has_og:
            # LV model (MLP/ResNet/Transformer) has native OG support
            if self.verbose:
                print("\n[OG Training] Using native OG component in LV model...")
            
            # IMPORTANT: Always pass the HV model INSTANCE (not string)
            # This matches original OG_transformer behavior where model_type
            # receives either a model instance or one of: 'lgb', 'xgboost', 'catboost'
            # Since we already created _hv_model from presets, pass the instance
            hv_model_instance = self._hv_model
            
            # Debug: verify tensorboard params
            print(f"  📊 TensorBoard: {self.tensorboard_name} (dir={self.tensorboard_dir})")
            
            # LV model will handle OG internally
            self._lv_model.fit(
                X_df, y_series,
                X_valid=X_valid, y_valid=y_valid,
                OG_componment=True,
                oscillation=self.oscillation,
                sampling_alpha=self.sampling_alpha,
                density=density_col,
                model_type=hv_model_instance,  # Pass model instance, not string
                progress_bar=self.verbose,
                early_stopping=self.early_stopping,
                patience=self.patience,
                eval_every_epochs=self.eval_every_epochs,
                tensorboard_dir=self.tensorboard_dir,
                tensorboard_name=self.tensorboard_name
            )
        else:
            # Manual OG training for custom LV models
            if self.verbose:
                print("\n[Stage 1] Fitting HV model (overfit)...")
            
            from .og_core import initialize_OG_componment, generate_OG_componment
            
            # Fit HV model
            self._hv_model.fit(X_df, y_series)
            
            if self.verbose:
                train_pred = self._hv_model.predict(X_df)
                train_r2 = r2_score(y_series, train_pred)
                print(f"  → HV Training R²: {train_r2:.4f}")
                print("\n[Stage 2] Training LV model with OG strategy...")
            
            # Generate OG data and train LV model
            X_og, y_og = generate_OG_componment(
                self._hv_model, X_df,
                density_col=density_col,
                oscillation=self.oscillation,
                alpha=self.sampling_alpha
            )
            
            # Fit LV model on pseudo-labels
            self._lv_model.fit(X_og, y_og.values.ravel())
        
        self._is_fitted = True
        
        if self.verbose:
            # Final evaluation
            y_pred = self.predict(X)
            final_r2 = r2_score(y, y_pred)
            print("\n" + "=" * 60)
            print(f"✓ OGModel training complete")
            print(f"  Final Training R²: {final_r2:.4f}")
            print("=" * 60)
        
        return self
    
    def predict(self, X):
        """
        Predict using the fitted LV model.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Features to predict
        
        Returns
        -------
        y_pred : ndarray of shape (n_samples,)
            Predicted values
        """
        if not self._is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")
        
        if isinstance(X, np.ndarray):
            X_df = pd.DataFrame(X, columns=[f'f{i}' for i in range(X.shape[1])])
        else:
            X_df = X
        
        # Use LV model for prediction (generalization)
        return self._lv_model.predict(X_df)
    
    def score(self, X, y):
        """
        Calculate R² score on test data.
        """
        y_pred = self.predict(X)
        return r2_score(y, y_pred)


def compare_models(X_train, y_train, X_test, y_test, models, density=None, tensorboard_dir=None, eval_every_epochs=5, save_dir=None):
    """
    Compare multiple models on the same data.
    
    Parameters
    ----------
    X_train, y_train : Training data
    X_test, y_test : Test data
    models : dict
        Dictionary of {name: model} pairs
    density : array-like, optional
        Density values for OG models
    tensorboard_dir : str, optional
        Directory for TensorBoard logs. If provided, each model's training curves
        will be logged and viewable at http://localhost:6006 after running:
        `tensorboard --logdir=<tensorboard_dir>`
    eval_every_epochs : int, default=5
        How often to log metrics to TensorBoard (in epochs)
    save_dir : str, optional
        Directory to save/load models. If provided:
        - Models are saved as {save_dir}/{model_name}/model.pkl after training
        - If model.pkl exists, it's loaded instead of retraining
        Can be same as tensorboard_dir for convenience.
    
    Returns
    -------
    results : dict
        Dictionary of {name: r2_score}
    """
    import warnings
    import pickle
    warnings.filterwarnings('ignore', category=UserWarning, message='.*non-writable.*')
    
    results = {}
    
    print("=" * 60)
    print("Model Comparison")
    print("=" * 60)
    
    if tensorboard_dir:
        print(f"📊 TensorBoard: tensorboard --logdir={tensorboard_dir}")
        print(f"   Open http://localhost:6006 to view training curves")
    
    for name, model in models.items():
        # Check for saved model
        model_name_clean = name.replace(" ", "_").replace("→", "to").replace("(", "").replace(")", "")
        model_path = None
        if save_dir:
            model_dir = os.path.join(save_dir, model_name_clean)
            model_path = os.path.join(model_dir, "model.pkl")
            
            # Try to load existing model
            if os.path.exists(model_path):
                print(f"\nLoading: {name} (from {model_path})")
                try:
                    # Check if it's an OG model (we saved just the LV model)
                    is_og = 'OG' in name or model.__class__.__name__ == 'OGModel'
                    if is_og:
                        # Load LV model and set it on the OGModel
                        with open(model_path, 'rb') as f:
                            lv_model = pickle.load(f)
                        model._lv_model = lv_model
                        model._is_fitted = True
                    else:
                        with open(model_path, 'rb') as f:
                            model = pickle.load(f)
                    y_pred = model.predict(X_test)
                    r2 = r2_score(y_test, y_pred)
                    results[name] = r2
                    print(f"  → R²: {r2:.4f} (loaded)")
                    continue  # Skip to next model
                except Exception as e:
                    print(f"  ⚠️ Failed to load, retraining: {e}")
        
        print(f"\nTraining: {name}...")
        
        try:
            # Check if it's an OG model (use class name check for robustness across imports)
            is_og_model = isinstance(model, OGModel) or model.__class__.__name__ == 'OGModel'
            
            if is_og_model:
                # Suppress verbose output in batch mode
                model.verbose = False
                # Set tensorboard for OG models
                if tensorboard_dir:
                    model.tensorboard_dir = tensorboard_dir
                    model.tensorboard_name = name.replace(" ", "_").replace("→", "to").replace("(", "").replace(")", "")
                    # Ensure eval_every_epochs is set for logging
                    if model.eval_every_epochs is None:
                        model.eval_every_epochs = eval_every_epochs
                if density is not None:
                    model.fit(X_train, y_train, density=density, X_valid=X_test, y_valid=y_test)
                else:
                    model.fit(X_train, y_train, X_valid=X_test, y_valid=y_test)
            elif hasattr(model, 'fit'):
                # Check if the model supports tensorboard (e.g., our MLPRegressor)
                if tensorboard_dir and hasattr(model.fit, '__code__'):
                    fit_params = model.fit.__code__.co_varnames
                    if 'tensorboard_dir' in fit_params:
                        # Pass tensorboard params AND eval_every_epochs to enable logging
                        # Suppress progress bar in batch mode
                        model.fit(X_train, y_train, 
                                 X_valid=X_test, y_valid=y_test,
                                 tensorboard_dir=tensorboard_dir,
                                 tensorboard_name=name.replace(" ", "_").replace("(", "").replace(")", ""),
                                 eval_every_epochs=eval_every_epochs,
                                 progress_bar=False)
                    else:
                        model.fit(X_train, y_train)
                else:
                    model.fit(X_train, y_train)
            
            y_pred = model.predict(X_test)
            r2 = r2_score(y_test, y_pred)
            results[name] = r2
            print(f"  → R²: {r2:.4f}")
            
            # Save model if save_dir is specified
            if save_dir and model_path:
                os.makedirs(os.path.dirname(model_path), exist_ok=True)
                try:
                    # For OGModel, save the internal LV model (avoids autoreload issues)
                    if is_og_model and hasattr(model, '_lv_model'):
                        with open(model_path, 'wb') as f:
                            pickle.dump(model._lv_model, f)
                    else:
                        with open(model_path, 'wb') as f:
                            pickle.dump(model, f)
                    print(f"  💾 Saved to {model_path}")
                except Exception as e:
                    print(f"  ⚠️ Could not save model: {e}")
            
        except Exception as e:
            print(f"  → Error: {e}")
            results[name] = None
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("-" * 60)
    for name, r2 in sorted(results.items(), key=lambda x: x[1] or 0, reverse=True):
        if r2 is not None:
            print(f"  {name}: {r2:.4f}")
        else:
            print(f"  {name}: Failed")
    print("=" * 60)
    
    return results

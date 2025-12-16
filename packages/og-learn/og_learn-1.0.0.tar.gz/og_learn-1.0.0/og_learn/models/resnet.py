import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.utils.validation import check_is_fitted
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
from tqdm.auto import tqdm
from sklearn.metrics import r2_score
import joblib
import os
import pandas as pd
from IPython.display import display, update_display, HTML
import base64
import matplotlib.pyplot as plt
import time

class ResidualBlock(nn.Module):
    def __init__(self, dim, dropout=0.1, activation='relu'):
        super().__init__()
        
        # First layer
        self.linear1 = nn.Linear(dim, dim)
        self.norm1 = nn.BatchNorm1d(dim)
        
        # Second layer
        self.linear2 = nn.Linear(dim, dim)
        self.norm2 = nn.BatchNorm1d(dim)
        
        # Activation and dropout
        if activation == 'relu':
            self.activation = nn.ReLU()
        elif activation == 'gelu':
            self.activation = nn.GELU()
        elif activation == 'tanh':
            self.activation = nn.Tanh()
        else:
            self.activation = nn.ReLU()
            
        self.dropout = nn.Dropout(dropout) if dropout > 0 else nn.Identity()
    
    def forward(self, x):
        residual = x
        
        # First transformation
        out = self.linear1(x)
        out = self.norm1(out)
        out = self.activation(out)
        out = self.dropout(out)
        
        # Second transformation
        out = self.linear2(out)
        out = self.norm2(out)
        
        # Add residual connection
        out = out + residual
        out = self.activation(out)
        
        return out


class ResNetTabular(nn.Module):
    def __init__(self, num_features, hidden_dim=512, num_blocks=4, dropout=0.1, activation='relu'):
        super().__init__()
        
        # Input projection
        self.input_projection = nn.Linear(num_features, hidden_dim)
        self.input_norm = nn.BatchNorm1d(hidden_dim)
        
        # Activation
        if activation == 'relu':
            self.activation = nn.ReLU()
        elif activation == 'gelu':
            self.activation = nn.GELU()
        elif activation == 'tanh':
            self.activation = nn.Tanh()
        else:
            self.activation = nn.ReLU()
        
        # Residual blocks
        self.blocks = nn.ModuleList([
            ResidualBlock(hidden_dim, dropout, activation) 
            for _ in range(num_blocks)
        ])
        
        # Output layers
        self.output_norm = nn.BatchNorm1d(hidden_dim)
        self.output_projection = nn.Linear(hidden_dim, 1)
        
        # Dropout
        self.dropout = nn.Dropout(dropout) if dropout > 0 else nn.Identity()
    
    def forward(self, x):
        # Input projection
        x = self.input_projection(x)
        x = self.input_norm(x)
        x = self.activation(x)
        x = self.dropout(x)
        
        # Pass through residual blocks
        for block in self.blocks:
            x = block(x)
        
        # Output
        x = self.output_norm(x)
        x = self.dropout(x)
        x = self.output_projection(x)
        
        return x


class ResNetRegressor(BaseEstimator, RegressorMixin):
    def __init__(self, num_features, hidden_dim=512, num_blocks=4, dropout=0.1, activation='relu',
                 lr=1e-3, batch_size=1024, epochs=10, eval_every_samples=50, device=None):
        self.num_features = num_features
        self.hidden_dim = hidden_dim
        self.num_blocks = num_blocks
        self.dropout = dropout
        self.activation = activation
        self.lr = lr
        self.batch_size = batch_size
        self.epochs = epochs
        self.eval_every_samples = eval_every_samples
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

    def evaluate(self, val_loader):
        self.model_.eval()
        val_preds = []
        val_targets = []
        with torch.no_grad():
            for xb, yb in val_loader:
                xb = xb.to(self.device)
                preds = self.model_(xb).cpu().numpy()
                val_preds.append(preds)
                val_targets.append(yb.numpy())
        
        val_preds = np.concatenate(val_preds, axis=0)
        val_targets = np.concatenate(val_targets, axis=0)
        return r2_score(val_targets, val_preds)

    def plot_training_history(self, train_history, val_history, epoch_history, save_path='resnet_training_history.png'):
        plt.close('all')  
        
        fig, ax = plt.subplots(figsize=(8, 4.5))
        
        ax.plot(epoch_history, train_history, 'b-', label='Train R2')
        if val_history:
            ax.plot(epoch_history, val_history, 'r-', label='Validation R2')
        ax.set_title('ResNet R2 Score during Training')
        ax.set_xlabel('Epochs')
        ax.set_ylabel('R2 Score')
        ax.set_ylim(0, 1)
        ax.grid(True)
        ax.legend()
        
        # Save plot
        fig.savefig(save_path, dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        import gc
        gc.collect()
        
        return save_path

    def dataloader(self, X, y, batch_size=None, shuffle=True):
        X = X.values.astype(np.float32) if isinstance(X, pd.DataFrame) else X
        y = y.values.ravel().astype(np.float32) if isinstance(y, (pd.Series, pd.DataFrame)) else y
        
        X_tensor = torch.from_numpy(X)
        y_tensor = torch.from_numpy(y).view(-1, 1)
        dataset = TensorDataset(X_tensor, y_tensor)
        
        return DataLoader(dataset, 
                         batch_size=batch_size or self.batch_size,
                         shuffle=shuffle)

    def fit(self, X, y, X_valid=None, y_valid=None, OG_componment=False, oscillation=0.05, 
            log_path=None, sampling_alpha=0.1, density=None, progress_bar=False, 
            early_stopping=False, patience=5, monitor_curve=False, eval_every_samples=None, 
            eval_every_seconds=None, eval_every_epochs=None, model_type="lgb",
            tensorboard_dir=None, tensorboard_name=None):
        
        # Import OG functions
        from ..og_core import generate_OG_componment, initialize_OG_componment
        
        # TensorBoard setup
        tb_writer = None
        if tensorboard_dir is not None:
            try:
                from torch.utils.tensorboard import SummaryWriter
                run_name = tensorboard_name or f"ResNet_{time.strftime('%Y%m%d_%H%M%S')}"
                log_dir = os.path.join(tensorboard_dir, run_name)
                tb_writer = SummaryWriter(log_dir=log_dir)
                print(f"  📊 TensorBoard: {run_name}")
            except ImportError:
                print("Warning: tensorboard not installed. Run: pip install tensorboard")
        
        samples_processed = 0  # ✅ Fixed: Start from 0
        train_r2_history = []
        val_r2_history = []
        epoch_history = []
        self.eval_every_samples = eval_every_samples
        self.eval_every_seconds = eval_every_seconds
        
        # Initialize time variables
        start_training_time = time.time()
        last_eval_time = time.time()  # ✅ Fixed: Initialize unconditionally
        
        train_loader = self.dataloader(X, y, shuffle=True)
        
        val_loader = None
        if X_valid is not None and y_valid is not None:
            eval_val_size = min(100000, len(X_valid))
            random_indices = np.random.choice(len(X_valid), eval_val_size, replace=False)
            X_valid_subset = X_valid[random_indices] if isinstance(X_valid, np.ndarray) else X_valid.iloc[random_indices]
            y_valid_subset = y_valid[random_indices] if isinstance(y_valid, np.ndarray) else y_valid.iloc[random_indices]
            val_loader = self.dataloader(X_valid_subset, y_valid_subset, shuffle=False)

        eval_train_size = min(100000, len(X))
        random_indices = np.random.choice(len(X), eval_train_size, replace=False)
        
        X_subset = X[random_indices] if isinstance(X, np.ndarray) else X.iloc[random_indices]
        y_subset = y[random_indices] if isinstance(y, np.ndarray) else y.iloc[random_indices]
        
        eval_train_loader = self.dataloader(X_subset, y_subset, shuffle=False)

        # Initialize model
        self.model_ = ResNetTabular(
            num_features=self.num_features,
            hidden_dim=self.hidden_dim,
            num_blocks=self.num_blocks,
            dropout=self.dropout,
            activation=self.activation
        ).to(self.device)

        optimizer = torch.optim.Adam(self.model_.parameters(), lr=self.lr)
        loss_fn = nn.MSELoss()
        val_r2 = 0
        train_r2 = 0  
        # Early stopping variables
        best_val_r2 = -float('inf')
        epochs_without_improvement = 0
        best_model_state = None
        
        # Evaluation tracking
        last_eval_epoch = -1

        # ✅ Fixed: Initialize display only if needed
        history_display = None
        if monitor_curve:
            history_display = display(HTML(""), display_id=True)

        # Initialize OG component if needed
        if OG_componment == True:
            model = initialize_OG_componment(X, y,model_type=model_type)
            
        for epoch in range(self.epochs):
            if OG_componment == True:
                X_mem, y_mem = generate_OG_componment(model, X, oscillation=oscillation, 
                                                    density_col=density, alpha=sampling_alpha, 
                                                    label='pseudo_label')
                train_mem_loader = self.dataloader(X_mem, y_mem, shuffle=True)
                train_loader = train_mem_loader

            self.model_.train()
                
            # Progress bar handling
            if progress_bar:
                pbar = tqdm(enumerate(train_loader), total=len(train_loader), 
                        desc=f"Epoch {epoch+1}/{self.epochs}", 
                        leave=False)
                
                pbar.set_postfix({ 
                            'train_r2': f'{train_r2:.4f}',
                            'val_r2': f'{val_r2:.4f}',
                            'best_val_r2': f'{best_val_r2:.4f}' if early_stopping and best_val_r2 > -float('inf') else '',
                            'patience': f'{epochs_without_improvement}/{patience}' if early_stopping else ''
                        })


            else:
                pbar = enumerate(train_loader)
            
            for batch_idx, (xb, yb) in pbar:
                xb, yb = xb.to(self.device), yb.to(self.device)

                # Forward pass
                preds = self.model_(xb)
                loss = loss_fn(preds, yb)
                
                # Backpropagation
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                samples_processed += xb.size(0)
                
                # ✅ Fixed: Decide whether to evaluate (same logic as MLP)
                should_evaluate = False
                eval_reason = None  # Track why we're evaluating
                if val_loader is not None:
                    if eval_every_epochs is not None:
                        # Epoch-based evaluation (only check at end of epoch to avoid performance issues)
                        # Always evaluate at epoch 0 and then every eval_every_epochs
                        if batch_idx == len(train_loader) - 1 and (epoch == 1 or (epoch + 1) % eval_every_epochs == 0):
                            should_evaluate = True
                            eval_reason = 'epochs'
                    elif eval_every_seconds is not None:
                        current_time = time.time()
                        if current_time - last_eval_time >= eval_every_seconds:
                            should_evaluate = True
                            eval_reason = 'seconds'
                            last_eval_time = current_time
                    elif self.eval_every_samples is not None:
                        if samples_processed >= self.eval_every_samples:
                            should_evaluate = True
                            eval_reason = 'samples'
                
                # Evaluate on validation set
                if should_evaluate:
                    val_r2 = self.evaluate(val_loader)
                    val_r2_history.append(val_r2)
                    self.model_.train()

                    train_r2 = self.evaluate(eval_train_loader)
                    train_r2_history.append(train_r2)
                    current_epoch = epoch + (batch_idx + 1) / len(train_loader)
                    epoch_history.append(current_epoch)
                    
                    # TensorBoard logging (use epoch as x-axis)
                    if tb_writer is not None:
                        tb_writer.add_scalar('R2_train', train_r2, epoch + 1)
                        tb_writer.add_scalar('R2_val', val_r2, epoch + 1)
                        tb_writer.add_scalar('Loss_train', loss.item(), epoch + 1)
                        if epoch == 0:
                            tb_writer.add_text('Note', 'X-axis (step) = Epoch number', 0)
                    
                    # ✅ Fixed: Early stopping check (moved here to align with evaluation)
                    if early_stopping:
                        if val_r2 > best_val_r2:
                            best_val_r2 = val_r2
                            epochs_without_improvement = 0
                            best_model_state = {k: v.clone() for k, v in self.model_.state_dict().items()}
                        else:
                            epochs_without_improvement += 1
                        
                        if epochs_without_improvement >= patience:
                            if best_model_state is not None:
                                self.model_.load_state_dict(best_model_state)
                                print(f"Early stopping triggered after {patience} evaluations without improvement")
                            return self

                    if progress_bar:
                        pbar.set_postfix({
                            'train_loss': f'{loss.item():.4f}',
                            'train_r2': f'{train_r2:.4f}',
                            'val_r2': f'{val_r2:.4f}',
                            'best_val_r2': f'{best_val_r2:.4f}' if early_stopping and best_val_r2 > -float('inf') else '',
                            'patience': f'{epochs_without_improvement}/{patience}' if early_stopping else ''
                        })

                    # ✅ Fixed: Generate and display training curve if monitor_curve is enabled
                    if monitor_curve:
                        img_path = self.plot_training_history(train_r2_history, val_r2_history, epoch_history)
                                                
                        # Read and convert to base64
                        try:
                            with open(img_path, 'rb') as img_file:
                                img_str = base64.b64encode(img_file.read()).decode()
                            
                            history_html = f'<img src="data:image/png;base64,{img_str}">'
                            if history_display is not None:
                                update_display(HTML(history_html), display_id=history_display.display_id)
                            
                            if os.path.exists(img_path):
                                os.remove(img_path)
                                
                        except Exception as e:
                            print(f"Error displaying training history: {e}")

                    self.model_.train()
                    
                    # ✅ Fixed: Only reset samples_processed if evaluation was triggered by samples
                    if eval_reason == 'samples':
                        samples_processed = 0

            # Note: Early stopping logic moved to evaluation section for consistency

        # Load best model if early stopping was used
        if early_stopping and best_model_state is not None and epochs_without_improvement < patience:
            self.model_.load_state_dict(best_model_state)

        # Save training history
        if log_path:
            # Calculate elapsed time for each evaluation
            history_df = pd.DataFrame({
                'train_r2': train_r2_history,
                'val_r2': val_r2_history,
                'epoch': epoch_history,
                'seconds': time.time() - start_training_time
            })
            history_path = log_path
            history_df.to_csv(history_path, index=False)
        
        # Close TensorBoard writer
        if tb_writer is not None:
            tb_writer.close()
            
        return self

    def predict(self, X):
        check_is_fitted(self, 'model_')
        if isinstance(X, pd.DataFrame):
            X = X.values.astype(np.float32)
        
        # Process in batches
        batch_size = 100000
        n_samples = len(X)
        predictions = []
        
        pbar = tqdm(total=(n_samples // batch_size) + (1 if n_samples % batch_size else 0), 
                   desc='Predicting')
        
        for i in range(0, n_samples, batch_size):
            batch = X[i:min(i + batch_size, n_samples)]
            X_tensor = torch.from_numpy(batch).to(self.device)
            self.model_.eval()
            with torch.no_grad():
                preds = self.model_(X_tensor)
                predictions.append(preds.cpu().numpy().flatten())
            pbar.update(1)
            
        pbar.close()
        return np.concatenate(predictions)
    
    def predict_with_uncertainty(self, X, n_samples=50):
        check_is_fitted(self, 'model_')
        if isinstance(X, pd.DataFrame):
            X = X.values.astype(np.float32)
        X_tensor = torch.from_numpy(X).to(self.device)
        
        # Enable dropout for uncertainty
        self.model_.train()
        
        predictions = []
        with torch.no_grad():
            for _ in range(n_samples):
                pred = self.model_(X_tensor)
                predictions.append(pred.cpu().numpy())
        
        predictions = np.array(predictions)
        mean_pred = predictions.mean(axis=0)
        std_pred = predictions.std(axis=0)
        
        return mean_pred.flatten(), std_pred.flatten() 
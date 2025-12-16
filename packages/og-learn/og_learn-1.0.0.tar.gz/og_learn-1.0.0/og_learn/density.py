"""
Data density calculation utilities.
"""

import numpy as np
import pandas as pd
from typing import Optional
from tqdm.auto import tqdm


def calculate_density(
    df: pd.DataFrame,
    radius: float = 500,
    reference_idx: Optional[np.ndarray] = None,
    output_idx: Optional[np.ndarray] = None,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Calculate weighted data density for each location.
    
    Density measures how many nearby observation stations exist.
    Higher density = more nearby stations.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with 'longitude' and 'latitude' columns
    radius : float, default=500
        Search radius in kilometers
    reference_idx : array-like, optional
        Indices of reference points to count. If None, uses all points.
    output_idx : array-like, optional
        Indices of points to calculate density for. If None, uses all points.
    verbose : bool, default=True
        Whether to show progress bar
    
    Returns
    -------
    df : pd.DataFrame
        Input DataFrame with new 'density' column added
    
    Example
    -------
    >>> df = calculate_density(df, radius=500)
    >>> print(f"Density range: {df['density'].min():.2e} - {df['density'].max():.2e}")
    """
    df = df.copy()
    
    if reference_idx is None:
        reference_idx = df.index
    if output_idx is None:
        output_idx = df.index
    
    # Get unique reference points
    ref_points = df.loc[reference_idx, ['longitude', 'latitude']].drop_duplicates().values
    
    # Get unique output points
    output_df = df.loc[output_idx, ['longitude', 'latitude']].drop_duplicates()
    output_points = output_df.values
    
    # Calculate area of search circle
    circle_area = np.pi * radius**2
    
    # Calculate density for each unique output point
    point_density = {}
    
    iterator = range(len(output_points))
    if verbose:
        iterator = tqdm(iterator, desc=f"Calculating density (r={radius}km)")
    
    for i in iterator:
        point = output_points[i]
        
        # Calculate distances to all reference points
        distances = _haversine_distance(
            point[0], point[1],
            ref_points[:, 0], ref_points[:, 1]
        )
        
        # Count neighbors within radius with distance weighting
        within_radius = distances <= radius
        if np.any(within_radius):
            weights = (radius - distances[within_radius]) / radius
            weighted_count = np.sum(weights)
        else:
            # Use nearest neighbor
            weighted_count = 0.1  # Small value for isolated points
        
        # Density = weighted count / area
        density = weighted_count / circle_area
        point_density[tuple(point)] = density
    
    # Map density values back to all rows
    all_output_coords = df.loc[output_idx, ['longitude', 'latitude']].values
    density_values = np.array([
        point_density.get(tuple(coord), 0) 
        for coord in all_output_coords
    ])
    
    df.loc[output_idx, 'density'] = density_values
    
    return df


def _haversine_distance(lon1, lat1, lon2, lat2):
    """
    Calculate great-circle distance in kilometers.
    
    Correctly handles crossing the date line.
    """
    R = 6371  # Earth radius in km
    
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    
    # Handle date line crossing
    dlon = (dlon + np.pi) % (2*np.pi) - np.pi
    
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    
    return R * c


def calculate_density_at_locations(
    target_lons, target_lats, 
    station_lons, station_lats, 
    radius: float = 500,
    verbose: bool = False
) -> np.ndarray:
    """
    Calculate density at arbitrary target locations based on station positions.
    
    This is useful for predicting accuracy at new locations where you need
    to compute density based on proximity to existing observation stations.
    
    Parameters
    ----------
    target_lons : array-like
        Longitude values of target locations
    target_lats : array-like
        Latitude values of target locations
    station_lons : array-like
        Longitude values of reference stations
    station_lats : array-like
        Latitude values of reference stations
    radius : float, default=500
        Search radius in kilometers
    verbose : bool, default=False
        Whether to show progress bar
    
    Returns
    -------
    densities : np.ndarray
        Density value for each target location
    
    Example
    -------
    >>> # Get station locations from training data
    >>> stations = df.drop_duplicates(subset=['longitude', 'latitude'])
    >>> station_lons = stations['longitude'].values
    >>> station_lats = stations['latitude'].values
    >>> 
    >>> # Calculate density at new locations
    >>> new_lons = [5.0, 10.0, 15.0]
    >>> new_lats = [50.0, 52.0, 54.0]
    >>> densities = calculate_density_at_locations(new_lons, new_lats, station_lons, station_lats)
    """
    target_lons = np.asarray(target_lons).flatten()
    target_lats = np.asarray(target_lats).flatten()
    station_lons = np.asarray(station_lons).flatten()
    station_lats = np.asarray(station_lats).flatten()
    
    # Get unique stations
    unique_stations = np.unique(np.column_stack([station_lons, station_lats]), axis=0)
    ref_lons = unique_stations[:, 0]
    ref_lats = unique_stations[:, 1]
    
    circle_area = np.pi * radius**2
    
    iterator = range(len(target_lons))
    if verbose:
        iterator = tqdm(iterator, desc=f"Calculating density (r={radius}km)")
    
    densities = []
    for i in iterator:
        distances = _haversine_distance(
            target_lons[i], target_lats[i],
            ref_lons, ref_lats
        )
        
        within_radius = distances <= radius
        if np.any(within_radius):
            weights = (radius - distances[within_radius]) / radius
            weighted_count = np.sum(weights)
        else:
            weighted_count = 0.1
        
        density = weighted_count / circle_area
        densities.append(density)
    
    return np.array(densities)


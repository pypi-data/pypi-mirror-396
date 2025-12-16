"""
Visualization utilities for TwoStageModel predictions.
"""

import numpy as np
import matplotlib.pyplot as plt

# Handle imports for both package and direct use
try:
    from ..data import calculate_density_at_locations
except ImportError:
    from data import calculate_density_at_locations


def plot_predicted_accuracy_map(
    ts_model,
    station_lons, station_lats,
    sufficiency,
    lon_range=(-10, 35),
    lat_range=(35, 70),
    grid_size=30,
    radius=500,
    figsize=(12, 4),
    show_stations=True,
    accuracy_range=None,
    cmap='Spectral_r'
):
    """
    Plot predicted accuracy map across a spatial grid.
    
    Args:
        ts_model: Fitted TwoStageModel
        station_lons: Array of station longitudes
        station_lats: Array of station latitudes  
        sufficiency: Sufficiency value for prediction
        lon_range: (min_lon, max_lon) for grid
        lat_range: (min_lat, max_lat) for grid
        grid_size: Number of grid points per axis
        radius: Radius for density calculation (km)
        figsize: Figure size
        show_stations: Whether to show station locations
        accuracy_range: (vmin, vmax) for accuracy colorbar
        cmap: Colormap for accuracy plot
        
    Returns:
        fig, axes: Matplotlib figure and axes
    """
    # Create grid
    lon_grid = np.linspace(lon_range[0], lon_range[1], grid_size)
    lat_grid = np.linspace(lat_range[0], lat_range[1], grid_size)
    lon_mesh, lat_mesh = np.meshgrid(lon_grid, lat_grid)
    
    # Calculate density for each pixel
    pixel_densities = calculate_density_at_locations(
        lon_mesh.ravel(), lat_mesh.ravel(),
        station_lons, station_lats, radius=radius
    )
    
    # Predict
    r2_grid = ts_model.predict(
        longitude=lon_mesh.ravel(),
        latitude=lat_mesh.ravel(),
        density=pixel_densities,
        sufficiency=sufficiency
    )
    
    # Auto-determine accuracy range if not provided
    if accuracy_range is None:
        vmin, vmax = np.nanmin(r2_grid), np.nanmax(r2_grid)
    else:
        vmin, vmax = accuracy_range
        # Clip to specified range for visualization
        r2_grid = np.clip(r2_grid, vmin, vmax)
    
    # Plot
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    
    # Left: Density map
    im1 = axes[0].contourf(lon_grid, lat_grid, pixel_densities.reshape(grid_size, grid_size), 
                           cmap='viridis', levels=20)
    plt.colorbar(im1, ax=axes[0], label='Density')
    if show_stations:
        axes[0].scatter(station_lons, station_lats, c='red', s=5, alpha=0.3, label='Stations')
        axes[0].legend(loc='upper right')
    axes[0].set_xlabel('Longitude')
    axes[0].set_ylabel('Latitude')
    axes[0].set_title('Station Density')
    axes[0].set_xlim(lon_range)
    axes[0].set_ylim(lat_range)
    
    # Right: Predicted R² map with accuracy_range
    levels = np.linspace(vmin, vmax, 21)
    im2 = axes[1].contourf(lon_grid, lat_grid, r2_grid.reshape(grid_size, grid_size), 
                           cmap=cmap, levels=levels, extend='both')
    plt.colorbar(im2, ax=axes[1], label='Predicted R²')
    axes[1].set_xlabel('Longitude')
    axes[1].set_ylabel('Latitude')
    axes[1].set_title(f'Predicted Accuracy (n={sufficiency:,})')
    axes[1].set_xlim(lon_range)
    axes[1].set_ylim(lat_range)
    
    plt.tight_layout()
    
    return fig, axes


def predict_at_locations(ts_model, lons, lats, station_lons, station_lats, sufficiency, radius=500):
    """
    Predict accuracy at specific locations.
    
    Args:
        ts_model: Fitted TwoStageModel
        lons: Target longitudes (scalar or array)
        lats: Target latitudes (scalar or array)
        station_lons: Station longitudes for density calculation
        station_lats: Station latitudes for density calculation
        sufficiency: Sufficiency value
        radius: Radius for density calculation (km)
        
    Returns:
        predictions: Predicted R² values
        densities: Calculated densities at locations
    """
    lons = np.atleast_1d(lons)
    lats = np.atleast_1d(lats)
    
    densities = calculate_density_at_locations(lons, lats, station_lons, station_lats, radius=radius)
    predictions = ts_model.predict(longitude=lons, latitude=lats, density=densities, sufficiency=sufficiency)
    
    return predictions, densities


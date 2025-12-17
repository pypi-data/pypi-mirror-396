import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import logging
import warnings
from typing import Optional, Union, Tuple, Dict, Any, List
from dask.diagnostics import ProgressBar

# Internal utility imports
# We assume these are available based on the package structure provided
from ..utils import (
    get_coord_name, 
    get_or_create_dask_client, 
    select_process_data, 
    get_spatial_mean
)

# Set up a logger for this module
logger = logging.getLogger(__name__)

# Check for optional dependency
try:
    from statsmodels.tsa.seasonal import STL
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False


@xr.register_dataset_accessor("climate_timeseries")
class TimeSeriesAccessor:
    """
    Accessor for analyzing and visualizing climate time series from xarray datasets.

    Provides methods for extracting, processing, and visualizing time series
    with support for weighted spatial averaging, seasonal filtering, and 
    robust time series decomposition.
    """

    def __init__(self, xarray_obj: xr.Dataset):
        """Initialize the accessor with a Dataset object."""
        self._obj = xarray_obj

    def _warn_if_not_chunked(self, variable: str) -> None:
        """
        Log a debug message if the data is not a Dask array.
        """
        if variable in self._obj and notVO hasattr(self._obj[variable].data, 'dask'):
            logger.debug(
                f"Variable '{variable}' is in-memory (numpy). For large datasets, "
                "consider using Dask chunks (e.g., ds.chunk({'time': 100}))."
            )

    def _get_spatial_series(
        self, 
        variable: str, 
        selection_kwargs: Dict[str, Any], 
        area_weighted: bool = True,
        operation: str = 'mean'
    ) -> Optional[xr.DataArray]:
        """
        Internal helper to Select -> Filter -> Spatially Reduce.

        This centralizes the logic for preparing a time series from 3D/4D data.

        Parameters
        ----------
        variable : str
            Variable name.
        selection_kwargs : dict
            Arguments passed to select_process_data (lat, lon, level, time, etc).
        area_weighted : bool
            Whether to apply cosine latitude weighting.
        operation : str
            'mean' for spatial average, 'std' for spatial variability.

        Returns
        -------
        xr.DataArray or None
            The reduced time series, or None if selection resulted in empty data.
        """
        # 1. Validation
        if not isinstance(variable, str):
            raise TypeError(f"Variable name must be a string, got {type(variable)}")
        if variable not in self._obj.data_vars:
            raise ValueError(f"Variable '{variable}' not found in dataset")
        
        self._warn_if_not_chunked(variable)
        get_or_create_dask_client()

        # 2. Select and Filter Data
        # We unpack the kwargs to match the signature of select_process_data
        try:
            data_selected = select_process_data(
                self._obj, 
                variable=variable, 
                **selection_kwargs
            )
        except ValueError as e:
            logger.error(f"Data selection failed: {e}")
            return None

        if data_selected.size == 0:
            logger.warning("Data selection resulted in an empty array.")
            return None

        # 3. Check Time Dimension
        time_name = get_coord_name(data_selected, ['time', 't'])
        if not time_name or time_name not in data_selected.dims:
             raise ValueError("A time dimension is required for time series analysis.")

        # 4. Perform Spatial Reduction
        if operation == 'mean':
            # Use the robust utility we defined in data_utils
            result = get_spatial_mean(data_selected, area_weighted=area_weighted)
            
        elif operation == 'std':
            # Calculate Spatial Standard Deviation (Variability across space at each time step)
            lat_name = get_coord_name(data_selected, ['lat', 'latitude', 'y', 'nav_lat'])
            lon_name = get_coord_name(data_selected, ['lon', 'longitude', 'x', 'nav_lon'])
            
            spatial_dims = [d for d in [lat_name, lon_name] if d and d in data_selected.dims]
            
            if not spatial_dims:
                logger.warning("No spatial dimensions found for spatial std dev. Returning raw data.")
                result = data_selected
            else:
                if area_weighted and lat_name in spatial_dims:
                    # Manually handle weighting for std dev since get_spatial_mean is for means
                    lat_coord = data_selected[lat_name]
                    weights = np.cos(np.deg2rad(lat_coord))
                    
                    logger.info("Calculating area-weighted spatial standard deviation.")
                    result = data_selected.weighted(weights).std(dim=spatial_dims, skipna=True)
                else:
                    logger.info("Calculating unweighted spatial standard deviation.")
                    result = data_selected.std(dim=spatial_dims, skipna=True)
        else:
            raise ValueError(f"Unknown operation: {operation}")

        return result

    # ==============================================================================
    # PUBLIC PLOTTING METHODS
    # ==============================================================================

    def plot_time_series(
        self, 
        variable: str = 'air', 
        latitude: Optional[Union[float, slice, List]] = None, 
        longitude: Optional[Union[float, slice, List]] = None, 
        level: Optional[Union[float, slice, List]] = None,
        time_range: Optional[slice] = None, 
        season: str = 'annual', 
        year: Optional[int] = None,
        area_weighted: bool = True, 
        figsize: Tuple[int, int] = (16, 10), 
        save_plot_path: Optional[str] = None, 
        title: Optional[str] = None
    ) -> Optional[plt.Axes]:
        """
        Plot a time series of a spatially averaged variable.

        Parameters
        ----------
        variable : str
            Name of the variable to plot.
        latitude, longitude, level : float, slice, or list
            Spatial selection parameters.
        time_range : slice
            Time range to select (e.g., slice('1990', '2000')).
        season : str
            Season filter ('annual', 'djf', 'jjas', etc.).
        year : int
            Specific year filter.
        area_weighted : bool
            If True, apply cosine latitude weighting to the mean.
        figsize : tuple
            Size of the figure.
        save_plot_path : str, optional
            Path to save the figure.
        title : str, optional
            Custom title.

        Returns
        -------
        matplotlib.axes.Axes or None
            The plot axes, or None if data was empty.
        """
        # Pack selection args for the helper
        selection_kwargs = {
            'latitude': latitude, 'longitude': longitude, 'level': level,
            'time_range': time_range, 'season': season, 'year': year
        }

        # Step 1: Get the processed time series
        ts_data = self._get_spatial_series(
            variable, selection_kwargs, area_weighted, operation='mean'
        )
        if ts_data is None: 
            return None

        # Step 2: Plot
        plt.figure(figsize=figsize)
        
        # Performance optimization: Use default line style (no markers) for dense time series
        # Markers ('.') on 10k+ points significantly slow down rendering.
        plot_kwargs = {'linewidth': 1.5, 'linestyle': '-'}
        
        if hasattr(ts_data, 'chunks') and ts_data.chunks:
            logger.info("Computing and plotting time series (Dask)...")
            with ProgressBar():
                ts_data.plot(**plot_kwargs)
        else:
            ts_data.plot(**plot_kwargs)
            
        ax = plt.gca()

        # Step 3: Decoration
        units = self._obj[variable].attrs.get("units", "")
        long_name = self._obj[variable].attrs.get("long_name", variable.replace('_', ' ').capitalize())
        ax.set_ylabel(f"{long_name} ({units})")
        ax.set_xlabel('Time')

        if title is None:
            season_display = season.upper() if season.lower() != 'annual' else 'Annual'
            weight_str = "Area-Weighted " if area_weighted else ""
            ax.set_title(f"{season_display}: {weight_str}Spatial Mean of {long_name}")
        else:
            ax.set_title(title)

        ax.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        if save_plot_path:
            plt.savefig(save_plot_path, bbox_inches='tight', dpi=300)
            logger.info(f"Plot saved to {save_plot_path}")
            
        return ax

    def plot_std_space(
        self, 
        variable: str = 'air', 
        latitude: Optional[Union[float, slice, List]] = None, 
        longitude: Optional[Union[float, slice, List]] = None, 
        level: Optional[Union[float, slice, List]] = None,
        time_range: Optional[slice] = None, 
        season: str = 'annual', 
        year: Optional[int] = None,
        area_weighted: bool = True, 
        figsize: Tuple[int, int] = (16, 10), 
        save_plot_path: Optional[str] = None, 
        title: Optional[str] = None
    ) -> Optional[plt.Axes]:
        """
        Plot a time series of the spatial standard deviation.

        This metric represents the **variability across space** at each time step.
        (e.g., how much temperature varies between the equator and pole today).

        Parameters
        ----------
        variable : str
            Name of the variable to plot.
        latitude, longitude, level : float, slice, or list
            Spatial selection parameters.
        time_range : slice
            Time range to select.
        season : str
            Season filter.
        year : int
            Specific year filter.
        area_weighted : bool
            If True, apply cosine latitude weighting to the std dev calculation.
        figsize : tuple
            Size of the figure.
        save_plot_path : str, optional
            Path to save the figure.
        title : str, optional
            Custom title.

        Returns
        -------
        matplotlib.axes.Axes or None
            The plot axes, or None if data was empty.
        """
        selection_kwargs = {
            'latitude': latitude, 'longitude': longitude, 'level': level,
            'time_range': time_range, 'season': season, 'year': year
        }

        ts_data = self._get_spatial_series(
            variable, selection_kwargs, area_weighted, operation='std'
        )
        if ts_data is None: 
            return None

        plt.figure(figsize=figsize)
        
        plot_kwargs = {'linewidth': 1.5, 'linestyle': '-'}
        
        if hasattr(ts_data, 'chunks') and ts_data.chunks:
            logger.info("Computing and plotting spatial std dev series (Dask)...")
            with ProgressBar():
                ts_data.plot(**plot_kwargs)
        else:
            ts_data.plot(**plot_kwargs)
            
        ax = plt.gca()
        
        units = self._obj[variable].attrs.get("units", "")
        long_name = self._obj[variable].attrs.get("long_name", variable.replace('_', ' ').capitalize())
        ax.set_ylabel(f"Spatial Std. Dev. ({units})")
        ax.set_xlabel('Time')
        
        if title is None:
            season_display = season.upper() if season.lower() != 'annual' else 'Annual'
            weight_str = "Weighted " if area_weighted else ""
            ax.set_title(f"{season_display}: {weight_str}Spatial Variability (Std Dev) of {long_name}")
        else:
            ax.set_title(title)

        ax.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        if save_plot_path:
            plt.savefig(save_plot_path, bbox_inches='tight', dpi=300)
            logger.info(f"Plot saved to {save_plot_path}")
            
        return ax

    def decompose_time_series(
        self, 
        variable: str = 'air', 
        level: Optional[Union[float, slice, List]] = None, 
        latitude: Optional[Union[float, slice, List]] = None, 
        longitude: Optional[Union[float, slice, List]] = None,
        time_range: Optional[slice] = None, 
        season: str = 'annual', 
        year: Optional[int] = None,
        stl_seasonal: int = 13, 
        stl_period: int = 12, 
        area_weighted: bool = True,
        plot_results: bool = True, 
        figsize: Tuple[int, int] = (16, 10), 
        save_plot_path: Optional[str] = None, 
        title: Optional[str] = None
    ) -> Union[Dict[str, pd.Series], Tuple[Dict[str, pd.Series], plt.Figure], None]:
        """
        Decompose a time series using STL (Seasonal-Trend decomposition using LOESS).

        This function handles missing data via linear interpolation to maintain 
        frequency alignment required by STL, which is critical for accurate decomposition.

        Parameters
        ----------
        variable : str
            Variable to decompose.
        stl_seasonal : int
            Length of the seasonal smoother. Must be an odd integer.
        stl_period : int
            Periodicity of the data (e.g., 12 for monthly, 365 for daily).
            Defaults to 12 (assuming monthly data).
        plot_results : bool
            If True, returns the figure along with the data.

        Returns
        -------
        dict or (dict, Figure)
            A dictionary with keys ['original', 'trend', 'seasonal', 'residual'],
            and optionally the matplotlib Figure object.
        """
        if not STATSMODELS_AVAILABLE:
            raise ImportError("The 'statsmodels' library is required for decomposition.")

        selection_kwargs = {
            'latitude': latitude, 'longitude': longitude, 'level': level,
            'time_range': time_range, 'season': season, 'year': year
        }

        # 1. Get Spatially Averaged Data
        ts_da = self._get_spatial_series(
            variable, selection_kwargs, area_weighted, operation='mean'
        )
        if ts_da is None: 
            return (None, None) if plot_results else None
        
        # 2. Compute to memory (STL requires numpy/pandas)
        # Check if Dask backed, if so compute
        if hasattr(ts_da, 'compute'):
            logger.info("Computing data into memory for STL decomposition...")
            with ProgressBar():
                ts_da = ts_da.compute()

        # 3. Check Dimensionality
        # STL works on 1D arrays. If we still have an 'ensemble' or 'member' dimension, fail.
        ts_da = ts_da.squeeze(drop=True)
        if ts_da.ndim > 1:
            raise ValueError(
                f"Data has {ts_da.ndim} dimensions after spatial averaging: {ts_da.dims}. "
                "STL requires a 1D time series. You must select a specific level or ensemble member."
            )

        # 4. Convert to Pandas and Handle Gaps
        try:
            ts_pd = ts_da.to_series()
        except Exception as e:
            raise ValueError(f"Failed to convert DataArray to Pandas Series: {e}")

        # CRITICAL SCIENTIFIC FIX:
        # STL requires regular spacing. Dropping NaNs destroys the time index structure.
        # We use linear interpolation to fill small gaps.
        if ts_pd.isnull().any():
            logger.warning(
                "Time series contains NaNs. Performing linear interpolation "
                "to maintain frequency alignment for STL."
            )
            ts_pd = ts_pd.interpolate(method='linear')
            
            # If NaNs remain (e.g., at the very start/end where interp fails), drop them.
            if ts_pd.isnull().any():
                ts_pd = ts_pd.dropna()

        if len(ts_pd) <= 2 * stl_period:
            warnings.warn(
                f"Time series too short for STL (Length {len(ts_pd)} <= 2 * Period {stl_period}). "
                "Decomposition aborted."
            )
            return (None, None) if plot_results else None

        # 5. Run STL
        if stl_seasonal % 2 == 0:
            stl_seasonal += 1
            logger.info(f"Adjusted stl_seasonal to {stl_seasonal} (must be odd).")

        try:
            res = STL(ts_pd, seasonal=stl_seasonal, period=stl_period, robust=True).fit()
        except Exception as e:
            logger.error(f"STL Decomposition failed: {e}")
            return (None, None) if plot_results else None

        results = {
            'original': res.observed,
            'trend': res.trend,
            'seasonal': res.seasonal,
            'residual': res.resid
        }

        # 6. Plotting
        if not plot_results:
            return results

        fig, axes = plt.subplots(4, 1, figsize=figsize, sharex=True)
        long_name = self._obj[variable].attrs.get("long_name", variable)
        units = self._obj[variable].attrs.get("units", "")

        components = ['original', 'trend', 'seasonal', 'residual']
        labels = ['Observed', 'Trend', 'Seasonal', 'Residual']
        
        for i, (comp, label) in enumerate(zip(components, labels)):
            ax = axes[i]
            series = results[comp]
            
            # Use scatter for residuals to better visualize noise patterns
            if comp == 'residual':
                ax.plot(series.index, series.values, marker='o', linestyle='None', 
                        markersize=2, alpha=0.5, color='black')
                ax.axhline(0, color='red', linestyle='--', alpha=0.5)
            else:
                ax.plot(series.index, series.values, linewidth=1.5)
            
            ax.set_ylabel(f"{label} ({units})")
            ax.grid(True, linestyle=':', alpha=0.6)

        axes[3].set_xlabel("Time")

        if title:
            axes[0].set_title(title)
        else:
            axes[0].set_title(f"STL Decomposition: {long_name}")

        plt.tight_layout()
        
        if save_plot_path:
            plt.savefig(save_plot_path, bbox_inches='tight', dpi=300)
            logger.info(f"Decomposition plot saved to {save_plot_path}")
            
        return results, fig

__all__ = ['TimeSeriesAccessor']
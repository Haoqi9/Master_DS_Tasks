"""
@author: Hao Qi
"""

###############################################################################################################################

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import scipy.stats as stats
from typing import Literal
import contextily

###############################################################################################################################

def describe_custom(df,
                    decimals=2,
                    sorted_nunique=True
                    ) -> pd.DataFrame:
    """
    Generate a custom summary statistics DataFrame for the input DataFrame.

    Parameters:
    ---
    - `df (pd.DataFrame)`: Input DataFrame for which summary statistics are calculated.
    - `decimals (int, optional)`: Number of decimal places to round the results to (default is 2).
    - `sorted_nunique (bool, optional)`: If True, sort the result DataFrame based on the 'nunique' column
      in descending order; if False, return the DataFrame without sorting (default is True).

    Returns:
    ---
    pd.DataFrame: A summary statistics DataFrame with counts, unique counts, minimum, 25th percentile,
    median (50th percentile), mean, standard deviation, coefficient of variation, 75th percentile, and maximum.
    """
    def q1_25(ser):
        return ser.quantile(0.25)

    def q2_50(ser):
        return ser.quantile(0.50)

    def q3_75(ser):
        return ser.quantile(0.75)
    
    def CV(ser):
        return ser.std()/ser.mean()

    df = df.agg(['count','nunique', 'mean', 'std', CV, q1_25, q2_50, q3_75, 'min', 'max']).round(decimals).T    
    if sorted_nunique is False:
        return df
    else:
        return df.sort_values('nunique', ascending=False)

###############################################################################################################################

def barh_plot(series,
              sort=True,
              extra_title=None,
              figsize=(7,6),
              xlim_expansion=1.15,
              palette='tab10',
              **kwargs
              ) -> plt.Axes:
    """
    Returns:
    ---
    - Create a horizontal bar plot for a categorical series.

    Parameters:
    ---
    - ``series (pandas.Series)``: The categorical data to be plotted.
    - ``sort (bool, optional)``: Whether to sort the bars by count. Default is True.
    - ``xlim_expansion (float, optional)``: Factor to expand the x-axis limit. Default is 1.15.
    - ``**kwargs``: Additional keyword arguments to pass to seaborn's countplot function.

    Notes:
    ---
    - The function creates a horizontal bar plot for the specified categorical series.
    - The bars can be sorted by count if 'sort' is True.
    - The function also annotates the bars with count and proportion information.
    - The x-axis limit is expanded by a factor of 'xlim_expansion'.

    Example:
    ---
    ```python
    # Sample data
    data = pd.Series(['A', 'B', 'A', 'C', 'B', 'A', 'C', 'C', 'B', 'A'])

    # Create a horizontal bar plot
    barh_plot(data, sort=True, xlim_expansion=1.1, palette='viridis')
    ```
    """
    plt.figure(figsize=figsize)
    
    sns.countplot(y=series,
                width=0.5,
                order=series.value_counts(sort=sort).index,
                palette=palette,
                **kwargs
                )
    
    counts_no_order = series.value_counts(sort=sort)
    props_no_order = series.value_counts(sort=sort, normalize=True)
        
    for i, (count, prop) in enumerate(zip(counts_no_order, props_no_order)):
        plt.annotate(f' ({count}, {prop:.0%})', (count, i), fontsize=8)

    suptitle_text = f"'{series.name}'"
    if extra_title:
        suptitle_text += f" | {extra_title}"
    
    plt.ylabel('')
    plt.suptitle(suptitle_text, fontsize='xx-large')
    plt.title(f"n = {series.count()}/{series.size} | n_unique = {series.nunique()} | sort = {sort}")
    # Set xlimit
    _, xlim_r = plt.xlim()
    plt.xlim(right=xlim_r*xlim_expansion)

###############################################################################################################################

def kdeplot_by_class(
    df: pd.DataFrame,
    x_num: str,
    y_cat: str,
    figsize=(8,6)
):
    """
    Plot kernel density estimation (KDE) plot grouped by a categorical variable.

    Parameters:
    ---
    - df (pd.DataFrame): The pandas DataFrame containing the data.
    - x_num (str): The name of the numerical column to be plotted on the x-axis.
    - y_cat (str): The name of the categorical column to be used for grouping.
    - figsize (tuple, optional): The size of the figure (width, height). Defaults to (8, 6).

    Returns:
    ---
    - fig (plt.Figure): The resulting matplotlib Figure object.
    """
    fig, ax = plt.subplots(figsize=figsize)

    sns.kdeplot(
        data=df,
        x=x_num,
        hue=y_cat,
        fill=True,
        palette='tab10',
        ax=ax
    )

    temp = df.groupby(y_cat, observed=False)[x_num].median()
    cats_indexes = temp.index
    cats_medians = temp.values

    y_axis = plt.ylim()[1] / 2
    position_decrease = 1
    for index, median in zip(cats_indexes, cats_medians):
        ax.axvline(median, ls='--', alpha=0.2, color='blue')
        plt.annotate(
            text=f"{index}: {median}",
            xy=(median, y_axis / position_decrease),
            fontsize=6,
            color='blue',
        )
        
        position_decrease += 0.8

    ax.set_ylabel('')
    ax.set_xlabel('')
    fig.suptitle(x_num, fontweight='bold')

    return fig

###############################################################################################################################

def class_balance_barhplot(x,
                           y,
                           text_size=9,
                           figsize=(8,6)
                           ):
    """
    Plot class balance bar horizontal plot.

    Parameters:
    -----------
    x : pandas.Series
        Input feature.
    y : pandas.Series
        Target variable.
    text_size : int, optional
        Font size for annotation text (default is 9).
    figsize : tuple, optional
        Figure size (width, height) in inches (default is (8, 6)).

    Returns:
    --------
    fig : matplotlib.figure.Figure
        Matplotlib figure object.
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    df_pct = pd.crosstab(x, y, normalize='index').sort_index(ascending=False)
    df_count = pd.crosstab(x, y).sort_index(ascending=False)
    
    # Binary or multiclass classification:
    n_y_classes = y.nunique()
    if n_y_classes > 2:
        df_pct.plot.barh(stacked=True, alpha=0.7, ax=ax)
        
        for i in range(0, len(df_pct.index)):
            pct_list = [str(np.round(pct, 2)) for pct in df_pct.iloc[i,:]]
            ax.annotate(
                text='p: ' + ' / '.join(pct_list),
                xy=(0.1, i + 0.1),
                alpha=0.8,
                color='blue'
            )
            
        for i in range(0, len(df_count.index)):
            pct_list = [str(np.round(pct, 2)) for pct in df_count.iloc[i,:]]
            ax.annotate(
                text='n: ' + ' / '.join(pct_list),
                xy=(0.1, i - 0.1),
                alpha=0.8,
                color='blue'
            )
        
    elif n_y_classes == 2:
        df_pct.plot.barh(stacked=True, color=['red', 'green'], alpha=0.7, ax=ax)

        for i, category in enumerate(df_pct.index):
            pct_0 = df_pct.iloc[:,0][category]
            pct_1 = df_pct.iloc[:,1][category]
            ax.annotate(text=f"{pct_0:.2f} | n={df_count.iloc[:,0][category]}",
                        xy=(0 + 0.01, i),
                        fontsize=text_size,
                        alpha=0.8,
                        color='blue'
                        )
            ax.annotate(text=f"{pct_1:.2f} | n={df_count.iloc[:,1][category]}",
                        xy=(0.92 - 0.1, i),
                        fontsize=text_size,
                        alpha=0.8,
                        color='blue'
                        )
            
    ax.legend(bbox_to_anchor=(1,1))
    ax.set_title(f"Class distribution of '{y.name}' for categories in '{x.name}'")
    fig.suptitle(x.name, fontsize=15, fontweight='bold')
    
    return fig

###############################################################################################################################

def geopoints_plot(longitude_ser,
                   latitude_ser,
                   plot_type: Literal['scatter', 'hexbin', 'density']='scatter',
                   color='red',
                   map_tile_source: Literal['positron', 'voyager', 'OpenStreetMap']='positron',
                   attribute_col=None,
                   figsize=(14,14),
                   cmap='viridis_r',
                   hb_gridsize=50,
                   marker_size=6,
                   alpha=0.2,
                   **kwargs
                   ):
    """
    Plot geospatial points (longitude and latitude coordinates) on a map.

    Parameters
    ---
    - `longitude_ser` (pandas.Series): Series of longitude values.
    - `latitude_ser` (pandas.Series): Series of latitude values.
    - `plot_type` (str, optional): Type of plot to be displayed. Options: 'scatter', 'hexbin', 'density'. Default is 'scatter'.
    - `map_tile_source` (str, optional): Source of map tiles to be used as the background. Options: 'positron', 'voyager', 'OpenStreetMap'. Default is 'positron'.
    - `attribute_col` (pandas.Series, optional): Series of attribute values to be represented by point color or size. Default is None.
    - `figsize` (tuple, optional): Figure size. Default is (14, 14).
    - `cmap` (str, optional): Colormap name for density and hexbin plot. Default is 'viridis_r' (inverse gradient).
    - `hb_gridsize` (int, optional): Grid size for hexbin plot. Default is 50.
    - `marker_size` (int, optional): Marker size for scatter plot. Default is 6.
    - `alpha` (float, optional): Opacity of the plotted points. Should be between 0 and 1. Default is 0.2.
    - `**kwargs`: Additional keyword arguments to be passed to the underlying plotting functions.
    """
    if map_tile_source == 'positron':
        map_source = contextily.providers.CartoDB.Positron
    elif map_tile_source =='voyager':
        map_source = contextily.providers.CartoDB.Voyager
    elif map_tile_source == 'OpenStreetMap':
        map_source = contextily.providers.OpenStreetMap.Mapnik
    else:
        raise Exception("map_tile_source must be one of the list: ['positron', 'voyager', 'OpenStreetMap']!")
        
    _, ax = plt.subplots(figsize=figsize)

    if plot_type == 'scatter':
        sns.scatterplot(x=longitude_ser,
                        y=latitude_ser,
                        s=marker_size,
                        color=color,
                        alpha=alpha,
                        ax=ax,
                        **kwargs)
    
    elif plot_type == 'hexbin':
        hb = ax.hexbin(x=longitude_ser,
                       y=latitude_ser,
                       gridsize=hb_gridsize,
                       lw=0,  # hexbin grid marker
                       alpha=alpha,
                       cmap=cmap,
                       **kwargs)
    
    elif plot_type == 'density':
        sns.kdeplot(x=longitude_ser,
                    y=latitude_ser,
                    n_levels=50,
                    fill=True,
                    alpha=alpha,
                    cmap=cmap,
                    weights=attribute_col,  # Intensidad de color basada en la variable 'price'
                    ax=ax,
                    **kwargs)

    contextily.add_basemap(
        ax=ax,
        zoom='auto',
        crs='EPSG:4326',
        source=map_source
    )
    
    title_text = 'Count distribution'
    if attribute_col is not None:
        title_text = f"Spatial density distribution by '{attribute_col.name}' attribute"
    ax.set_title(title_text)
    plt.show()

###############################################################################################################################

def manage_outliers(series: pd.Series,
                       mode: Literal['check', 'return', 'winsor', 'miss']='check',
                       non_normal_crit: Literal['MAD', 'IQR']='MAD',
                       n_std=4,
                       multiplier=4,
                       MAD_threshold=8,
                       normal_cols: list=[],
                       alpha=0.05,
                       n_ljust=30
                       ) -> pd.Series:
   """
    Detect and manage outliers in a given numeric series.
    Often use the following way: ``df.apply(manage_outliers, mode='check')``

    Parameters
    ---
    - ``series (pd.Series)``: Input data series containing numeric values.
    - ``mode (str)``: Specifies the operation mode. Possible values: 'check' (default), 'return', 'winsor', 'miss'.
    Only essential for ``'return'`` mode!
    - ``n_std (float)``: Number of standard deviation away from the mean (normal distributions). Default is 4.
    - ``alpha (float)``: Significance level for normality tests (default=0.05).
    - ``multiplier (float)``: Multiplier for IQR-based outlier detection (default=4).
    - ``MAD_threshold (float)``: Threshold for Median Absolute Deviation (MAD)-based outlier detection (default=8).
    - ``normal_cols (list)``: List of cols assummed to be normal (default=[]).
    - ``n_ljust (int)``: Text alignment that displays determination method. (Default=30).
    
    Notes
    ---
    - For ``'check' mode``: pd.Series with lower, upper, and combined percentage of outliers (subset).
    - For ``'return' mode``: printed messages with a series of outlier values for each series/variable.
    Follow by using the ``function add_outliers_col()`` to get a new 'outlier col with list as values'.
    - For ``'winsor' mode``: Winsorized series based on lower and upper limits (df).
    - For ``'miss' mode``: Series with outliers replaced by NaN and information about missing values (series inplace change!).
   """
   # Check if mode is correct
   modes = ['check', 'winsor', 'return', 'miss']
   if mode not in modes:
       return f"Choose: {modes}"
   
   # Condición de asimetría y aplicación de criterio 1 según el caso
   if series.name == 'outlier_list':
       return series
   
   # Calcular primer cuartil     
   q1 = series.quantile(0.25)  
   # Calcular tercer cuartil  
   q3 = series.quantile(0.75)
   # Calculo de IQR
   IQR=q3-q1
   
   if series.name in normal_cols:
       message = f"'\033[1m{series.name}\033[0m':".ljust(n_ljust) + f"    normal (manual  | +-{n_std} std)"
       criterio1 = abs((series-series.mean())/series.std())>n_std
   else:
       n = series.shape[0] - series.isna().sum()
       if n < 50:
           method = 'shapiro'
           _, p_value = stats.shapiro(series)
       else:
           method = 'Kolmogo'
           _, p_value = stats.kstest(series, 'norm')
        
       if p_value >= alpha:
            message = f"'\033[1m{series.name}\033[0m':".ljust(n_ljust) + f"    normal ({method} | +-{n_std} std)"
            criterio1 = abs((series-series.mean())/series.std())>n_std
       else:
            if non_normal_crit == 'MAD':
                message = f"'\033[1m{series.name}\033[0m':".ljust(n_ljust) + f"non-normal ({method} | +-{MAD_threshold} MAD)"
                criterio1 = abs((series-series.median())/stats.median_abs_deviation(series.dropna()))>MAD_threshold
            elif non_normal_crit == 'IQR':
                message = f"'\033[1m{series.name}\033[0m':".ljust(n_ljust) + f"non-normal ({method} | +-{multiplier} IQR)"
                criterio1 = (series<(q1 - multiplier*IQR))|(series>(q3 + multiplier*IQR))
   
   lower = series[criterio1&(series<q1)].count()/series.dropna().count()
   upper = series[criterio1&(series>q3)].count()/series.dropna().count()
   
   # Salida según el tipo deseado
   if mode == 'check':
       print(message)
       ser = pd.Series({
           'lower (%)': np.round(lower*100, 2),
           'upper (%)': np.round(upper*100, 2),
           'All (%)': np.round((lower+upper)*100, 2)})
       return ser
   
   elif mode == 'return':
       print(f"\n---------------- \033[1m{series.name}\033[0m ----------------")
       print(series[criterio1].value_counts().sort_index())
       return None
   
   elif mode == 'winsor':
       winsored_series = series.clip(lower=series.quantile(lower, interpolation='lower'),
                                  upper=series.quantile(1 - upper, interpolation='higher'))
       return winsored_series
   
   elif mode == 'miss':
       missing_bef = series.isna().sum()
       series.loc[criterio1] = np.nan
       missing_aft = series.isna().sum()
      
   if missing_bef != missing_aft:
        print(series.name)
        print('Missing_bef: ' + str(missing_bef))
        print('Missing_aft: ' + str(missing_aft) +'\n')
        return (series)

###############################################################################################################################

def get_cramersV(x,
                 y,
                 n_bins=5,
                 return_scalar=False
                 ):
    """
    - Calculate Cramer's V statistic for the association between two categorical variables.
    - If either x or y is a continuous variable, the function discretizes it using fixed binning (default is 5 bins).

    Parameters:
    ---
    - `x (pd.Series)`: Predictor variable.
    - `y (pd.Series)`: Response variable.
    
    Notes:
    ---
    - Optimal binning is performed using the get_optbinned_x function if opt_binning is True.
    - The function then computes the Cramer's V statistic for the association between the two categorical variables using the contingency table.
    - The result is returned as a Pandas Series with the Cramer's V statistic and the variable name as the index.
    """
    # Discretizar x continua
    if pd.api.types.is_numeric_dtype(x) and (not (x.nunique() == 2)):
        x= pd.cut(x, bins=min(n_bins, x.nunique()))
            
    # Discretizar y continua
    if pd.api.types.is_numeric_dtype(y) and (not (y.nunique() == 2)):
        y = pd.cut(y, bins=min(n_bins, y.nunique()))
    
    name = f'CramersV: min(nunique, {n_bins}) bins'
        
    data = pd.crosstab(x, y).values
    vCramer = stats.contingency.association(data, method='cramer')
    
    if return_scalar is True:
        return vCramer
    else:
        return pd.Series({name:vCramer}, name=x.name)

###############################################################################################################################

def association_barplot(df_widefmt: pd.DataFrame,
                        y: pd.Series=None,
                        abs_value=False,
                        extra_title=None,
                        xlim_expansion=1.15,
                        text_size=8,
                        text_right_size=0.0003,
                        palette='coolwarm',
                        figsize=(6,5),
                        title_size=14,
                        no_decimals=False,
                        ascending=False,
                        sort=True,
                        **kwargs
                        ) -> plt.Axes:
    """
    - Generate a barplot to visualize the association of predictors with a target variable.
    - Equivalent for Pearson corr df: 
    - `df_pearson = pd.DataFrame(X.select_dtypes(np.number).apply(lambda x: np.corrcoef(x, y)[0,1])).T`

    Parameters
    ---
    - `df_widefmt (pd.DataFrame)`: Wide-format DataFrame containing predictor variables.
    - `y (pd.Series)`: Target variable.
    - `palette (str or list of str, optional)`: Color palette for the barplot. Default is 'Reds'.
    - `extra_title (str, optional)`: Additional title text to be appended to the plot title. Default is None.
    - `figsize (tuple, optional)`: Figure size in inches. Default is (7, 6).
    - `xlim_expansion (float, optional)`: Expansion factor for the x-axis limit. Default is 1.15.
    - `text_size (int, optional)`: Font size for annotation text. Default is 8.
    - `text_right_size (float, optional)`: Adjustment for the horizontal position of annotation text. Default is 0.001.
    - `**kwargs`: Additional keyword arguments to be passed to seaborn.barplot.

    Notes
    ---
    - The function sorts the predictor variables based on their association with the target variable in descending order.
    - The barplot is annotated with the corresponding association metric values.
    - The title of the plot includes the number of predictors and the name of the target variable.
    - If extra_title is provided, it is appended to the plot title.
    - The x-axis limit is adjusted based on xlim_expansion.
    - The resulting plot is displayed using matplotlib.pyplot.show().
    """
    metric_col = df_widefmt.T.columns[0]
    
    if sort is True:
        df_longfmt = df_widefmt.T.sort_values(metric_col, ascending=ascending)
    else:
        df_longfmt = df_widefmt.T
    
    hue = None
    if abs_value is True:
        df_longfmt['Sign'] = df_longfmt[metric_col].apply(lambda row: 'Negative' if row < 0 else 'Positive')
        df_longfmt[metric_col] = abs(df_longfmt[metric_col])
        df_longfmt.sort_values(metric_col, ascending=False, inplace=True)
        hue = df_longfmt['Sign']
        
    plt.figure(figsize=figsize)
    
    sns.barplot(x=df_longfmt[metric_col], y=df_longfmt.index,
                hue=hue, hue_order=['Negative', 'Positive'],
                palette=palette, **kwargs)
    
    if no_decimals is True:
        for i, col in enumerate(df_longfmt.index):
            plt.annotate(text=f'{df_longfmt[metric_col][col]}',
                    xy=(df_longfmt[metric_col][col] + text_right_size, i),
                    fontsize=text_size)
    else:
        for i, col in enumerate(df_longfmt.index):
            plt.annotate(text=f'{df_longfmt[metric_col][col]:.3f}',
                        xy=(df_longfmt[metric_col][col] + text_right_size, i),
                        fontsize=text_size)
    
    if y is not None:
        title_text = f"{len(df_longfmt.index)} Predictors association wrt '{y.name}'"
    else:
        title_text = f"{len(df_longfmt.index)} Predictors"
        
    if extra_title:
        title_text += f" | {extra_title}"
    
    plt.ylabel('Predictors')
    plt.title(title_text, fontsize=title_size)
    _, xlim_r = plt.xlim()
    plt.xlim(right=xlim_r*xlim_expansion)
    plt.tight_layout()
    if abs_value is True:
        plt.legend(loc='lower right', fontsize=9)
    plt.show()

###############################################################################################################################

def feature_importance_plot(tree_predictor,
                            n_rows:int=None,
                            return_df=False,
                            bottom=False,
                            figsize=(8,6),
                            palette='tab10'
                            ) -> plt.Axes | pd.DataFrame:
    """
    Returns:
    --
    - Plot feature importance based on a tree-based predictor.

    Parameters:
    --
    - ``tree_predictor (object)``: A tree-based predictor (e.g., DecisionTreeClassifier, RandomForestRegressor).
    - ``bottom (bool, optional)``: If True, plot the bottom features; if False, plot the top features. Default is False.
    - ``n_rows (int, optional)``: Number of features to include in the plot. If None, all features are included. Default is None.
    - ``figsize (tuple, optional)``: Figure size. Default is (8, 6).
    - ``palette (str or list, optional)``: Color palette for the barplot. Default is 'viridis'.
    - ``return_df (bool, optional)``: Returns the df with feature importance measure (%) and feature names (index). Default is False.
    A subset df of the top or bottom features is possible.

    """
    # Bottom or top features
    if bottom is False:
        sort_type = 'Top'
    else:
        sort_type = 'Bottom'
    
    df_feature = pd.DataFrame({'feature_importance': tree_predictor.feature_importances_ * 100},
                              index=tree_predictor.feature_names_in_)
    
    # number of rows/features
    if n_rows:
        n = n_rows
    else: 
        n = df_feature.shape[0]
        
    sub_feature = df_feature.sort_values('feature_importance', ascending=bottom)[:n]
    
    if return_df:
        return sub_feature
    
    plt.figure(figsize=figsize)
    sns.barplot(y=sub_feature.index, x=sub_feature['feature_importance'], palette=palette, hue=sub_feature.index, legend=False)

    for idx, measure in enumerate(sub_feature['feature_importance']):
        plt.annotate(xy=(measure, idx), text=f'{measure:.2f}', fontsize='x-small')

    _, x_right = plt.xlim()
    plt.xlim(right=x_right + 1)
    plt.title(f'Feature importance ({sort_type} {n} out of {df_feature.shape[0]}) | {tree_predictor.__class__.__name__}', fontsize='large')
    
    try:
        criterion = tree_predictor.criterion
    except:
        criterion = 'UNKOWN'
    
    plt.ylabel('Features')
    plt.xlabel(f'Total amount {criterion} decreased by splits in % (averaged over all trees if RF)', fontsize='small')
    plt.show()

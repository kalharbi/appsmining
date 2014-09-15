import pandas as pd
import numpy as np


# How many apps have used a column in any release?
def find_usage_in_any_release(dataframe, column_feature, show_no_matches=False):
    """Returns a dataframe that contains the package,number of packages, and last version number of the supported feature.
       Keyword arguments:
       dataframe -- the original dataframe indexed using a hierarchical indexing of package and version_code)
       column_feature -- the column name of a specific feature and must have boolean type values
       show_no_matches -- Include results even if the app does not support this feature.
       """
    # Get the first index name (package name)
    first_index = dataframe.index.names[0]
    result_column_name = column_feature + '_last_supported_version'
    df_result = pd.DataFrame(columns=[first_index, 'available_versions', result_column_name])
    df_result.set_index(first_index, inplace =True)
    # Get a list of unique packages
    packages = dataframe.index.get_level_values(first_index).unique()
    for package in packages:
        package_data_frame = dataframe.loc[package]
        # Get a list of supported versions for this package
        versions_list = package_data_frame[package_data_frame[column_feature]==True].index.tolist()
        # Exclude no matches
        if not versions_list and not show_no_matches:
            continue
        # Include no matches; use True or False 
        found = False
        max_supported_version= np.NaN
        if versions_list: 
            found = True
            max_supported_version = max(versions_list)
        # get the total number of available versions regardless of using this feature
        versions_count = len(package_data_frame.index)
        # Add the most total versions and the most recent supported version to the result dataframe
        df_result.ix[package, 'available_versions'] = versions_count
        if show_no_matches:
            df_result.ix[package, 'support_this_feature'] = found
        df_result.ix[package, result_column_name] = max_supported_version
    return df_result

    
def get_diff(dataframe, count_column_name, result_column_name):
    print('|==================================================================|')
    print('| The difference in ' + count_column_name + ' between multiple versions.|')
    print('|==================================================================|')
    # Get the first index name (package name)
    first_index = dataframe.index.names[0]
    df_result = pd.DataFrame(columns=[first_index, 'number_of_versions', result_column_name])
    df_result.set_index(first_index, inplace =True)
    for gp in dataframe.index.get_level_values(first_index).unique():
        tmp_df = dataframe.loc[gp, count_column_name]
        d = 0
        if len(tmp_df) == 1:
            d = 0
        else:
            for r in tmp_df:
                d = r - d
        df_result.ix[gp, result_column_name] = d
        df_result.ix[gp, 'number_of_versions'] = len(tmp_df)
    return df_result

# coding: utf-8

# In[54]:

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
get_ipython().magic('matplotlib inline')
from IPython.display import HTML
import matplotlib as mpl


# In[55]:

def get_diff(dataframe, count_column_name, result_column_name):
    #print('|==================================================================|')
    #print('| The difference in ' + count_column_name + ' between multiple versions.|')
    #print('|==================================================================|')
    # Get the first index name (package name)
    first_index = dataframe.index.names[0]
    df_result = pd.DataFrame(columns=[first_index, 'number_of_versions', result_column_name])
    df_result.set_index(first_index, inplace =True)
    for gp in dataframe.index.get_level_values(first_index).unique():
        tmp_df = dataframe.loc[gp][count_column_name]
        d = 0
        print(tmp_df)
        if len(tmp_df) == 1:
            d = 0
        else:
            for r in tmp_df:
                d = r - d
        df_result.ix[gp, result_column_name] = d
        df_result.ix[gp, 'number_of_versions'] = len(tmp_df)
    return df_result


# In[56]:

def find_usage_in_any_release(dataframe, column_feature, show_no_matches=False):
    """Returns a dataframe that contains the package,number of packages, and first version number of the supported feature.
       Keyword arguments:
       dataframe -- the original dataframe indexed using a hierarchical indexing of package and version_code)
       column_feature -- the column name of a specific feature and must have boolean type values
       show_no_matches -- Include results even if the app does not support this feature.
       """
    # Get the first index name (package name)
    first_index = dataframe.index.names[0]
    result_column_name = column_feature + '_first_supported_version'
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
            max_supported_version = min(versions_list)
        # get the total number of available versions regardless of using this feature
        versions_count = len(package_data_frame.index)
        # only consider multiple versions
        if(versions_count == 1):
            continue
        # Add the most total versions and the most recent supported version to the result dataframe
        df_result.ix[package, 'available_versions'] = versions_count
        if show_no_matches:
            df_result.ix[package, 'support_this_feature'] = found
        df_result.ix[package, result_column_name] = max_supported_version
    return df_result


# In[57]:

def find_usage_in_any_release_n(dataframe, column_feature, show_no_matches=False, opposite=False):
    """Returns a dataframe that contains the package,number of packages, and first version number of the supported feature.
       Keyword arguments:
       dataframe -- the original dataframe indexed using a hierarchical indexing of package and version_code)
       column_feature -- the column name of a specific feature and must have boolean type values
       show_no_matches -- Include results even if the app does not support this feature.
       """
    # Get the first index name (package name)
    first_index = dataframe.index.names[0]
    result_column_name = column_feature + '_first_supported_version'
    df_result = pd.DataFrame(columns=[first_index, 'available_versions', result_column_name])
    df_result.set_index(first_index, inplace =True)
    # Get a list of unique packages
    packages = dataframe.index.get_level_values(first_index).unique()
    for package in packages:
        package_data_frame = dataframe.loc[package]
        # Get a list of supported versions for this package
        versions_list = package_data_frame[package_data_frame[column_feature]>0].index.tolist()
        if opposite:
            versions_list = package_data_frame[package_data_frame[column_feature]==0].index.tolist()
        # Exclude no matches
        if not versions_list and not show_no_matches:
            continue
        # Include no matches; use True or False
        found = False
        max_supported_version= np.NaN
        if versions_list:
            found = True
            max_supported_version = min(versions_list)
        # get the total number of available versions regardless of using this feature
        versions_count = len(package_data_frame.index)
        # only consider multiple versions
        if(versions_count == 1):
            continue
        # Add the most total versions and the most recent supported version to the result dataframe
        df_result.ix[package, 'available_versions'] = versions_count
        if show_no_matches:
            df_result.ix[package, 'support_this_feature'] = found
        df_result.ix[package, result_column_name] = max_supported_version
    return df_result


# In[43]:

# How many apps have still used this feature in the latest release.
def find_use_in_latest_release(dataframe, column_feature):
    """Returns a dataframe that contains the package,number of packages, and last version number of the supported feature.
       Keyword arguments:
       dataframe -- the original dataframe indexed using a hierarchical indexing of package and version_code)
       column_feature -- the column name of a specific feature and must have boolean type values
       """
    # Get the first index name (package name)
    first_index = dataframe.index.names[0]
    result_column_name = column_feature + '_use_in_latest_version'
    df_result = pd.DataFrame(columns=[first_index, 'available_versions', result_column_name])
    df_result.set_index(first_index, inplace =True)
    # Get a list of unique packages
    packages = dataframe.index.get_level_values(first_index).unique()
    for package in packages:
        package_data_frame = dataframe.loc[package]
        # Get a list of supported versions for this package
        supported_versions_list = package_data_frame[package_data_frame[column_feature]==True].index.tolist()
        unsupported_versions_list = package_data_frame[package_data_frame[column_feature]==False].index.tolist()
        # Exclude no matches
        if supported_versions_list is None or unsupported_versions_list is None:
            continue
        if len(supported_versions_list) == 0:
            continue
        # compare the two version lists
        try:
            max_supported_ver = max(supported_versions_list)
            max_unsupported_ver = max(unsupported_versions_list)
        except ValueError:
            pass
        # if the latest version still supports the feature and has no unsupported versions
        if(len(supported_versions_list) > 0 and len(unsupported_versions_list) == 0):
            max_supported_ver = max(supported_versions_list)
            max_unsupported_ver = -1000000
       
        # Include no matches; use True or False
        found = False
        # Return the first adopted version
        earlier_adopted_version= np.NaN
        if max_supported_ver > max_unsupported_ver:
            found = True
            earlier_adopted_version = max_supported_ver
        # get the total number of available versions regardless of adopting this feature
        versions_count = len(package_data_frame.index)
               # Do not compare single versions
        if versions_count == 1:
            continue
        # Add the total versions and the first supported version to the result dataframe
        df_result.ix[package, 'available_versions'] = versions_count
        df_result.ix[package, 'support_this_feature'] = found
        df_result.ix[package, result_column_name] = earlier_adopted_version
    return df_result


# In[44]:

# How many apps have still used this feature in the latest release.
def find_use_in_latest_release_n(dataframe, column_feature, opposite=False):
    """Returns a dataframe that contains the package,number of packages, and last version number of the supported feature.
       Keyword arguments:
       dataframe -- the original dataframe indexed using a hierarchical indexing of package and version_code)
       column_feature -- the column name of a specific feature and must have boolean type values
       """
    # Get the first index name (package name)
    first_index = dataframe.index.names[0]
    result_column_name = column_feature + '_use_in_latest_version'
    df_result = pd.DataFrame(columns=[first_index, 'available_versions', result_column_name])
    df_result.set_index(first_index, inplace =True)
    # Get a list of unique packages
    packages = dataframe.index.get_level_values(first_index).unique()
    for package in packages:
        package_data_frame = dataframe.loc[package]
        # Get a list of supported versions for this package
        supported_versions_list = package_data_frame[package_data_frame[column_feature]>0].index.tolist()
        unsupported_versions_list = package_data_frame[package_data_frame[column_feature]==0].index.tolist()
        if opposite:
            supported_versions_list = package_data_frame[package_data_frame[column_feature]==0].index.tolist()
            unsupported_versions_list = package_data_frame[package_data_frame[column_feature]>0].index.tolist()
        # Exclude no matches
        if supported_versions_list is None or unsupported_versions_list is None:
            continue
        if len(supported_versions_list) == 0:
            continue
        # compare the two version lists
        try:
            max_supported_ver = max(supported_versions_list)
            max_unsupported_ver = max(unsupported_versions_list)
        except ValueError:
            pass
        # if the latest version still supports the feature and has no unsupported versions
        if(len(supported_versions_list) > 0 and len(unsupported_versions_list) == 0):
            max_supported_ver = max(supported_versions_list)
            max_unsupported_ver = -1000000
       
        # Include no matches; use True or False
        found = False
        # Return the first adopted version
        earlier_adopted_version= np.NaN
        if max_supported_ver > max_unsupported_ver:
            found = True
            earlier_adopted_version = max_supported_ver
        # get the total number of available versions regardless of adopting this feature
        versions_count = len(package_data_frame.index)
               # Do not compare single versions
        if versions_count == 1:
            continue
        # Add the total versions and the first supported version to the result dataframe
        df_result.ix[package, 'available_versions'] = versions_count
        df_result.ix[package, 'support_this_feature'] = found
        df_result.ix[package, result_column_name] = earlier_adopted_version
    return df_result


# In[45]:

h = HTML("<h1>Permissions</h1>"); h


# In[9]:

df_details = pd.read_csv('/Users/Khalid/git/appsmining/results/chi-15/listing/additional_info.csv')
df_details.sort(columns=['package','version_code'], inplace=True)
df_details.set_index(['package','version_code'], inplace=True)
df_details.head()


# In[10]:

df_per_changes = get_diff(df_details, 'total_permissions','changes_to_permissions')
df_per_changes


# In[11]:

df_per_changes.head()


# In[12]:

plt.title('Changes to the number of permissions')
plt.xlabel('Changes in permissions')
plt.ylabel('Number of apps')
df_per_changes.changes_to_permissions.hist(bins=20)


# In[30]:

s = df_per_changes['changes_to_permissions']
s = s.reset_index(drop=True)
s.min()


# In[13]:

h = HTML("<h1>App Widgets</h1>"); h


# In[31]:

df_appswidgets = pd.read_csv('/Users/Khalid/git/appsmining/results/chi-15/ui/appswidgets.txt')
df_appswidgets.sort(columns=['package','version_code'], inplace=True)
df_appswidgets.set_index(['package','version_code'], inplace=True)
df_appswidgets.head()


# In[46]:

# How many apps ever used it?
h = HTML("<h2>How many apps ever used App widgets in their UI in any release?</h2>"); h


# In[47]:

df_appswidgets_use = find_usage_in_any_release_n(df_appswidgets, 'widgets_count', True)
df_appswidgets_use.head()


# In[48]:

arr = np.array(df_appswidgets_use['support_this_feature'], dtype= bool) + 0
tmp = df_appswidgets_use
try:
    tmp.insert(0, 'binary_value', arr)
except ValueError:
    pass
tmp.groupby('support_this_feature').count().plot(kind='pie', y='binary_value',
                      autopct='%1.1f%%', title='App widgets Usage',
                      figsize=(4,4), colors=['r', 'g'], fontsize=20)
print('Number of apps that used App widgets: ' + 
      str(len(tmp.loc[tmp.support_this_feature == True])) +
      ' out of ' + str(len(tmp)) + ' apps.')


# In[50]:

h = HTML("<h2>How many apps that no longer use any App Widgets in their recent release?</h2>"); h


# In[51]:

df_appswidgets_still_using = find_use_in_latest_release(df_appswidgets, 'widgets_count')
df_appswidgets_still_using.head()


# In[53]:

arr = np.array(df_appswidgets_still_using['support_this_feature'], dtype= bool) + 0
tmp = df_appswidgets_still_using
try:
    tmp.insert(0, 'binary_value', arr)
except ValueError:
    pass
tmp.groupby('support_this_feature').count().plot(kind='pie', y='binary_value',
                      autopct='%1.1f%%', title='App widgets Use in Latest release',
                      figsize=(4,4), colors=['r', 'g'], fontsize=20)
print('Number of apps that no longer use Up App widgets button: ' + 
      str(len(tmp.loc[tmp.support_this_feature == False])) +
      ' out of ' + str(len(tmp)) + ' apps.')


# In[58]:

df_appswidgets_changes = get_diff(df_appswidgets, 'widgets_count','changes_to_widgets')
df_appswidgets_changes.head()


# In[60]:

df_appswidgets_changes.changes_to_widgets.hist(bins=50)


# In[61]:

df_appswidgets_changes.changes_to_widgets.head()


# In[63]:

df_appswidgets_changes[df_appswidgets_changes.changes_to_widgets > 10]


# In[ ]:




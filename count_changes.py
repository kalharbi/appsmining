#!/usr/bin/python
import pandas as pd
import numpy as np
import matplotlib as mpl
import sys
import os
import datetime
import logging
from optparse import OptionParser

log = logging.getLogger("count_changes")
# The logger's level must be set to the "lowest" level.
log.setLevel(logging.DEBUG)

# Return a list of unique items in a series
def to_items_list(items_str, separator):
    if type(items_str) is float and np.isnan(items_str):
        return ''
    stripped = (x.strip() for x in items_str.split(separator))
    return [x for x in stripped if x]

def get_all_items(series, separator):
    item_sets = (set(to_items_list(x, separator)) for x in series)
    return sorted(set.union(*item_sets))
    
def count_permission_changes(dataframe, list_column_name):
    ''' Returns a new Data frame that contains columns for the added or dropped values 
    in the given list_column_name.
    '''
    print('|==================================================================|')
    print('| Counting the changes in ' + list_column_name + ' ')
    print('|==================================================================|')
    dataframe.set_index(keys=['package'], inplace=True)
    # Get all unique added or dropped values
    all_values = get_all_items(dataframe[list_column_name], '|')
    #count_column = list_column_name + "_count"
    #all_values.append(count_column)
    # Create a dummy dataframe that holds all
    values_index = pd.Index(np.unique(all_values))
    result_frame = pd.DataFrame(np.zeros((len(dataframe), len(values_index))),
                               index= dataframe.index, columns=all_values)
    # Iterate over the dataframe and store values in the dummy dataframe
    for package in dataframe.index.get_values():
        log.info('In package: ' + package)
        vals_list = dataframe.loc[package, list_column_name]
        if type(vals_list) is float and np.isnan(vals_list):
            continue
        else:
            vals_list = vals_list.split('|')
            #result_frame.loc[package, count_column] = len(vals_list)
            for val in vals_list:
                result_frame.loc[package, val] = 1
    return result_frame
    
def check_permission_first_use(dataframe, column_name, perm_name):
    ''' Returns a new Data frame that contains two columns; the first column is 
    version_before_first_use, which contains the version before the app used
    the given permission perm_name and the second column is version_first_use, 
    which contains the version when the app used the given permission, perm_name for the first time.
    
    Keyword arguments:
    dataframe -- the original data frame that contains the permissions and
    is indexed by package and version_code columns.
    column_name -- the column name that includes the permissions.
    per_name -- the permission that the app later used.
    '''
    print("Checking apps that used %s for the first use ..." %(perm_name))
    # Create the result datafram
    result_frame = pd.DataFrame(columns=['package',
                                           'version_before_first_use',
                                           'version_first_use'])
    result_frame.set_index(keys=['package'], inplace=True)
    dataframe.set_index(keys=['package','version_code'], inplace=True)
    first_index = dataframe.index.names[0]
    second_index = dataframe.index.names[1]
    # Iterate over the dataframe and store values in the dummy dataframe
    for package in dataframe.index.get_level_values(first_index).unique():
        versions = dataframe.xs(package, level=first_index).index.get_level_values(second_index)
        version_first_use = np.nan
        version_first_use_index = np.nan
        version_before_first_use = np.nan
        permissions_list_before = np.nan
        permissions_list_first_use = np.nan
        diff_permissions_added = np.nan
        diff_permissions_removed = np.nan
        # get first use
        for idx, version in enumerate(versions):
            permissions = dataframe.loc[package, version].permissions
            if type(permissions) is float and np.isnan(permissions):
                continue
            permissions = permissions.split(',')
            if perm_name in permissions and len(permissions) > 1:
                version_first_use = version
                version_first_use_index = idx
                permissions_list_first_use = permissions
                break
        # get before first use
        if type(version_first_use) is float and np.isnan(version_first_use):
            continue
        elif version_first_use_index > 0:
            version_before_first_use = versions[version_first_use_index - 1]
            if version_before_first_use > version_first_use:
                continue
            permissions_list_before = dataframe.loc[package, version_before_first_use].permissions
            if type(permissions_list_before) is float and np.isnan(permissions_list_before):
                continue
            else:
                permissions_list_before = permissions_list_before.split(',')
                if perm_name in permissions_list_before:
                    continue
            diff_permissions_added = list(set(permissions_list_first_use) - set(permissions_list_before))
            diff_permissions_removed = list(set(permissions_list_before) - set(permissions_list_first_use))
            
        if not np.isnan(version_first_use) and not np.isnan(version_before_first_use):
            result_frame.ix[package, 'version_before_first_use'] = version_before_first_use
            result_frame.ix[package, 'version_first_use'] = version_first_use
            result_frame.ix[package, 'permissions_list_before_first_use'] = ",".join(permissions_list_before)
            result_frame.ix[package, 'permissions_list_in_first_use'] = ",".join(permissions_list_first_use)
            result_frame.ix[package, 'diff_permissions_added'] = ",".join(diff_permissions_added)
            result_frame.ix[package, 'diff_permissions_removed'] = ",".join(diff_permissions_removed)
    return result_frame
    
def run_command(command, in_file, column_name, out_file, args):
    df_details = pd.read_csv(in_file)
    if command == 'count_permission_changes':
        df_changes = count_permission_changes(df_details, column_name)
        df_changes.to_csv(out_file)
    elif command == 'check_permission_first_use':
        df_result = check_permission_first_use(df_details, column_name, args[0])
        df_result.to_csv(out_file)

def main(args):
    # Time the execution
    start_time = datetime.datetime.now()
    # Configure logging
    logging_file = None
    logging_level = logging.ERROR
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # Create console logger and set its formatter and level
    logging_console = logging.StreamHandler(sys.stdout)
    logging_console.setFormatter(formatter)
    logging_console.setLevel(logging.DEBUG)
    # Add the console logger
    log.addHandler(logging_console)
    usage_info = ''' python %prog <COMMAND> <in_csv_file> <column_name> <out_csv_file> [<permission_name>] [options]
                     The following commands are available:
                     count_permission_changes
                     check_permission_first_use
                     
                     [<permission_name>]: permission name is required for the following commands: 
                                          check_permission_first_use
                     '''
    description_paragraph = ("DESCRIPTION: Count the changes to an app's feature over multiple versions")
    # command line parser
    parser = OptionParser(
                          usage=usage_info, description = description_paragraph,
                          version="%prog 1.0")
    parser.add_option("-l", "--log", dest="log_file", help="write logs to FILE.", metavar="FILE")
    parser.add_option('-v', '--verbose', dest="verbose", default=0,
                      action='count', help='increase verbosity.')
    (options, args) = parser.parse_args()
    if len(args) < 4:
        parser.error("incorrect number of arguments.")
    if options.log_file:
        logging_file = logging.FileHandler(options.log_file, mode='a',
                                           encoding='utf-8', delay=False)                                   
        logging_file.setLevel(logging_level)
        logging_file.setFormatter(formatter)
        log.addHandler(logging_file)
    if options.verbose:
        levels = [logging.ERROR, logging.INFO, logging.DEBUG]
        logging_level = levels[min(len(levels) - 1, options.verbose)]
        # set the file logger level if it exists
        if logging_file:
            logging_file.setLevel(logging_level)
    # Check command name
    command = None
    if args[0] == 'count_permission_changes':
        command = 'count_permission_changes'
    elif args[0] == 'check_permission_first_use':
        command = 'check_permission_first_use'
    else:
        sys.exit(args[0] + ". Error: unknown command. Valid commands are: [count_permission_changes, check_permission_first_use]")
    # Check in/out files
    in_file = None
    out_file = None
    if os.path.isfile(args[1]):
        in_file = os.path.abspath(args[1])
    else:
        sys.exit("Error: source directory " + args[1] + " does not exist.")
    if os.path.isdir(os.path.abspath(os.path.join(args[3], os.pardir))) and not os.path.exists(args[3]):
        out_file = os.path.abspath(args[3])
    else:
        sys.exit("Error: out file " + args[3] + " cannot be created.")
    run_command(command, in_file, args[2], out_file, args[4:])
    print("======================================================")
    print("Finished after " + str(datetime.datetime.now() - start_time))
    print("======================================================")

if __name__ == '__main__':
    main(sys.argv[1:])
    
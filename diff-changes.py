#!/usr/bin/python
import pandas as pd
import numpy as np
import sys
import os
import datetime
import logging
from optparse import OptionParser


log = logging.getLogger("diff_changes")
# The logger's level must be set to the "lowest" level.
log.setLevel(logging.DEBUG)
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
    
def get_unique_diff(dataframe, count_column_name, result_column_name):
    print('|==================================================================|')
    print('| The difference in ' + count_column_name + ' between multiple versions.|')
    print('|==================================================================|')
    # Get the first index name (package name)
    first_index = dataframe.index.names[0]
    df_result = pd.DataFrame(columns=[first_index, 'number_of_versions', result_column_name])
    df_result.set_index(first_index, inplace =True)
    for gp in dataframe.index.get_level_values(first_index).unique():
        tmp_df = dataframe.loc[gp, count_column_name]
        # Only apps that have multiple versions.
        if len(tmp_df) < 2:
            print("Skipping " + gp + " because it has only " + str(len(tmp_df)) + " versions.")
            continue
        d = 0
        if len(tmp_df) == 1:
            d = 0
        else:
            l = tmp_df.tolist()
            d =  l[-1] - l[0]
        df_result.ix[gp, result_column_name] = d
        df_result.ix[gp, 'number_of_versions'] = len(tmp_df)
        vers = tmp_df.index.get_level_values('version_code')
        vers_str = ', '.join(str(x) for x in vers)
        df_result.ix[gp, 'versions_list'] = vers_str 
    return df_result

def get_list_diff(dataframe, list_column_name):
    ''' Returns a new Data frame that contains the added and dropped values 
    in the given list_column_name between the first and last version.
    '''
    print('|==================================================================|')
    print('| The difference in ' + list_column_name + ' between the first and last version|')
    print('|==================================================================|')
    # Get the first index name (package name)
    first_index = dataframe.index.names[0]
    second_index = dataframe.index.names[1]
    df_result = pd.DataFrame(columns=['package', 'previous_version_code', 'new_version_code', 'added', 'dropped'])
    df_result.set_index(keys=['package'], inplace = True)
    # get all packages
    packages = dataframe.index.get_level_values(first_index).unique()
    i = 0
    for package in packages:
        # for each package, get all versions
        version_codes_list = dataframe.ix[package].index.tolist()
        version_codes_list.sort()
        # Skip apps with one version
        if len(version_codes_list) < 2:
            continue
        for current_idx, version_code in enumerate(version_codes_list):
            next_idx = current_idx + 1
            if next_idx == len(version_codes_list):
                break
            previous_version_code = version_codes_list[current_idx]
            new_version_code = version_codes_list[next_idx]
            print('Comparing ' + package + ' version ' + str(previous_version_code) +
                  ' with version ' + str(new_version_code))
            previous_features = dataframe.loc[package, previous_version_code][list_column_name]
            if type(previous_features) is not str:
                previous_features = ''
            new_features = dataframe.loc[package, new_version_code][list_column_name]
            if type(new_features) is not str:
                new_features = ''
            added_features = set(new_features.split(',')) - set(previous_features.split(','))
            dropped_features = set(previous_features.split(',')) - set(new_features.split(','))
            if added_features is None or len(added_features) == 0:
                added_features = ''
            else:
                added_features = list(added_features)
            if dropped_features is None or len(dropped_features) == 0:
                dropped_features = ''
            else:
                dropped_features = list(dropped_features)
            row_dict = {'package': [package],
                        'previous_version_code': [str(previous_version_code)],
                        'new_version_code': [str(new_version_code)],
                        'added' :  ','.join(added_features),
                        'dropped' : ','.join(dropped_features)
                        }
            
            df_result = df_result.append(pd.DataFrame(row_dict))
            
    return df_result
    
def run_command(command, in_file, column_name, out_file):
    df_details = pd.read_csv(in_file)
    df_details.sort(columns=['package','version_code'], inplace=True)
    df_details.set_index(['package','version_code'], inplace=True)
    result_col_name = column_name + '_changes'
    df_changes = None
    if command == 'diff':
        df_changes = get_diff(df_details, column_name, result_col_name)
        df_changes.to_csv(out_file)
    elif command == 'unique_diff':
        df_changes = get_unique_diff(df_details, column_name, result_col_name)
        df_changes.to_csv(out_file)
    elif command == 'list_diff':
        df_changes = get_list_diff(df_details, column_name)
        df_changes.set_index(keys= ['package'], inplace = True)
        df_changes.to_csv(out_file, dtype = int)


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
    usage_info = ''' python %prog <COMMAND> <in_csv_file> <column_name> <out_csv_file> [options]
                     The following commands are available:
                     diff
                     unique_diff
                     list_diff'''
    description_paragraph = ("DESCRIPTION: Compare the changes to an app's feature over multiple versions")
    # command line parser
    parser = OptionParser(
                          usage=usage_info, description = description_paragraph,
                          version="%prog 1.0")
    parser.add_option("-l", "--log", dest="log_file", help="write logs to FILE.", metavar="FILE")
    parser.add_option('-v', '--verbose', dest="verbose", default=0,
                      action='count', help='increase verbosity.')
    (options, args) = parser.parse_args()
    if len(args) != 4:
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
    if args[0] == 'diff':
        command = 'diff'
    elif args[0] == 'unique_diff':
        command = 'unique_diff'
    elif args[0] == 'list_diff':
        command = 'list_diff'
    else:
        sys.exit(args[0] + ". Error: unknown command. Valid commands are: [diff, unique_diff, list_diff]")
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
    run_command(command, in_file, args[2], out_file)
    print("The result is saved at " + out_file)
    print("======================================================")
    print("Finished after " + str(datetime.datetime.now() - start_time))
    print("======================================================")

if __name__ == '__main__':
    main(sys.argv[1:])
    

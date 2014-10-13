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
    
def run_command(command, in_file, column_name, out_file):
    df_details = pd.read_csv(in_file)
    df_details.set_index(keys=['package'], inplace=True)
    df_changes = None
    if command == 'count_permission_changes':
        df_changes = count_permission_changes(df_details, column_name)
        df_changes.to_csv(out_file)

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
                     count_permission_changes'''
    description_paragraph = ("DESCRIPTION: Count the changes to an app's feature over multiple versions")
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
    if args[0] == 'count_permission_changes':
        command = 'count_permission_changes'
    else:
        sys.exit(args[0] + ". Error: unknown command. Valid commands are: [count_permission_changes]")
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
    print("======================================================")
    print("Finished after " + str(datetime.datetime.now() - start_time))
    print("======================================================")

if __name__ == '__main__':
    main(sys.argv[1:])
    
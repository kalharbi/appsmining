#!/usr/bin/python
import sys
import os
import datetime
import logging
import glob
import multiprocessing
import os.path
from helpers.resources_listing import ResourcesListing
from multiprocessing import Pool
from optparse import OptionParser
from subprocess import Popen, PIPE



log = logging.getLogger("layout_features_counter")
log.setLevel(logging.DEBUG) # The logger's level must be set to the "lowest" level.

def run_count_files(apk_dir):
    # check if the directory is for an unpacked apk. i.e, contains
    # AndroidManifest.xml
    manifest_file = os.path.abspath(
        os.path.join(apk_dir, 'AndroidManifest.xml'))
    if os.path.isdir(apk_dir) and os.path.isfile(manifest_file):
        log.info('Counting layout files in %s', apk_dir)
    else:
        log.error("AndroidManifest.xml file is missing. Not a valid unpacked apk dir: %s", apk_dir)
        return ('NA', False)
    layout_files = ResourcesListing.get_all_layout_files(apk_dir)
    return (apk_dir, len(layout_files))
        
class LayoutFilesCounter(object):
    # Set the number of worker processes to the number of available CPUs.
    processes = multiprocessing.cpu_count()
    
    def start_main(self, source_dir, target_dir):
        pool = Pool(processes=self.processes)
        log.info('A pool of %i worker processes has been created', self.processes)
        count = 0
        # Iterate over the unpacked apk files in the source directory.
        apk_dir_list = [os.path.join(source_dir, f) for f in os.listdir(source_dir)]
        if apk_dir_list > 0:
            # output file
            result_file_name = os.path.join(target_dir, 'count_layout_files.csv')
            result_file = open(result_file_name, 'w')
            result_file.write('package,version_code,layout_count' + '\n')
            results = [pool.apply_async(run_count_files, [apk_dir]) for apk_dir in apk_dir_list]
            for r in results:
                if r is not None:
                    (apk_dir, layout_count) = r.get()
                    if apk_dir == 'NA':
                        continue
                    package_name = os.path.basename(apk_dir).rsplit('-', 1)[0]
                    version_code = os.path.basename(apk_dir).rsplit('-', 1)[1]
                    result_file.write(package_name + ',' + version_code + ',' + str(layout_count) + '\n')
                           
            # close the pool to prevent any more tasks from being submitted to the pool.
            pool.close()
            # Wait for the worker processes to exit
            pool.join()
            log.info("The output has been written at: %s", result_file_name)
            result_file.close()
        else:
            log.error('Failed to find unpacked apk dirs in %s', source_dir)

        
    def main(self, args):
        start_time = datetime.datetime.now()
        # Configure logging
        logging_file = None
        logging_level = logging.ERROR
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        # Create console logger and set its formatter and level
        logging_console = logging.StreamHandler(sys.stdout)
        logging_console.setFormatter(formatter)
        logging_console.setLevel(logging.DEBUG)
        # Add the console logger
        log.addHandler(logging_console)

        # command line parser
        parser = OptionParser(
            usage="python %prog [options] unpacked_apk_dir target_dir",
            version="%prog 1.1",
            description='The layout files counter ')
        parser.add_option("-p", "--processes", dest="processes", type="int",
                           help="the number of worker processes to use. " +
                           "Default is the number of CPUs in the system.")
        parser.add_option("-l", "--log", dest="log_file",
                          help="write logs to FILE.", metavar="FILE")
        parser.add_option('-v', '--verbose', dest="verbose", default=0,
                          action='count', help='Increase verbosity.')
        (options, args) = parser.parse_args()
        if len(args) != 2:
            parser.error("incorrect number of arguments.")
        if options.processes:
            self.processes = options.processes
        if options.log_file:
            if not os.path.exists(os.path.dirname(options.log_file)):
                sys.exit("Error: Log file directory does not exist.")
            else:
                logging_file = logging.FileHandler(options.log_file, mode='a',
                                                   encoding='utf-8',
                                                   delay=False)
                logging_file.setLevel(logging_level)
                logging_file.setFormatter(formatter)
                log.addHandler(logging_file)
        if options.verbose:
            levels = [logging.ERROR, logging.INFO, logging.DEBUG]
            logging_level = levels[min(len(levels) - 1, options.verbose)]
            # set the file logger level if it exists
            if logging_file:
                logging_file.setLevel(logging_level)
        if os.path.isdir(args[0]) and os.path.isdir(args[1]):
            self.start_main(args[0], args[1])
        else:
            sys.exit("Error: No such directory.")

        print("======================================================")
        print("Finished after " + str(datetime.datetime.now() - start_time))
        print("======================================================")
    
    

if __name__ == '__main__':
    LayoutFilesCounter().main(sys.argv[1:])

#!/usr/bin/python
import sys
import os
import datetime
import logging
from optparse import OptionParser

from helpers.resources_listing import ResourcesListing
from helpers.app_info import AppInfo


class ScreenSupport(object):
    
    log = logging.getLogger("screen-support")
    # The logger's level must be set to the "lowest" level.
    log.setLevel(logging.DEBUG)
    
    # Find supported screen densities info  
    def find_screen_densities(self, apk_dirs, target_dir):
        result_file_name = os.path.join(
            target_dir, "screen_densities.csv")
        result_file = open(result_file_name, 'w')
        header_info = 'Package Name,' + 'Version Code,' + \
               "Number of Supported Screen Densities," + \
               "Supported Screen Densities" + '\n'
        result_file.write(header_info)
        count = 0
        apk_files = []
        for f in os.listdir(apk_dirs):
            if f.lower().endswith('.apk'):
                apk_files.append(os.path.abspath(os.path.join(apk_dirs, f)))
        if apk_files is None or len(apk_files) == 0:
            self.log.error('No apk files in %s', apk_dirs)
            return
        for apk_file in apk_files:
            count += 1
            self.log.info("%i Checking supported screen densities for %s", count, apk_file)
            app_info_obj = AppInfo(apk_file)
            screen_densities = app_info_obj.get_screen_densities()
            package_name, version_code, version_name = app_info_obj.get_version_info()
            screen_densities_list = ""
            screen_densities_count = 0
            if screen_densities is not None and len(screen_densities) > 0:
                screen_densities_list = ' '.join(map(str, screen_densities))
                screen_densities_count = len(screen_densities)
            result_file.write(
                package_name + ',' + version_code + ',' + str(screen_densities_count) + ',' + screen_densities_list + '\n')
    
    # Find supported screen size info    
    def find_screen_sizes(self, apk_dirs, target_dir):
        result_file_name = os.path.join(
            target_dir, "screen_sizes.csv")
        result_file = open(result_file_name, 'w')
        header_info = 'Package Name,' + 'Version Code,' + \
               "Number of Supported Screen Sizes," + \
               "normal,normal,large,xlarge" + '\n'
        result_file.write(header_info)
        count = 0
        apk_files = []
        for f in os.listdir(apk_dirs):
            if f.lower().endswith('.apk'):
                apk_files.append(os.path.abspath(os.path.join(apk_dirs, f)))
        if apk_files is None or len(apk_files) == 0:
            self.log.error('No apk files in %s', apk_dirs)
            return
        for apk_file in apk_files:
            count += 1
            self.log.info("%i Checking supported screen sizes for %s", count, apk_file)
            app_info_obj = AppInfo(apk_file)
            small, normal, large, xlarge = app_info_obj.get_screen_sizes()
            package_name, version_code, version_name = app_info_obj.get_version_info()
            screen_sizes_count = sum([small, normal, large, xlarge])
            result_file.write(
                package_name + ',' + version_code + ',' + 
                str(screen_sizes_count) + ',' + str(small) + ',' + str(normal) + ',' +
                str(large) + ',' + str(xlarge) + '\n')
        
    def start_main(self, command, source_dir, target_dir):
        if command == 'screen_sizes':
            self.find_screen_sizes(source_dir, target_dir)
        elif command == 'screen_densities':
            self.find_screen_densities(source_dir, target_dir)
        else:
            self.log.error('Unknown command.')

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
        self.log.addHandler(logging_console)

        usage_info = ''' python %prog <COMMAND> <source_directory> <target_directory> [options]
        
        The following commands are available:
        
        screen_sizes <directory_of_apk_files>
        screen_densities <directory_of_apk_files>
        '''
        description_paragraph = ("DESCRIPTION: Find the number of supported"
                   " screen sizes and densities of apps and save the"
                   " results into a .csv file at the given target_directory."
                   " Screen sizes and densities info are obtained from the"
                   " output of aapt tool.")
        
        # command line parser
        parser = OptionParser(
            usage=usage_info, description = description_paragraph,
            version="%prog 1.0")
        parser.add_option("-l", "--log", dest="log_file",
                          help="write logs to FILE.", metavar="FILE")
        parser.add_option('-v', '--verbose', dest="verbose", default=0,
                          action='count', help='increase verbosity.')

        (options, args) = parser.parse_args()
        if len(args) != 3:
            parser.error("incorrect number of arguments.")
        if options.log_file:
            logging_file = logging.FileHandler(options.log_file, mode='a',
                                               encoding='utf-8', delay=False)
            logging_file.setLevel(logging_level)
            logging_file.setFormatter(formatter)
            self.log.addHandler(logging_file)
        if options.verbose:
            levels = [logging.ERROR, logging.INFO, logging.DEBUG]
            logging_level = levels[min(len(levels) - 1, options.verbose)]

            # set the file logger level if it exists
            if logging_file:
                logging_file.setLevel(logging_level)
                
        # Check command name
        command = None
        if args[0] == 'screen_sizes':
            command = 'screen_sizes'
        elif args[0] == 'screen_densities':
            command = 'screen_densities'
        else:
            sys.exit(args[0] + ". Error: unknown command. Valid commands are: [screen_sizes, screen_densities]")
        # Check target directory
        source_dir = None
        target_dir = None
        if os.path.isdir(args[1]):
            source_dir = os.path.abspath(args[1])
        else:
            sys.exit("Error: source directory " + args[1] + " does not exist.")

        if os.path.isdir(args[2]):
            target_dir = os.path.abspath(args[2])
        else:
            sys.exit("Error: target directory " + args[2] + " does not exist.")
        self.start_main(command, source_dir, target_dir)

        print("======================================================")
        print("Finished after " + str(datetime.datetime.now() - start_time))
        print("======================================================")
        
if __name__ == '__main__':
    ScreenSupport().main(sys.argv[1:])
    
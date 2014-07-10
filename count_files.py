#!/usr/bin/python
import sys
import os
import datetime
import logging
from optparse import OptionParser

from helpers.resources_listing import ResourcesListing


class CountFiles(object):
    
    log = logging.getLogger("count-files")
    # The logger's level must be set to the "lowest" level.
    log.setLevel(logging.DEBUG)
    
    def find_layouts(self, source_dir, target_dir):
        result_file_name = os.path.join(
            target_dir, "default_layouts.csv")
        result_file = open(result_file_name, 'w')
        header_info = 'Package Name,' + 'Version Code,' + \
               "Number of Default Layouts" + '\n'
        result_file.write(header_info)
        count = 0
        # Iterate over the unpacked apk files in the source directory.
        for apk_dir in [os.path.join(source_dir, f) for f in os.listdir(source_dir)]:
            # check if the directory is for an unpacked apk. i.e, contains
            # AndroidManifest.xml
            manifest_file = os.path.abspath(
                os.path.join(apk_dir, 'AndroidManifest.xml'))
            if os.path.isdir(apk_dir) and os.path.isfile(manifest_file):
                try:
                    package_name = os.path.basename(apk_dir).rsplit('-', 1)[0]
                    version_code = os.path.basename(apk_dir).rsplit('-', 1)[1]
                    count += 1
                    self.log.info("%i Checking the number of default layouts for %s", count, apk_dir)
                    layouts = ResourcesListing.get_default_layout_files(apk_dir)
                    # Ignore the actual file names of layout files.
                    #layouts_files_list = ""
                    layouts_files_count = 0
                    if layouts is not None and len(layouts) > 0:
                        #layouts_files_list = ' '.join(map(str, layouts))
                        layouts_files_count = len(layouts)
                    result_file.write(
                        package_name + ',' + version_code + ',' + str(layouts_files_count) + '\n')
                except IndexError:
                    self.log.error(
                        'Directory must be named using the following scheme: packagename-versioncode')
        
    def find_specific_layouts(self, source_dir, target_dir):
        result_file_name = os.path.join(
            target_dir, "specific_layouts.csv")
        result_file = open(result_file_name, 'w')
        header_info = 'Package Name,' + 'Version Code,' + \
               "Number of Specific Layouts" + '\n'
        result_file.write(header_info)
        count = 0
        # Iterate over the unpacked apk files in the source directory.
        for apk_dir in [os.path.join(source_dir, f) for f in os.listdir(source_dir)]:
            # check if the directory is for an unpacked apk. i.e, contains
            # AndroidManifest.xml
            manifest_file = os.path.abspath(
                os.path.join(apk_dir, 'AndroidManifest.xml'))
            if os.path.isdir(apk_dir) and os.path.isfile(manifest_file):
                try:
                    package_name = os.path.basename(apk_dir).rsplit('-', 1)[0]
                    version_code = os.path.basename(apk_dir).rsplit('-', 1)[1]
                    count += 1
                    self.log.info("%i Checking the number of specific layouts for %s", count, apk_dir)
                    layouts = ResourcesListing.get_specific_layout_files(apk_dir)
                    # Ignore the actual file names of layout files.
                    #layouts_files_list = ""
                    layouts_files_count = 0
                    if layouts is not None and len(layouts) > 0:
                        #layouts_files_list = ' '.join(map(str, layouts))
                        layouts_files_count = len(layouts)
                    result_file.write(
                        package_name + ',' + version_code + ',' + str(layouts_files_count) + '\n')
                except IndexError:
                    self.log.error(
                        'Directory must be named using the following scheme: packagename-versioncode')
        
    def start_main(self, command, source_dir, target_dir):
        if command == 'default_layouts':
            self.find_layouts(source_dir, target_dir)
        elif command == 'specific_layouts':
            self.find_specific_layouts(source_dir, target_dir)
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
        
        default_layouts <directory_of_unpacked_apk_files>
        specific_layouts <directory_of_unpacked_apk_files>
        '''
        description_paragraph = ("DESCRIPTION: Find the number of default"
                   " layout files in apps and save the results into a .csv"
                   " file at the given target_directory. Default Layout files"
                   " are located in res/layout directories for normal screen"
                   " size (default). It also finds the number of specific"
                   " layouts for different screen sizes (e.g, layout-small)"
                   " or direction layouts (e.g, layout-ldrtl).")
        
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
        if args[0] == 'default_layouts':
            command = 'default_layouts'
        elif args[0] == 'specific_layouts':
            command = 'specific_layouts'
        else:
            sys.exit(args[0] + ". Error: unknown command. Valid commands are: [default_layouts, specific_layouts]")
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
    CountFiles().main(sys.argv[1:])
    
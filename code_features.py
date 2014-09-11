#!/usr/bin/python
import sys
import os
import datetime
import logging
import glob
from optparse import OptionParser

class CodeFeatures(object):
    
    log = logging.getLogger("code_features")
    # The logger's level must be set to the "lowest" level.
    log.setLevel(logging.DEBUG)
    
    # Find whether an app uses shared library files or not.
    def find_ndk(self, source_dir, target_dir):
        result_file_name = os.path.join(
            target_dir, "ndk_support.csv")
        result_file = open(result_file_name, 'w')
        header_info = 'Package Name,' + 'Version Code,' + \
               "NDK Support" + '\n'
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
                    ndk_support = False
                    self.log.info("%i - Checking NDK support for %s", count, apk_dir)
                    lib_dir = os.path.join(apk_dir, 'lib')
                    if os.path.isdir(lib_dir):
                        # check if shared library files exist
                        native_files = glob.glob(lib_dir + '/*/*.so')
                        if native_files:
                            ndk_support = True
                    elements_count = 0
                    result_file.write(
                        package_name + ',' + version_code + ',' + str(ndk_support) + '\n')
                except IndexError:
                    self.log.error(
                        'Directory must be named using the following scheme: packagename-versioncode')
    
    # Find whether an app uses Apache Cordova framework or not
    def find_cordova(self, source_dir, target_dir):
        return 0
    # Find whether an app uses PhoneGap framework or not
    def find_phonegap(self, source_dir, target_dir):
        return 0
        
    def start_main(self, command, source_dir, target_dir):
        if command == 'ndk':
            self.find_ndk(source_dir, target_dir)
        elif command == 'cordova':
            self.find_cordova(source_dir, target_dir)
        elif command == 'phonegap':
            self.find_phonegap(source_dir, target_dir)
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
        
        ndk <directory_of_unpacked_apk_files>
        cordova <directory_of_unpacked_apk_files>
        phonegap <directory_of_unpacked_apk_files>
        '''
        description_paragraph = ("DESCRIPTION: Find features in source code files."
                   " Features include specific libraries."
                   " These features are extracted from lib/* or smali/*"
                   " The results are saved in a .csv file at the given target_directory.")
        
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
        if args[0] == 'ndk':
            command = 'ndk'
        elif args[0] == 'cordova':
            command = 'cordova'
        elif args[0] == 'phonegap':
            command = 'phonegap'
        else:
            sys.exit(args[0] + ". Error: unknown command. Valid commands are: [ndk, cordova, phonegap]")
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
    CodeFeatures().main(sys.argv[1:])
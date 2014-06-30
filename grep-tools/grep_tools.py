#!/usr/bin/python
import sys
import os
import datetime
import logging
from optparse import OptionParser
from subprocess import Popen, PIPE


class GrepTools(object):
    log = logging.getLogger("grep-tools")
    # The logger's level must be set to the "lowest" level.
    log.setLevel(logging.DEBUG)
    # Flag that indicates the use of custom directory naming scheme. i.e.
    # dir/c/com/a/amazon/com.amazon
    use_custom_file_search = False

    def __init__(self):
        self.apk_files = []

    def find_fragments(self, package_name, version_code, apk_dir):
        search_words = "'Landroid/app/Fragment\|Landroid/app/DialogFragment\|Landroid/app/ListFragment\|Landroid/app/PreferenceFragment\|Landroid/app/WebViewFragment'"
        source_dirs = self.get_source_directories(apk_dir)
        if len(source_dirs) == 0:
            self.log.error(
                'No source code directories for package: %s , version code: %s', package_name, version_code)
        found = False
        for d in source_dirs:
            sub_process = Popen(
                ['grep', '-nr', search_words, d], stdout=PIPE, stderr=PIPE)
            out, err = sub_process.communicate()
            if out:
                self.log.info(
                    "Fragment found for %s - %s: %s", package_name, version_code, out)
                found = True
                # No need to search in other directories, so stop right here.
                break
            if err:
                self.log.error(
                    "Error in Fragment search for package: %, version code %s. %s",
                    package_name, version_code, err)
        return found

    # Return the source directories inside /smali/ excluding /smali/android
    @staticmethod
    def get_source_directories(apk_root_path):
        dir_list = []
        for d in [os.path.join(apk_root_path, f) for f in os.listdir(apk_root_path)]:
            if os.path.isdir(d) and os.path.basename(d) != 'android':
                dir_list.append(d)
        return dir_list

    def start_main(self, command, source_dir, target_dir):
        result_file_name = os.path.join(
            target_dir, "grep_files_" + command + ".csv")
        result_file = open(result_file_name, 'w')
        result_file.write('package_name,' + 'version_code,' + command + '\n')
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
                    if command == 'find_fragments':
                        count += 1
                        self.log.info("%i Running grep on %s", count, apk_dir)
                        found = self.find_fragments(
                            package_name, version_code, apk_dir)
                        result_file.write(
                            package_name + ',' + version_code + ',' + str(found) + '\n')
                except IndexError:
                    self.log.error(
                        'Directory must be named using the following scheme: packagename-versioncode')
        result_file.close

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

        usage_info = ''' python %prog COMMAND <unpacked_apk_source_directory> <target_directory> [options]
        
        Run grep command to find patterns in unpacked Android apks.
        
        The following commands are available:
        find_fragments
        '''
        # command line parser
        parser = OptionParser(usage=usage_info, version="%prog 1.0")
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
        if args[0] == 'find_fragments':
            command = 'find_fragments'
        else:
            sys.exit(args[0] + ". Error: unknown command.")

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
    GrepTools().main(sys.argv[1:])

#!/usr/bin/python
import sys
import os
import datetime
import logging
from optparse import OptionParser

import pycountry
from helpers.resources_listing import ResourcesListing


class FindLanguages(object):
    log = logging.getLogger("grep-tools")
    # The logger's level must be set to the "lowest" level.
    log.setLevel(logging.DEBUG)

    def find_languages(self, package_name, version_code, apk_dir):
        values_dirs = ResourcesListing.get_values_directories(apk_dir)
        supported_languages = []
        if len(values_dirs) == 0:
            self.log.error(
                'No res/values directories for package: %s , version code: %s', package_name, version_code)
            return
        for res_val_dir in values_dirs:
            dir_name = os.path.basename(res_val_dir)
            if dir_name == 'values':
                lang = 'English'
                if lang not in supported_languages:
                    supported_languages.append(lang)
                    continue
            elif '-' in dir_name:
                try:
                    lang_code = dir_name.split('-')[1]
                    lang = self.get_language_name(lang_code)
                    
                    if lang is not None and lang not in supported_languages:
                        supported_languages.append(lang)
                        continue
                except IndexError:
                    self.log.error('Unknown res/values directory name. %s (package: %s, version code: %s)',
                                   res_val_dir, package_name, version_code)
                    continue
        return supported_languages

    def get_language_name(self, language_code):
        try:
            lang_unicode_name = pycountry.languages.get(alpha2=language_code).name
            return lang_unicode_name.encode('ascii','ignore')
        except (KeyError, UnicodeEncodeError):
            self.log.error('Unknown language code %s', language_code)
            return None

    def start_main(self, source_dir, target_dir):
        result_file_name = os.path.join(
            target_dir, "languages.csv")
        result_file = open(result_file_name, 'w')
        header_info = 'Package Name,' + 'Version Code,' + "No. of Supported Languages" + ',' + \
                      "Supported Languages" + '\n'
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
                    self.log.info("%i Checking supported languages for %s", count, apk_dir)
                    languages = self.find_languages(
                        package_name, version_code, apk_dir)
                    languages_list = ""
                    if len(languages) > 0:
                        languages_list = '=='.join(map(str, languages))
                    result_file.write(
                        package_name + ',' + version_code + ',' + str(len(languages)) + ',' + languages_list + '\n')
                except IndexError:
                    self.log.error(
                        'Directory must be named using the following scheme: packagename-versioncode')

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

        usage_info = ''' python %prog <unpacked_apk_source_directory> <target_directory> [options]
        
        Find supported langauges in Android apps and save the results into a .csv file at the given target_directory.'''
        # command line parser
        parser = OptionParser(usage=usage_info, version="%prog 1.0")
        parser.add_option("-l", "--log", dest="log_file",
                          help="write logs to FILE.", metavar="FILE")
        parser.add_option('-v', '--verbose', dest="verbose", default=0,
                          action='count', help='increase verbosity.')

        (options, args) = parser.parse_args()
        if len(args) != 2:
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

        # Check target directory
        source_dir = None
        target_dir = None
        if os.path.isdir(args[0]):
            source_dir = os.path.abspath(args[0])
        else:
            sys.exit("Error: source directory " + args[0] + " does not exist.")

        if os.path.isdir(args[1]):
            target_dir = os.path.abspath(args[1])
        else:
            sys.exit("Error: target directory " + args[1] + " does not exist.")
        self.start_main(source_dir, target_dir)

        print("======================================================")
        print("Finished after " + str(datetime.datetime.now() - start_time))
        print("======================================================")


if __name__ == '__main__':
    FindLanguages().main(sys.argv[1:])

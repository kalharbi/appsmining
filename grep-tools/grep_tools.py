#!/usr/bin/python
import sys
import os
import datetime
import logging
import xml.etree.ElementTree as ET
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

    def find_fragment(self, package_name, version_code, apk_dir):
        search_words = r"Landroid/app/Fragment\|Landroid/app/DialogFragment\|Landroid/app/ListFragment\|Landroid/app/PreferenceFragment\|Landroid/app/WebViewFragment"
        source_dirs = self.get_source_directories(apk_dir)
        if len(source_dirs) == 0:
            self.log.error(
                'No source code directories for package: %s , version code: %s', package_name, version_code)
        found = False
        for d in source_dirs:
            sub_process = Popen(
                ['grep', '-r', search_words, d], stdout=PIPE, stderr=PIPE)
            out, err = sub_process.communicate()
            if out:
                self.log.info(
                    "Fragment found for %s - %s.", package_name, version_code)
                found = True
                # No need to search in other directories, so stop right here.
                break
            if err:
                self.log.error(
                    "Error in Fragment search for package: %s, version code %s. %s",
                    package_name, version_code, err)
        return found
    
    # Returns the type of the webview the app uses (Android Webview, CordovaWebView,
    def find_webview(self, package_name, version_code, apk_dir):
        # 1 - search in the source code directories for the class 'android.webkit.WebView'
        search_words = r"Landroid/webkit/WebView\|Lorg/apache/cordova/CordovaWebView"
        source_dirs = self.get_source_directories(apk_dir)
        if len(source_dirs) == 0:
            self.log.warn(
                'No source code directories for package: %s , version code: %s', package_name, version_code)
        for d in source_dirs:
            sub_process = Popen(
                ['grep', '-r', search_words, d], stdout=PIPE, stderr=PIPE)
            out, err = sub_process.communicate()
            if out:
                self.log.info(
                    "Found WebView in source code files for %s - %s.", package_name, version_code)
                if 'Landroid/webkit/WebView' in out:
                    return 'WebView'
                elif 'Lorg/apache/cordova/CordovaWebView' in out:
                    return 'CordovaWebView'
                else:
                    return 'other'
            if err:
                self.log.warn(
                    "Error in WebView search for package: %s, version code %s. %s",
                    package_name, version_code, err)
        # 2 - If nothin is found in source files, search for a <WebView> element in the XML layout files
        layout_files = self.get_layout_files(os.path.join(apk_dir, 'res'))
        for layout in layout_files:
            webView_elements = self.find_element_in_xml_file(layout, 'WebView')
            if webView_elements:
                self.log.info('Found %i WebView elements in layout files.', len(webView_elements))
                return 'WebView'
            else:
                cordovaWebView_elements = self.find_element_in_xml_file(layout, 'org.apache.cordova.CordovaWebView')
                if cordovaWebView_elements:
                    return 'CordovaWebView'
        self.log.info("WebView is not found in package: %s, version code: %s", package_name, version_code)
        return None
        

    # Return the source directories inside /smali/ excluding /smali/android
    @staticmethod
    def get_source_directories(apk_root_path):
        smali_path = os.path.join(apk_root_path, 'smali')
        dir_list = []
        for d in [os.path.join(smali_path, f) for f in os.listdir(smali_path)]:
            if os.path.isdir(d) and os.path.basename(d) != 'android':
                dir_list.append(d)
        return dir_list
        
    # Return the layout files inside /res/layout*
    @staticmethod
    def get_layout_files(apk_res_path):
        layout_files = []
        for d in [os.path.join(apk_res_path, f) for f in os.listdir(apk_res_path)]:
            if os.path.isdir(d) and os.path.basename(d).lower().startswith('layout'):
                for layout_file in [os.path.join(d, lf) for lf in os.listdir(d)]:
                    if layout_file.lower().endswith('.xml'):
                        layout_files.append(layout_file)
        return layout_files
        
    # Search for an element in an xml file.
    @staticmethod    
    def find_element_in_xml_file(xml_file, element_name):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        return root.findall(element_name)
        
    def get_out_header(self, command):
        if command == 'find_fragment':
            return 'Package Name,' + 'Version Code,' + "Fragment" + '\n'
        elif command == 'find_webview':
            return 'Package Name,' + 'Version Code,' + "WebView" + '\n'
    
    def start_main(self, command, source_dir, target_dir):
        result_file_name = os.path.join(
            target_dir,  command + ".csv")
        result_file = open(result_file_name, 'w')
        header_info = self.get_out_header(command)
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
                    if command == 'find_fragment':
                        count += 1
                        self.log.info("%i Running grep on %s", count, apk_dir)
                        found = self.find_fragment(
                            package_name, version_code, apk_dir)
                        result_file.write(
                            package_name + ',' + version_code + ',' + str(found) + '\n')
                    elif command == 'find_webview':
                        count += 1
                        self.log.info("%i Running grep on %s", count, apk_dir)
                        webview = self.find_webview(
                            package_name, version_code, apk_dir)
                        found = False
                        webview_type = ""
                        if webview:
                            found = True
                            webview_type = webview
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
        find_fragment
        find_webview
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
        if args[0] == 'find_fragment':
            command = 'find_fragment'
        elif args[0] == 'find_webview':
            command = 'find_webview'
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

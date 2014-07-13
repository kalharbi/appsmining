#!/usr/bin/python
import sys
import os
import datetime
import logging
from xml.etree import ElementTree
from xml.etree.ElementTree import QName
from optparse import OptionParser
from helpers.resources_listing import ResourcesListing

class LayoutFeatures(object):
    
    NAME_SPACE= "http://schemas.android.com/apk/res/android"
    log = logging.getLogger("grep-tools")
    # The logger's level must be set to the "lowest" level.
    log.setLevel(logging.DEBUG)
    
    def find_on_click(self, source_dir, target_dir):
        result_file_name = os.path.join(
            target_dir, "on_click.csv")
        result_file = open(result_file_name, 'w')
        header_info = 'Package Name,' + 'Version Code,' + \
               "Number of used on_click" + '\n'
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
                    self.log.info("%i - Checking the number of elements with android:onClick attribute for %s", count, apk_dir)
                    layout_files = ResourcesListing.get_all_layout_files(apk_dir)
                    print("Number of layout files: " + str(len(layout_files)))
                    elements_count = 0
                    for layout_file in layout_files:
                        elements = self.find_xml_elements_by_attribute(layout_file, 'onClick')
                        elements_count += len(elements)
                    result_file.write(
                        package_name + ',' + version_code + ',' + str(elements_count) + '\n')
                except IndexError:
                    self.log.error(
                        'Directory must be named using the following scheme: packagename-versioncode')
        
    def find_image_button(self, source_dir, target_dir):
        result_file_name = os.path.join(
            target_dir, "image_button.csv")
        result_file = open(result_file_name, 'w')
        header_info = 'Package Name,' + 'Version Code,' + \
               "Number of ImageButton elements" + '\n'
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
                    self.log.info("%i - Checking the number of ImageButton elements for %s", count, apk_dir)
                    layout_files = ResourcesListing.get_all_layout_files(apk_dir)
                    image_buttons_count = 0
                    for layout_file in layout_files:
                        elements = self.find_xml_elements_by_name(layout_file, 'ImageButton')
                        image_buttons_count += len(elements)
                    result_file.write(
                        package_name + ',' + version_code + ',' + str(image_buttons_count) + '\n')
                except IndexError:
                    self.log.error(
                        'Directory must be named using the following scheme: packagename-versioncode')
        
    
    # Search for an element in an xml file.
    @staticmethod
    def find_xml_elements_by_name(xml_file, element_name):
        tree = ElementTree.parse(xml_file)
        root = tree.getroot()
        return root.findall(element_name)
    
    # Search for an attribute in an xml file.
    @staticmethod
    def find_xml_elements_by_attribute(xml_file, attribute_name):
        
        # Returns elements that contain this attribute
        elements_list = []
        tree = ElementTree.parse(xml_file)
        root = tree.getroot()
        attribute_full_name = str(QName(LayoutFeatures.NAME_SPACE, attribute_name))
        for element in root.iter("*"):
            if element.get(attribute_full_name):
                elements_list.append(element.tag)
        return elements_list
        
    def start_main(self, command, source_dir, target_dir):
        if command == 'on_click':
            self.find_on_click(source_dir, target_dir)
        elif command == 'image_button':
            self.find_image_button(source_dir, target_dir)
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
        
        on_click <directory_of_unpacked_apk_files>
        image_button <directory_of_unpacked_apk_files>
        '''
        description_paragraph = ("DESCRIPTION: Find features in layout files."
                   " Features include xml elements and attributes."
                   " These features are extracted from res/layout*/*.xml"
                   " files, which are the layouts for normal and specific screen sizes."
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
        if args[0] == 'on_click':
            command = 'on_click'
        elif args[0] == 'image_button':
            command = 'image_button'
        else:
            sys.exit(args[0] + ". Error: unknown command. Valid commands are: [on_click, image_button]")
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
    LayoutFeatures().main(sys.argv[1:])
#!/usr/bin/python
import sys
import os
import datetime
import logging
from lxml.etree import ParserError
from lxml.etree import XMLSyntaxError
from lxml import etree
from xml.etree import ElementTree
from xml.etree.ElementTree import QName
from optparse import OptionParser
from helpers.resources_listing import ResourcesListing

class LayoutFeatures(object):
    
    NAME_SPACE= "http://schemas.android.com/apk/res/android"
    log = logging.getLogger("grep-tools")
    # The logger's level must be set to the "lowest" level.
    log.setLevel(logging.DEBUG)
    
    def __init__(self):
        self.element_name = None
        self.attribute_name = None
        self.attribute_name_not_present = False
        
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
    
    def find_ui_element(self, source_dir, target_dir):
        if self.element_name is None:
            abort("Please specify the element name using the -e option.")
        result_file_name = os.path.join(
            target_dir, self.element_name + ".csv")
        header_info = 'package,' + 'version_code,' + \
               "use_" + self.element_name + "_elements," + \
               "count,files"'\n'
        if self.attribute_name is not None:
            result_file_name = os.path.join(
                target_dir, "use_" + self.element_name.strip() + "_" + self.attribute_name.strip() + ".csv")
            header_info = 'package,' + 'version_code,' + \
                   "use_" + self.element_name + "_elements_with_" + self.attribute_name.replace(":","_").strip() + \
                   ",count,files"'\n'
        if self.attribute_name_not_present:
            result_file_name = os.path.join(
                target_dir, "no_use_" + self.element_name.strip() + "_" + self.attribute_name.strip() + ".csv")
            header_info = 'package,' + 'version_code,' + \
                   "use_" + self.element_name + "_elements_without_" + self.attribute_name.replace(':',"_").strip() + \
                   ",count,files"'\n'
                   
        result_file = open(result_file_name, 'w')
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
                    self.log.info("%i - Checking the number of " + self.element_name + " elements for %s", count, apk_dir)
                    layout_files = ResourcesListing.get_all_layout_files(apk_dir)
                    element_name_count = 0
                    found = False
                    layout_file_names = []
                    layout_files_names_list = ""
                    for layout_file in layout_files:
                        elements = self.find_xml_elements_by_name(layout_file, self.element_name, 
                                                                  self.attribute_name, self.attribute_name_not_present)
                        element_name_count += len(elements)
                        if len(elements) > 0:
                            found = True
                            dir_name = os.path.basename(os.path.dirname(layout_file))
                            layout_file_names.append(dir_name + "/" + os.path.basename(layout_file))
                            layout_files_names_list = '|'.join(map(str, layout_file_names))
                    result_file.write(
                        package_name + ',' + version_code + ',' + str(found) + ',' + str(element_name_count) + ',' + layout_files_names_list + '\n')
                except IndexError:
                    self.log.error(
                        'Directory must be named using the following scheme: packagename-versioncode')
        
    def find_custom_widgets(self, source_dir, target_dir):
        result_file_name = os.path.join(
            target_dir, "custom_widgets.csv")
        result_file = open(result_file_name, 'w')
        header_info = 'package,' + 'version_code,' + \
               "totalCustomWidgets, allCustomWidgets" + '\n'
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
                    self.log.info("%i - Checking the number of custom widget elements for %s", count, apk_dir)
                    layout_files = ResourcesListing.get_all_layout_files(apk_dir)
                    custom_widgets_count = 0
                    custom_widgets = set()
                    for layout_file in layout_files:
                        elements = self.find_custom_xml_elements(layout_file)
                        for e in elements:
                            e_base = '.'.join(e.tag.split('.')[:3])
                            custom_widgets.add(e_base)
                        custom_widgets_count += len(elements)
                    result_file.write(
                        package_name + ',' + version_code + ',' + str(custom_widgets_count) + \
                        ',"' + ','.join(custom_widgets) + '"' +  '\n')
                    custom_widgets = None
                except IndexError:
                    self.log.error(
                        'Directory must be named using the following scheme: packagename-versioncode')
                except UnicodeEncodeError:
                    self.log.error('Encoding error in %s-%s', package_name, version_code)
                        
    # Search for an element in an xml file.
    @staticmethod
    def find_xml_elements_by_name(xml_file, element_name, attribute_name, exclude_attribute = False):
        try:
            tree = etree.parse(xml_file)
            xpath_query = "//" + element_name + ""
            if attribute_name is not None:
                xpath_query = "//" + element_name + "[@" + attribute_name + "]"
            if exclude_attribute:
                xpath_query = "//" + element_name + "[not(@" + attribute_name + ")]"
            return tree.xpath(xpath_query, 
                              namespaces={'android': "http://schemas.android.com/apk/res/android"})
        except (ParserError, XMLSyntaxError) as e:
            print("Error in file: %s",xml_file)
        return []
    
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
    
    @staticmethod
    def find_xml_elements_start_with_name(xml_file, start_name):
        try:
            tree = etree.parse(xml_file)
            xpath_query = "//*[starts-with(name(), '" + start_name + "')]"
            return tree.xpath(xpath_query)
        except (ParserError, XMLSyntaxError) as e:
            print("Error in file: %s",xml_file)
        return []
    
    @staticmethod
    def find_custom_xml_elements(xml_file):
        try:
            tree = etree.parse(xml_file)
            xpath_query = "//*[contains(name(), '.')]"
            return tree.xpath(xpath_query)
        except (ParserError, XMLSyntaxError) as e:
            print("Error in file: %s",xml_file)
        return []
        
    def start_main(self, command, source_dir, target_dir):
        if command == 'on_click':
            self.find_on_click(source_dir, target_dir)
        elif command == 'ui_element':
            self.find_ui_element(source_dir, target_dir)
        elif command == 'custom_widgets':
            self.find_custom_widgets(source_dir, target_dir)
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
        ui_element <directory_of_unpacked_apk_files> -e element_name -a attribute_name
        custom_widgets <directory_of_unpacked_apk_files>
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
        parser.add_option('-e', '--element', dest="element",
                          help='the name of the UI element.')
        parser.add_option('-x', '--exclude-attribute', action="store_true",
                          default=False, dest="attribute_name_not_present",
                          help='Exclude the attribute name from the search. For example, ' +
                          'find elements where the given attribute name (-a attribute_name) is not present.')
        parser.add_option('-a', '--attribute', dest="attribute",
                          help='the name of the UI element and attribute.')
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
        if options.element:
            self.element_name = options.element
        if options.attribute:
            self.attribute_name = options.attribute
        if options.verbose:
            levels = [logging.ERROR, logging.INFO, logging.DEBUG]
            logging_level = levels[min(len(levels) - 1, options.verbose)]
        if options.attribute_name_not_present:
            self.attribute_name_not_present = True

            # set the file logger level if it exists
            if logging_file:
                logging_file.setLevel(logging_level)
                
        # Check command name
        command = None
        if args[0] == 'on_click':
            command = 'on_click'
        elif args[0] == 'ui_element':
            command = 'ui_element'
        elif args[0] == 'custom_widgets':
            command = 'custom_widgets'
        elif args[0] == 'ui_element_attribute':
            command = 'ui_element_attribute'
        else:
            sys.exit(args[0] + ". Error: unknown command. Valid commands are: [on_click, ui_element, custom_widgets]")
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

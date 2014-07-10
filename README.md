# appsmining
A set of tools for mining Android apps.

## grep_tools.py
This tool runs grep on unpacked apk files to find fragments and webviews.

```
Usage:  python grep_tools.py COMMAND <unpacked_apk_source_directory> <target_directory> [options]
        
        Run grep command to find patterns in unpacked Android apks.
        
        The following commands are available:
        find_fragment
		find_webview
        

Options:  --version            show program's version number and exit
  -h, --help           show this help message and exit
  -l FILE, --log=FILE  write logs to FILE.
  -v, --verbose        increase verbosity.
```

## find_langauges.py
This tool finds supported languages and locales.

```
Usage:  python find_langauges.py <COMMAND> <source_directory> <target_directory> [options]
        
        The following commands are available:
        
        find_locales <directory_of_apk_files>
        find_languages <directory_of_unpacked_apk_files>        

DESCRIPTION: Find supported locales and languages in apps and save the results
into a .csv file at the given target_directory. Locales are obtained from aapttool. Languages are found in res/values directories that are named with an
additional hyphen and the ISO language code at the end of the values directory
name.

Options:
  --version            show program's version number and exit
  -h, --help           show this help message and exit
  -l FILE, --log=FILE  write logs to FILE
```

##  count_files.py
This tool gets the number of default and specific layout files. 

```
Usage:  python count_files.py <COMMAND> <source_directory> <target_directory> [options]
        
        The following commands are available:
        
        default_layouts <directory_of_unpacked_apk_files>
        specific_layouts <directory_of_unpacked_apk_files>        

DESCRIPTION: Find the number of default layout files in apps and save the
results into a .csv file at the given target_directory. Default Layout filesare located in res/layout directories for normal screen size (default). It
also finds the number of specific layouts for different screen sizes (e.g,
layout-small) or direction layouts (e.g, layout-ldrtl).

Options:
  --version            show program's version number and exit
  -h, --help           show this help message and exit
  -l FILE, --log=FILE  write logs to FILE.
  -v, --verbose        increase verbosity.
```

## screen_support.py
This tool finds the supported screen sizes and densities.

```
Usage:  python screen_support.py <COMMAND> <source_directory> <target_directory> [options]
        
        The following commands are available:
        
        screen_sizes <directory_of_apk_files>
        screen_densities <directory_of_apk_files>        

DESCRIPTION: Find the number of supported screen sizes and densities of apps
and save the results into a .csv file at the given target_directory. Screensizes and densities info are obtained from the output of aapt tool.

Options:
  --version            show program's version number and exit
  -h, --help           show this help message and exit
  -l FILE, --log=FILE  write logs to FILE.
  -v, --verbose        increase verbosity.
```

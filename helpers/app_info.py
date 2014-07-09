from config.conf import *
from subprocess import Popen, PIPE

class AppInfo(object):
    
    def __init__(self, apk_file):
        self.apk_file = apk_file
        self.run_aapt()
    
    def run_aapt(self):
        sub_process = Popen(
            [AAPT, 'dump', 'badging', self.apk_file], stdout=PIPE, stderr=PIPE)
        out, err = sub_process.communicate()
        if out:
            self.aapt_out = out
        if err:
            self.aapt_out = None
            self.log.error('Failed to run aapt on %s', self.apk_file)
    
    def get_version_info(self):
        package_name = version_code = version_name = None
        if self.aapt_out:
            for line in self.aapt_out.split('\n'):
                if line.startswith('package:'):
                    fields = line.split(' ',1)[1].split(' ')
                    for field in fields:
                        if field.startswith('name='):
                            package_name = field.split('name=',1)[1].replace("'", "")
                        elif field.startswith('versionCode='):
                            version_code = field.split('versionCode=',1)[1].replace("'", "")
                        elif field.startswith('versionName='):
                            version_name = field.split('versionName=',1)[1].replace("'", "")
                break
        return package_name, version_code, version_name
        
    
    # Find supported languages by running aapt.  
    def get_languages_from_aapt(self):
        languages_arr = []
        if self.aapt_out:
            for line in self.aapt_out.split('\n'):
                if line.startswith('locales:'):
                    languages_arr = line.split(' ',1)[1].split(' ')
                    break
        return languages_arr
        
        
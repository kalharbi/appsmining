import os
import os.path


class ResourcesListing(object):
    # Return the source directories inside /smali/ excluding /smali/android
    @staticmethod
    def get_source_directories(apk_root_path):
        smali_path = os.path.join(apk_root_path, 'smali')
        dir_list = []
        if not os.path.exists(smali_path):
            return []
        for d in [os.path.join(smali_path, f) for f in os.listdir(smali_path)]:
            if os.path.isdir(d) and os.path.basename(d) != 'android':
                dir_list.append(d)
        return dir_list

    # Return the values directories inside /res/
    @staticmethod
    def get_values_directories(apk_root_path):
        res_path = os.path.join(apk_root_path, 'res')
        dir_list = []
        if not os.path.exists(res_path):
            return []
        for d in [os.path.join(res_path, f) for f in os.listdir(res_path)]:
            if os.path.isdir(d) and os.path.basename(d).lower().startswith('values'):
                dir_list.append(d)
        return dir_list

    # Return all the layout files inside /res/layout*
    @staticmethod
    def get_all_layout_files(apk_root_path):
        apk_res_path = os.path.join(apk_root_path, 'res')
        if not os.path.exists(apk_res_path):
           return []
        layout_files = []
        for d in [os.path.join(apk_res_path, f) for f in os.listdir(apk_res_path)]:
            if os.path.isdir(d) and os.path.basename(d).lower().startswith('layout'):
                for layout_file in [os.path.join(d, lf) for lf in os.listdir(d)]:
                    if layout_file.lower().endswith('.xml'):
                        layout_files.append(layout_file)
        return layout_files
        
    # Return all the widget layout files inside /res/xmlayout*
    @staticmethod
    def get_all_widget_layout_files(apk_root_path):
        apk_res_path = os.path.join(apk_root_path, 'res')
        if not os.path.exists(apk_res_path):
           return []
        layout_files = []
        for d in [os.path.join(apk_res_path, f) for f in os.listdir(apk_res_path)]:
            if os.path.isdir(d) and os.path.basename(d).lower().startswith('xml'):
                for layout_file in [os.path.join(d, lf) for lf in os.listdir(d)]:
                    if layout_file.lower().endswith('.xml'):
                        layout_files.append(layout_file)
        return layout_files
    
    # Return all the layout files inside /res/layout for normal screen size (default)
    @staticmethod
    def get_default_layout_files(apk_root_path):
        apk_res_path = os.path.join(apk_root_path, 'res')
        layout_files = []
        if not os.path.exists(apk_res_path):
            return []
        for d in [os.path.join(apk_res_path, f) for f in os.listdir(apk_res_path)]:
            if os.path.isdir(d) and os.path.basename(d) == 'layout':
                for layout_file in [os.path.join(d, lf) for lf in os.listdir(d)]:
                    if layout_file.lower().endswith('.xml'):
                        layout_files.append(layout_file)
        return layout_files
        
    # Return all the specific layout files inside /res/layout-* for specific screen size
    # Or for specific layout direction (e.g, /res/layout-ldrtl for "right-to-left" language)
    @staticmethod
    def get_specific_layout_files(apk_root_path):
        apk_res_path = os.path.join(apk_root_path, 'res')
        layout_files = []
        if not os.path.exists(apk_res_path):
            return []
        for d in [os.path.join(apk_res_path, f) for f in os.listdir(apk_res_path)]:
            if os.path.isdir(d) and os.path.basename(d).startswith('layout-'):
                for layout_file in [os.path.join(d, lf) for lf in os.listdir(d)]:
                    if layout_file.lower().endswith('.xml'):
                        layout_files.append(layout_file)
        return layout_files

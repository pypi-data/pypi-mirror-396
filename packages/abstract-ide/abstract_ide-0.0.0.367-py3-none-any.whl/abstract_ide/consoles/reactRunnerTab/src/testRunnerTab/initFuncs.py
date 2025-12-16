

from abstract_utilities import get_logFile
from .functions import (_group_key_from, _have_babel, _inspect_exports_babel, _inspect_exports_regex, _introspect_file_exports, _looks_server_safe, base_path, build_args_json, current_mode, group_key_from, have_babel, inspect_exports_babel, inspect_exports_regex, install_analyzers, load_all, load_functions_folder, load_functions_folder_grouped, load_packages, load_pkg_functions, looks_server_safe, on_path_changed, open_function_file, open_item, reload_all, run_function, show_inputs, update_topbar_visibility)
logger=get_logFile(__name__)
def initFuncs(self):
    try:
        for f in (_group_key_from, _have_babel, _inspect_exports_babel, _inspect_exports_regex, _introspect_file_exports, _looks_server_safe, base_path, build_args_json, current_mode, group_key_from, have_babel, inspect_exports_babel, inspect_exports_regex, install_analyzers, load_all, load_functions_folder, load_functions_folder_grouped, load_packages, load_pkg_functions, looks_server_safe, on_path_changed, open_function_file, open_item, reload_all, run_function, show_inputs, update_topbar_visibility):
            setattr(self, f.__name__, f)
    except Exception as e:
        logger.info(f"{e}")
    return self

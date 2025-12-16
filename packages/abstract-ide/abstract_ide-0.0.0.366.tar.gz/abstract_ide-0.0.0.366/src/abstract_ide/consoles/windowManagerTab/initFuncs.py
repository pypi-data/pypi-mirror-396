

from abstract_utilities import get_logFile
from .functions import (_build_ui, _selected_rows, activate_window, close_selected, control_window, get_self, is_self, move_window, open_file, refresh, run_command, select_all_by_type, should_close, update_monitor_dropdown, update_table, wm_clear_highlights, wm_compute_self_ids, wm_refresh_monitors, wm_refresh_windows)
logger=get_logFile(__name__)
def initFuncs(self):
    try:
        for f in (_build_ui, _selected_rows, activate_window, close_selected, control_window, get_self, is_self, move_window, open_file, refresh, run_command, select_all_by_type, should_close, update_monitor_dropdown, update_table, wm_clear_highlights, wm_compute_self_ids, wm_refresh_monitors, wm_refresh_windows):
            setattr(self, f.__name__, f)
    except Exception as e:
        logger.info(f"{e}")
    return self

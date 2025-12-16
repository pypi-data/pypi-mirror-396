

from abstract_utilities import get_logFile
from .functions import (_slug, apply_profile, autofill_media_file, cancel_tasks, closeEvent, display_results, get_proxy_pool, init_ui, load_profiles, load_proxy_list, log, save_results, start_crawl, start_scrape, toggle_buttons)
logger=get_logFile(__name__)
def initFuncs(self):
    try:
        for f in (_slug, apply_profile, autofill_media_file, cancel_tasks, closeEvent, display_results, get_proxy_pool, init_ui, load_profiles, load_proxy_list, log, save_results, start_crawl, start_scrape, toggle_buttons):
            setattr(self, f.__name__, f)
    except Exception as e:
        logger.info(f"{e}")
    return self

# abstract_x11/monitor_utils.py
import re
from typing import List, Tuple

def get_monitors(run_cmd) -> List[Tuple[str, int, int, int, int]]:
    """
    Returns [(name, x, y, w, h)]
    """
    out = run_cmd("xrandr --query | grep ' connected'")
    monitors = []

    for line in out.splitlines():
        m = re.match(r"(\S+)\s+connected\s+(\d+)x(\d+)\+(\d+)\+(\d+)", line)
        if m:
            name, w, h, x, y = m.groups()
            monitors.append((name, int(x), int(y), int(w), int(h)))

    return monitors

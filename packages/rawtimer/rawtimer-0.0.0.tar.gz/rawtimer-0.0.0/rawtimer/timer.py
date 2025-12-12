import time
from typing import Optional

BAN_ALL_TIMER_CNT = 0
__global_obj_timer_name_dict = {}

class _TimerSilentObject:
    def __enter__(self):
        global BAN_ALL_TIMER_CNT
        BAN_ALL_TIMER_CNT += 1
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        global BAN_ALL_TIMER_CNT
        BAN_ALL_TIMER_CNT -= 1
        return False # do not ignore exception

# use `with timer_silent():` to make all timer silent
def timer_silent():
    return _TimerSilentObject()

def _extend_str(s:str, min_len:int) -> str:
    if len(s) < min_len:
        s += " " * (min_len - len(s))
    return s

def begin_timer(name: str):
    assert __global_obj_timer_name_dict.get(name) is None
    __global_obj_timer_name_dict[name] = time.time()

DEFAULT_MIN_NAME_LEN = 0
def _get_default_min_name_len(name:str) -> int:
    if DEFAULT_MIN_NAME_LEN <= 0:
        return len(name)
    else:
        return DEFAULT_MIN_NAME_LEN

def set_default_min_name_len(val:int):
    if not isinstance(val, int):
        raise TypeError("type of val should be int")
    global DEFAULT_MIN_NAME_LEN
    DEFAULT_MIN_NAME_LEN = val

def end_timer(name: str, disp: bool = True, min_name_len:Optional[int]=None) -> float:
    assert __global_obj_timer_name_dict.get(name) is not None
    
    if min_name_len is None:
        min_name_len = _get_default_min_name_len(name)

    # Calculate elapsed time
    time_cost = time.time() - __global_obj_timer_name_dict[name]

    # Remove the timer from the dictionary
    del __global_obj_timer_name_dict[name]

    # Display the timer result
    if disp and (BAN_ALL_TIMER_CNT <= 0):

        # Names starting with $ are displayed in yellow
        if name.startswith("$"):
            print(f"Timer [\033[1;33m{_extend_str(name, min_name_len)}\033[0m]: {time_cost:13.6f}s")

        # Names starting with # are displayed in red
        elif name.startswith("#"):
            print(f"Timer [\033[1;31m{_extend_str(name, min_name_len)}\033[0m]: {time_cost:13.6f}s")

        # Other names are displayed in green
        else:
            print(f"Timer [\033[1;32m{_extend_str(name, min_name_len)}\033[0m]: {time_cost:13.6f}s")
    return time_cost

# rawtimer
a simple timer manager.

GitHub repo: [https://github.com/GGN-2015/rawtimer](https://github.com/GGN-2015/rawtimer)

## Installation
```bash
pip install rawtimer
```

## Usage
```python
import rawtimer
import time

rawtimer.begin_timer("timer_name_1")
time.sleep(2.0)                    # Do something that you want to time
rawtimer.end_timer("timer_name_1") # this will output a line into stdout

# means do not output to show time cost
with rawtimer.timer_silent(): 
    rawtimer.begin_timer("timer_name_1")
    time.sleep(2.0)
    time_cost = rawtimer.end_timer("timer_name_1") # silent
    print(f"time_cost: {time_cost:13.3f}s")        # you can output yourself

# you can use this function to make alignment, if necessary
rawtimer.set_default_min_name_len(30)

# if the timer name begins with character '$', when output, its name will be in yellow
rawtimer.begin_timer("$special_timer_1")
time.sleep(2.0)
rawtimer.end_timer("$special_timer_1")

# if the timer name begins with character '#', when output, its name will be in red
rawtimer.begin_timer("#special_timer_2")
time.sleep(2.0)
rawtimer.end_timer("#special_timer_2")
```

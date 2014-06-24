import json
import os
import time

def get_cache_path():
    home = os.path.expanduser("~")
    return home + '/package_list.cdncache'


def time_has_passed(last_time, time_now):
    time_is_blank = time_now is None or last_time is None
    if time_is_blank:
        return time_is_blank
    time_difference = int(time.time()) - int(last_time)
    time_has_passed = time_difference > int(time_now)
    print(time_difference)
    print(time_has_passed)
    
    return time_has_passed


def get_package_list(path):
    packageList = {}
    with open(path, 'r') as f:
        packageList = json.loads(f.read())
    return packageList


def set_package_list(path, packageList):
    with open(path, 'w') as f:
        f.write(json.dumps(packageList))
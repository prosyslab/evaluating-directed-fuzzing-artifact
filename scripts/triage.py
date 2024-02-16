import re

TOP_SIG = " #0 "


def warn(msg, buf):
    print("[Warning]: %s" % msg)
    print("Check the following replay log:")
    print(buf)


# Obtain the function where the crash had occurred.
def get_crash_func(buf):
    match = re.search(r"#0 0x[0-9a-f]+ in [\S]+", buf)
    if match is None:
        return ""
    start_idx, end_idx = match.span()
    line = buf[start_idx:end_idx]
    return line.split()[-1]


# Get all functions appearing in the stack trace.
def get_all_funcs(buf):
    matches = re.findall(r"#(?:[0-9a-f]+) (?:0x[0-9a-f]+) in ([\S]+)", buf)
    return set(matches)


# Get the direct caller of the function that crashed.
def get_crash_func_caller(buf):
    match = re.search(r"#1 0x[0-9a-f]+ in [\S]+", buf)
    if match is None:
        return ""
    start_idx, end_idx = match.span()
    line = buf[start_idx:end_idx]
    return line.split()[-1]


# Helper function for for-all check.
def check_all(buf, checklist):
    for str_to_check in checklist:
        if str_to_check not in buf:
            return False
    return True


# Helper function for if-any check.
def check_any(buf, checklist):
    for str_to_check in checklist:
        if str_to_check in buf:
            return True
    return False


def check_TODO(buf):
    print("TODO: implement triage logic")
    return False


####################################################################################
####################################################################################
####################################################################################


def check_cxxfilt_2016_4487(buf):
    if get_crash_func(buf) == "register_Btype":
        return "cplus-dem.c:4319" in buf
    return False


def check_cxxfilt_2016_4489(buf):
    return check_all(buf, ["string_appendn", "cplus-dem.c:4839"])


def check_cxxfilt_2016_4490(buf):
    if get_crash_func(buf) == "d_unqualified_name":
        return "cp-demangle.c:1596" in buf
    return False


def check_cxxfilt_2016_4491(buf):
    return check_all(buf, ["stack-overflow", "d_print_comp"])


def check_cxxfilt_2016_4492(buf):
    if "stack-overflow" in buf:
        return False
    if get_crash_func(buf) == "do_type":
        if check_any(buf, ["cplus-dem.c:3606", "cplus-dem.c:3781"]):
            return True
    return False


def check_cxxfilt_2016_6131(buf):
    if check_all(buf, ["stack-overflow", "do_type"]):
        if check_all(buf, [
                "demangle_arm_hp_template", "demangle_class_name",
                "demangle_fund_type"
        ]):
            warn("Unexpected crash point in do_type", buf)
            return True
    return False


def check_swftophp_2016_9827(buf):
    if "heap-buffer-overflow" in buf:
        if "outputscript.c:1687:" in buf:
            return True
    return False


def check_swftophp_2016_9829(buf):
    if "heap-buffer-overflow" in buf:
        if "parser.c:1656:" in buf:
            return True
    return False


def check_swftophp_2016_9831_v1(buf):
    if "heap-buffer-overflow" in buf:
        # Only triage BOF at line 66 as a targeted bug
        if "parser.c:66:" in buf:
            return True
    return False


def check_swftophp_2016_9831_v2(buf):
    if "heap-buffer-overflow" in buf:
        # Any BOF that occurs in line 66~69 corresponds to this CVE.
        if re.search(r"parser.c:6[6-9]:", buf) is not None:
            return True
    return False


def check_swftophp_2016_9831_v3(buf):
    if "heap-buffer-overflow" in buf:
        # Any BOF that occurs in line 66~69,  corresponds to this CVE.
        if re.search(r"parser.c:6[6-9]:", buf) is not None:
            return True
        elif "parser.c:745:" in buf or "parser.c:747:" in buf:
            return True
    return False


def check_swftophp_2017_9988(buf):
    if "SEGV" in buf:
        if "parser.c:2995:" in buf:
            return True
    return False


def check_swftophp_2017_11728(buf):
    if "heap-buffer-overflow" in buf:
        if "decompile.c:868" in buf:
            if get_crash_func_caller(buf) == "decompileSETMEMBER":
                return True
    return False


def check_swftophp_2017_11729(buf):
    if "heap-buffer-overflow" in buf:
        if "decompile.c:868" in buf:
            if get_crash_func_caller(buf) == "decompileINCR_DECR":
                return True
    return False

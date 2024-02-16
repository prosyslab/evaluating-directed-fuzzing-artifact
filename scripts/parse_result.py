import sys, os, csv
from common import csv_read
from benchmark import EXP_ENV, check_targeted_crash_asan, check_targeted_crash_patch
from stats import average_tte, median_tte, min_max_tte
import pandas as pd

BASE_DIR = os.path.join(os.path.dirname(__file__), os.pardir)
DATA_DIR = os.path.join(BASE_DIR, "output", "data")
REPLAY_ORIG_FILE = "replay_log.txt"
ALT_REPLAY_ORIG_FILE = "replay_log_orig.txt"
REPLAY_PATCH_FILE = {
    "": "replay_log_patch.txt",
    "a": "replay_log_patch_a.txt",
    "b": "replay_log_patch_b.txt",
}
FOUND_TIME_FILE = "found_time.csv"
FUZZ_LOG_FILE = "fuzzer_stats"
REPLAY_ITEM_SIG = "Replaying crash - "
ADDITIONAL_INFO_SIG = " is located "
FOUND_TIME_SIG = "found at "
FUZZER_STATS_FILE = "fuzzer_stats"


def parse_timeout(stats_file):
    with open(stats_file, "r", encoding="latin-1") as f:
        start_time = int(f.readline().split(':')[1])
        end_time = int(f.readline().split(':')[1])
    return end_time - start_time


def get_experiment_info(outdir):
    targ_list = []
    max_iter_id = 0
    for d in os.listdir(outdir):
        if d.endswith("-iter-0"):
            targ = d[:-len("-iter-0")]
            targ_list.append(targ)
            timeout = parse_timeout(os.path.join(outdir, d, FUZZER_STATS_FILE))
        iter_id = int(d.split("-")[-1])
        if iter_id > max_iter_id:
            max_iter_id = iter_id
    iter_cnt = max_iter_id + 1
    return (targ_list, iter_cnt, timeout)


def parse_found_time(log_file):
    f = open(log_file, "r", encoding="latin-1")
    buf = f.read()
    f.close()
    time_list = []
    while REPLAY_ITEM_SIG in buf:
        # Proceed to the next item.
        start_idx = buf.find(REPLAY_ITEM_SIG)
        buf = buf[start_idx + len(REPLAY_ITEM_SIG):]
        # Identify the end of this replay.
        if REPLAY_ITEM_SIG in buf:
            end_idx = buf.find(REPLAY_ITEM_SIG)
        else:  # In case this is the last replay item.
            end_idx = len(buf)
        replay_buf = buf[:end_idx]
        # If there is trailing allocsite information, remove it.
        if ADDITIONAL_INFO_SIG in replay_buf:
            remove_idx = buf.find(ADDITIONAL_INFO_SIG)
            replay_buf = replay_buf[:remove_idx]
        found_time = int(replay_buf.split(FOUND_TIME_SIG)[1].split()[0])
        time_list.append(found_time)
    return time_list


def split_replay(buf):
    replays = []
    while REPLAY_ITEM_SIG in buf:
        # Proceed to the next item.
        start_idx = buf.find(REPLAY_ITEM_SIG)
        buf = buf[start_idx + len(REPLAY_ITEM_SIG):]
        # Identify the end of this replay.
        if REPLAY_ITEM_SIG in buf:
            end_idx = buf.find(REPLAY_ITEM_SIG)
        else:  # In case this is the last replay item.
            end_idx = len(buf)
        replay_buf = buf[:end_idx]
        # If there is trailing allocsite information, remove it.
        if ADDITIONAL_INFO_SIG in replay_buf:
            remove_idx = buf.find(ADDITIONAL_INFO_SIG)
            replay_buf = replay_buf[:remove_idx]
        replays.append(replay_buf)
    return replays


def read_sa_results():
    df = pd.read_csv(os.path.join(BASE_DIR, 'sa_overhead.csv'))
    targets = list(df['Target'])
    dafl = list(df['DAFL'])
    aflgo = list(df['AFLGo'])
    aflgo = list(df['SelectFuzz'])
    beacon = list(df['Beacon'])

    sa_dict = {}
    for tool in ["DAFL", "SelectFuzz", "AFLGo", "Beacon"]:
        sa_dict[tool] = {}
        for i in range(len(targets)):
            sa_dict[tool][targets[i]] = df[tool][i]
    return sa_dict


def parse_tte(targ, targ_dir, triage_ver):
    found_time_file = os.path.join(targ_dir, FOUND_TIME_FILE)
    replay_orig_file = os.path.join(targ_dir, REPLAY_ORIG_FILE)
    if not os.path.exists(replay_orig_file):
        replay_orig_file = os.path.join(targ_dir, ALT_REPLAY_ORIG_FILE)
    found_time_list = list(map(int, csv_read(found_time_file)[0]))
    n_crash = len(found_time_list)
    with open(replay_orig_file, "r", encoding="latin-1") as f:
        replay_orig_list = split_replay(f.read())
    if len(replay_orig_list) != n_crash:
        print("Number of crash from replay_orig and found_time does not match")
        exit(1)
    if triage_ver.startswith("asan"):
        for i in range(n_crash):
            if check_targeted_crash_asan(targ, replay_orig_list[i],
                                         triage_ver):
                return found_time_list[i]
        return None
    elif triage_ver.startswith("patch"):
        replay_patch_file = os.path.join(
            targ_dir, REPLAY_PATCH_FILE[triage_ver[len("patch-"):]])
        with open(replay_patch_file, "r", encoding="latin-1") as f:
            replay_patch_list = split_replay(f.read())
        if len(replay_patch_list) != n_crash:
            print(
                "Number of crash from replay_patch and found_time does not match"
            )
            exit(1)
        for i in range(n_crash):
            if check_targeted_crash_patch(targ, replay_orig_list[i],
                                          replay_patch_list[i]):
                return found_time_list[i]
        return None
    else:
        print(f"Unknown triage method: {triage_ver}")
        exit(1)


def parse_tte_list(outdir, targ, iter_cnt, triage_ver):
    tte_list = []
    for iter_id in range(iter_cnt):
        targ_dir = os.path.join(outdir, "%s-iter-%d" % (targ, iter_id))
        tte = parse_tte(targ, targ_dir, triage_ver)
        tte_list.append(tte)
    return tte_list


def analyze_targ_result(outdir, timeout, targ, iter_cnt, triage_ver):
    tte_list = parse_tte_list(outdir, targ, iter_cnt, triage_ver)
    print("(Result of %s)" % targ)
    print("Timeout: %d" % timeout)
    print("Time-to-error: %s" % tte_list)
    print("Avg: %s" % average_tte(tte_list, timeout))
    print("Med: %s" % median_tte(tte_list, timeout))
    print("Min: %s\nMax: %s" % min_max_tte(tte_list, timeout))
    if None in tte_list:
        print("T/O: %d times" % tte_list.count(None))
    print("------------------------------------------------------------------")


def print_table(data_dir, outdir, target, tools, target_list, df_dict,
                       name, triage_vers=None):
    timelimit = EXP_ENV["TIMELIMTS"][name] if "original" not in data_dir else 86400
    iterations = EXP_ENV["ITERATIONS"][name] if "original" not in data_dir else 160
    if triage_vers is None:
        triage_vers = ["patch"]
    else:
        triage_vers = triage_vers.split()

    for tool in tools:
        med_tte_list = []
        for targ in target_list:
            targ_dir = os.path.join(data_dir, "%s-%s" % (targ, tool))
            for triage in triage_vers:
                tte_list = parse_tte_list(targ_dir, targ,
                                          iterations, triage)
                med_tte = median_tte(tte_list, timelimit)
                found_iter_cnt = iterations - len([
                        x for x in tte_list
                        if (x is None or x > timelimit)
                    ])
                if ">" in med_tte:
                    med_tte = "N.A.(%d)" % (found_iter_cnt)
                elif name == "table6":
                    med_tte = "%s (%d)" % (med_tte, found_iter_cnt)
                med_tte_list.append(med_tte)
        df_dict[tool] = med_tte_list

    tte_df = pd.DataFrame.from_dict(df_dict)
    tte_df.to_csv(os.path.join(outdir, "%s.csv" % target), index=False)


def print_result_custom_target(data_dir, outdir, target, tools, target_list):
    df_dict = {}
    df_dict["Target CVE"] = target_list
    print_table(data_dir, outdir, target, tools, target_list, df_dict,
                       "custom")


def print_result_table3(data_dir, outdir, target, tools, target_list):
    df_dict = {}
    df_dict["Target Location"] = ["Line 9", "Line 14"]
    print_table(data_dir, outdir, target, tools, target_list, df_dict,
                       "table3")


def print_result_table4(data_dir, outdir, target, tools, target_list):
    df_dict = {}
    df_dict["Target Location"] = ["Line 4", "Line 13"]
    print_table(data_dir, outdir, target, tools, target_list, df_dict,
                       "table4")


def print_result_table5(data_dir, outdir, target, tools, target_list):
    df_dict = {}
    df_dict["Lines Checked"] = ["17", "17-20", "17-20, 10, 12"]
    print_table(data_dir, outdir, target, tools, target_list, df_dict,
                    "table5", "asan-a asan-b asan-c")


def print_result_table6(data_dir, outdir, target, tools, target_list):
    df_dict = {}
    df_dict["Patch Used"] = ["Incomplete", "Complete"]
    print_table(data_dir, outdir, target, tools, target_list, df_dict,
                       "table6", "patch-a patch-b")


def print_result_table8(data_dir, outdir, target, tools, target_list):
    timelimit = EXP_ENV["TIMELIMTS"]["table8"] if "original" not in data_dir else 86400
    iterations = EXP_ENV["ITERATIONS"]["table8"] if "original" not in data_dir else 160
    triage = "patch"

    df_dict = {}
    df_dict["CVE"] = ["CVE-2016-4489", "CVE-2016-9831"]
    sa_dict = read_sa_results()
    fuzzing_dict = {}
    sa_fuzzing_dict = {}

    for tool in tools:
        med_tte_list = []
        sa_med_tte_list = []
        for targ in target_list:
            targ_dir = os.path.join(data_dir, "%s-%s" % (targ, tool))
            tte_list = parse_tte_list(targ_dir, targ,
                                      iterations, triage)
            med_tte = median_tte(tte_list, timelimit)
            if ">" in med_tte:
                found_iter_cnt = iterations - len([
                    x for x in tte_list
                    if (x is None or x > timelimit)
                ])
                med_tte = "N.A.(%d)" % (found_iter_cnt)
            elif tool in sa_dict:
                sa_med_tte = str(int(med_tte) + sa_dict[tool][targ])

            med_tte_list.append(med_tte)
            sa_med_tte_list.append(sa_med_tte)
        fuzzing_dict[tool] = med_tte_list
        sa_fuzzing_dict[tool] = sa_med_tte_list

    for tool in tools:
        df_dict[tool + " (T_f)"] = fuzzing_dict[tool]

    for tool in tools:
        df_dict[tool + " (T_f + T_sa)"] = sa_fuzzing_dict[tool]

    tte_df = pd.DataFrame.from_dict(df_dict)
    tte_df.to_csv(os.path.join(outdir, "%s.csv" % target), index=False)


def print_result_table9(data_dir, outdir, target, tools, target_list):
    timelimit = EXP_ENV["TIMELIMTS"]["table9"] if "original" not in data_dir else 86400
    iterations = EXP_ENV["ITERATIONS"]["table9"] if "original" not in data_dir else 160
    triage = "patch"
    
    df_dict = {}
    df_dict["Target CVE"] = []
    df_dict[" "] = []
    for targ in target_list:
        if "crash" in targ or "caller" in targ:
            continue
        df_dict["Target CVE"].append(targ)
        df_dict["Target CVE"].append(targ)
        df_dict["Target CVE"].append(targ)

        df_dict[" "].append("min")
        df_dict[" "].append("max")
        df_dict[" "].append("med")

    for tool in tools:
        stat_list = []
        for targ in target_list:
            if "crash" in targ or "caller" in targ:
                continue
            if tool == "AFLGo" and "2016-4487" in targ:
                stat_list.append("-")
                stat_list.append("-")
                stat_list.append("-")
                continue
            targ_dir = os.path.join(data_dir, "%s-%s" % (targ, tool))
            tte_list = parse_tte_list(targ_dir, targ,
                                      iterations, triage)
            tte_list = [
                x if x != None else timelimit for x in tte_list
            ]
            min_tte = min(tte_list)
            max_tte = max(tte_list)

            med_tte = median_tte(tte_list, timelimit)
            if ">" in med_tte:
                med_tte = "N.A."
            if max_tte == timelimit:
                TO_iter_cnt = len(
                    [x for x in tte_list if x >= timelimit])
                max_tte = "T.O.(%d)" % (TO_iter_cnt)
            if min_tte == timelimit:
                min_tte = "N.A."

            stat_list.append(min_tte)
            stat_list.append(max_tte)
            stat_list.append(med_tte)

        df_dict[tool] = stat_list

    tte_df = pd.DataFrame.from_dict(df_dict)
    tte_df.to_csv(os.path.join(outdir, "%s.csv" % target), index=False)


def print_result_figure(data_dir, outdir, target, tools, target_list, name):
    timelimit = EXP_ENV["TIMELIMTS"][name] if "original" not in data_dir else 86400
    iterations = EXP_ENV["ITERATIONS"][name] if "original" not in data_dir else 160
    triage = "patch"

    file = open(os.path.join(outdir, "%s.csv" % target), mode='w', newline='')
    writer = csv.writer(file)

    for tool in tools:
        for targ in target_list:
            targ_dir = os.path.join(data_dir, "%s-%s" % (targ, tool))
            tte_list = parse_tte_list(targ_dir, targ,
                                      iterations, triage)
            tte_list = [
                x if x != None else timelimit for x in tte_list
            ]

        writer.writerow([tool] + tte_list)

    file.close()


def print_result(data_dir, outdir, target, tools, target_list):
    if target == "table3":
        print_result_table3(data_dir, outdir, target, tools, target_list)
    elif target == "table4":
        print_result_table4(data_dir, outdir, target, tools, target_list)
    elif target == "table5":
        print_result_table5(data_dir, outdir, target, tools, target_list)
    elif target == "table6":
        print_result_table6(data_dir, outdir, target, tools, target_list)
    elif target == "table8":
        print_result_table8(data_dir, outdir, target, tools, target_list)
    elif target == "table9":
        print_result_table9(data_dir, outdir, target, tools, target_list)
    elif target == "figure6":
        print_result_figure(data_dir, outdir, target, tools, target_list,
                            "figure6")
    elif target == "figure7":
        print_result_figure(data_dir, outdir, target, tools, target_list,
                            "figure7")
    else:
        print_result_custom_target(data_dir, outdir, target, tools,
                                   target_list)


def main():
    if len(sys.argv) != 3:
        print("Usage: %s <output dir> <triage method>" % sys.argv[0])
        exit(1)
    outdir = sys.argv[1]
    triage_ver = sys.argv[2]
    targ_list, iter_cnt, timeout = get_experiment_info(outdir)
    targ_list.sort()
    for targ in targ_list:
        analyze_targ_result(outdir, timeout, targ, iter_cnt, triage_ver)


if __name__ == "__main__":
    main()

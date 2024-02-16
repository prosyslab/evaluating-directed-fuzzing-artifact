import sys, os
from common import csv_write_row
from parse_result import get_experiment_info, parse_tte_list

RESULT_FILE = 'result.csv'


def save_targ_result(outdir, timeout, targ, iter_cnt, triage_vers):
    for triage_ver in triage_vers.split():
        tte_list = parse_tte_list(outdir, targ, iter_cnt, triage_ver)
        tte_list = [x if x != None else 86400 for x in tte_list]

        if not os.path.isfile(RESULT_FILE):
            csv_write_row(RESULT_FILE,
                          ["DIR", "TARGET", "TIMEOUT", "ITER", "TRIAGE_VER"])

        csv_write_row(
            RESULT_FILE,
            [os.path.basename(os.path.normpath(outdir)).split("-")[-1], targ] +
            tte_list, True)


def main():
    if len(sys.argv) != 3:
        print("Usage: %s <replay dir> <triage methods>" % sys.argv[0])
        exit(1)
    replay_dir = sys.argv[1]
    triage_vers = sys.argv[2]

    targ_list, iter_cnt, timeout = get_experiment_info(replay_dir)
    targ_list.sort()
    for targ in targ_list:
        save_targ_result(replay_dir, timeout, targ, iter_cnt, triage_vers)


if __name__ == "__main__":
    main()

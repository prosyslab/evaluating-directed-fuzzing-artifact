import sys, os, time, csv
from common import *
from benchmark import generate_replay_worklist
from parse_result import get_experiment_info, parse_found_time

IMAGE_NAME = "directed-fuzzing-benchmark"
TIMEOUT_FILE = "timeout"

def spawn_containers(works, fuzz_result):
    for i in range(len(works)):
        targ_prog, _, _, iter_id = works[i]
        crash_dir =  os.path.join(fuzz_result, f"{targ_prog}-{iter_id}", "crashes")
        cmd = "docker run --tmpfs /box:exec --rm -m=4g -v%s:/crashes -it -d --name %s-%s %s" \
                % (crash_dir, targ_prog, iter_id, IMAGE_NAME)
        run_cmd(cmd)
    

def run_replay(works, patch_vers):
    for (targ_prog, cmdline, src, iter_id) in works:
        cmd = "/tool-script/replay.sh %s \"%s\" \"%s\" \"%s\"" % (targ_prog, cmdline, src, patch_vers)
        run_cmd_in_docker(f"{targ_prog}-{iter_id}", cmd, True)


def wait_finish(works):
    total_count = len(works)
    elapsed_min = 0
    while True:
        time.sleep(60)
        elapsed_min += 1
        print("Waited for %d min" % elapsed_min)
        finished_count = 0
        for (targ_prog, _, _, iter_id) in works:
            container = "%s-%s" % (targ_prog, iter_id)
            stat_str = run_cmd_in_docker(container, "cat /STATUS", False)
            if "FINISHED" in stat_str:
                finished_count += 1
            else:
                print("%s-%s not finished" % (targ_prog, iter_id))
        if finished_count == total_count:
            print("All works finished!")
            break


def store_outputs(works, outdir):
    for (targ_prog, _, _, iter_id) in works:
        container = "%s-%s" % (targ_prog, iter_id)
        cmd = "docker cp %s:/output %s/%s" % (container, outdir, container)
        run_cmd(cmd)


def cleanup_containers(works):
    for (targ_prog, _, _, iter_id) in works:
        cmd = "docker kill %s-%s" % (targ_prog, iter_id)
        run_cmd(cmd)


def save_found_times(works, fuzz_result, outdir):
    for (targ_prog, _, _, iter_id) in works:
        iter_dir  = os.path.join(outdir, f"{targ_prog}-{iter_id}")
        run_cmd(f"mkdir -p {iter_dir}")
        log_file =  os.path.join(fuzz_result, f"{targ_prog}-{iter_id}", "replay_log.txt")
        time_list = parse_found_time(log_file)
        cp_log_file = os.path.join(outdir, f"{targ_prog}-{iter_id}", "replay_log_orig.txt")
        cmd = f"cp {log_file} {cp_log_file}"
        run_cmd(cmd)
        result_file = os.path.join(outdir, f"{targ_prog}-{iter_id}", "found_time.csv")
        csv_write_row(result_file, time_list, True)


def save_fuzzer_stats(works, fuzz_result, outdir):
    for (targ_prog, _, _, iter_id) in works:
        stats_file =  os.path.join(fuzz_result, f"{targ_prog}-{iter_id}", "fuzzer_stats")
        result_file =  os.path.join(outdir, f"{targ_prog}-{iter_id}", "fuzzer_stats")
        cmd = f"cp {stats_file} {result_file}"
        run_cmd(cmd)


def replay_crashes(fuzz_result, outdir, patch_vers):
    targ_list, iter_cnt, timeout = get_experiment_info(fuzz_result)
    for targ in targ_list:
        worklist = generate_replay_worklist(targ, iter_cnt)
        while len(worklist) > 0:
            works = fetch_works(worklist)
            spawn_containers(works, fuzz_result)
            run_replay(works, patch_vers)
            wait_finish(works)
            store_outputs(works, outdir)
            cleanup_containers(works)
            save_found_times(works, fuzz_result, outdir)
            save_fuzzer_stats(works, fuzz_result, outdir)

def main():
    if len(sys.argv) not in [3, 4]:
        print("Usage: %s <fuzz_result> <outdir> (patch_vers)" % sys.argv[0])
        exit(1)
    fuzz_result = os.path.abspath(sys.argv[1])
    outdir = sys.argv[2]
    patch_vers = sys.argv[3] if len(sys.argv) == 4 else "orig default"
    for ver in patch_vers.split():
        if ver not in ['a', 'b', 'c', 'orig', 'default']:
            print(f"Unknown patch version: {ver}")
            exit(1)

    run_cmd(f"mkdir -p {outdir}")
    replay_crashes(fuzz_result, outdir, patch_vers)

if __name__ == "__main__":
    main()
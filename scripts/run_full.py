import sys, os, time, csv, shutil
from common import run_cmd, run_cmd_in_docker, check_cpu_count, fetch_works, MEM_PER_INSTANCE
from benchmark import generate_fuzzing_worklist, FUZZ_TARGETS, SUB_TARGETS, TIMEOUTS
from benchmark import under5000, under21600, under43200, under86400
from parse_result import print_result
from plot import draw_figure5, draw_figure7, draw_figure8, draw_figure9, draw_result
import copy

BASE_DIR = os.path.join(os.path.dirname(__file__), os.pardir)
IMAGE_NAME = "directed-fuzzing-benchmark"
SUPPORTED_TOOLS = \
  [ "AFLGo", "Beacon", "WindRanger","SelectFuzz", "DAFL" ]


def decide_outdir(isReproduce, target, tool):
    name = "%s-%ssec-%siters" % (target, timelimit, iteration)
    if isReproduce:
        outdir = os.path.join(BASE_DIR, "output", "origin")
    elif tool == "":
        outdir = os.path.join(BASE_DIR, "output", target)
    else:
        outdir = os.path.join(BASE_DIR, "output", target, tool)
    os.makedirs(outdir, exist_ok=True)
    return outdir


def spawn_containers(works):
    for i in range(len(works)):
        targ_prog, _, _, iter_id = works[i]
        cmd = "docker run --tmpfs /box:exec --rm -m=%dg --cpuset-cpus=%d -it -d --name %s-%s %s" \
                % (MEM_PER_INSTANCE, i, targ_prog, iter_id, IMAGE_NAME)
        run_cmd(cmd)


def run_fuzzing(works, tool, timelimit):
    for (targ_prog, cmdline, src, iter_id) in works:
        cmd = "/tool-script/run_%s.sh %s \"%s\" %s %d" % \
                (tool, targ_prog, cmdline, src, timelimit)
        run_cmd_in_docker("%s-%s" % (targ_prog, iter_id), cmd, True)


def wait_finish(works, timelimit):
    time.sleep(timelimit)
    total_count = len(works)
    elapsed_min = 0
    while True:
        if elapsed_min > 120:
            break
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


def main():
    if len(sys.argv) < 2:
        print("Usage: %s <redo/reproduce> <table/figure name>" % sys.argv[0])
        exit(1)

    check_cpu_count()

    # Read action
    action = sys.argv[1]
    if action not in ["redo", "reproduce"]:
        print("Invalid action! Choose from [redo, reproduce]" )
        exit(1)

    # Read target
    target = sys.argv[2]
    if target not in ["table3", "table4", "table5", "table6", "table7", "table8", "table9",
                      "figure6", "figure7"]:
        print("Invalid target! \n \
               Choose from [table3, table4, table5, table6, table7, table8, table9, figure6, figure7]")
    
    target_list = []
    tools = []
    
    benchmark = SUB_TARGETS[target]
    target_list = [x for (x,y,z,w) in SUB_TARGETS[target]]

    # Set tools to run according to target
    if target == "table4":
        tools = ["Beacon", "WindRanger", "SelectFuzz", "DAFL" ]
    elif target == "table8":
        tools = ["AFLGo", "Beacon"]
    elif target == "figure7":
        tools = ["AFLGo", "DAFL"]
    else:
        tools = ["AFLGo", "Beacon", "WindRanger", "SelectFuzz", "DAFL" ]


    # Set output directory
    if action == "reproduce":
        outdir = decide_outdir(True, target, "")
    else:
        outdir = decide_outdir(False, target, "")


    ## If redoing from scratch, Run Fuzzing, Replay the found crashes, and Triage them first.
    if action == "redo":
        ### 1. Run fuzzing     
        timelimit = TIMEOUTS[target]
        iteration = 160
        for tool in tools:
            worklist = generate_fuzzing_worklist(benchmark, iteration)
            outdir = decide_outdir(False, target, tool)
            while len(worklist) > 0:
                works = fetch_works(worklist)
                spawn_containers(works)
                run_fuzzing(works, tool, timelimit)
                wait_finish(works, timelimit)
                store_outputs(works, outdir)
                cleanup_containers(works)

        ### 2. Replay crashes
        replayed_dir = replay_target(outdir, target, tools)

    

    if "origin" in sys.argv[2]:
        outdir = decide_outdir("origin", "", "", "")
    else:
        outdir = decide_outdir(target, str(timelimit), str(iteration), "")
    
    ### 2. Replay crashes
    replayed_dir = replay(outdir, target, target_list, tools)

    ### 3. Parse and print results in CSV format
    print_result(outdir, target, target_list, timelimit, iteration, tools)

    ### 4. Draw chart from CSV file
    draw_result(outdir, target)


if __name__ == "__main__":
    main()

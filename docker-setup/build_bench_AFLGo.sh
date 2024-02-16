#!/bin/bash

. $(dirname $0)/build_bench_common.sh

# arg1 : Target project
# arg2~: Fuzzing targets
function build_with_AFLGo() {
    for TARG in "${@:2}"; do
        str_array=($TARG)
        BIN_NAME=${str_array[0]}

        cd /benchmark
        CC="/fuzzer/AFLGo/afl-clang-fast"
        CXX="/fuzzer/AFLGo/afl-clang-fast++"
        TMP_DIR=/benchmark/temp_$1

        for BUG_NAME in "${str_array[@]:1}"; do
            ### Draw CFG and CG with BBtargets
            mkdir -p $TMP_DIR
            
            cp /benchmark/target/line/$BIN_NAME/$BUG_NAME $TMP_DIR/BBtargets.txt

            ADDITIONAL="-targets=$TMP_DIR/BBtargets.txt \
                        -outdir=$TMP_DIR -flto -fuse-ld=gold \
                        -Wl,-plugin-opt=save-temps"
            build_target $1 $CC $CXX "$ADDITIONAL"
            # find /benchmark/RUNDIR-$1 -name "config.cache" -exec rm -rf {} \;

            cat $TMP_DIR/BBnames.txt | rev | cut -d: -f2- | rev | sort | uniq > $TMP_DIR/BBnames2.txt \
            && mv $TMP_DIR/BBnames2.txt $TMP_DIR/BBnames.txt
            cat $TMP_DIR/BBcalls.txt | sort | uniq > $TMP_DIR/BBcalls2.txt \
            && mv $TMP_DIR/BBcalls2.txt $TMP_DIR/BBcalls.txt

            ### Compute Distances based on the graphs
            cd /benchmark/RUNDIR-$1
            /fuzzer/AFLGo/scripts/genDistance.sh $PWD $TMP_DIR $BIN_NAME

            ### Build with distance info, with ASAN disabled
            cd /benchmark
            rm -rf /benchmark/RUNDIR-$1
            build_target $1 $CC $CXX "-distance=$TMP_DIR/distance.cfg.txt"

            ### copy results
            copy_build_result $1 $BIN_NAME $BUG_NAME "AFLGo"
            rm -rf /benchmark/RUNDIR-$1

            ### Cleanup
            rm -rf $TMP_DIR
        done
    done
}

# Build with AFLGo
mkdir -p /benchmark/bin/AFLGo
build_with_AFLGo "libming-4.7" \
    "swftophp 2016-9827 2016-9829 2016-9831 2017-9988 2017-11728 2017-11729" &
build_with_AFLGo "binutils-2.26" \
    "cxxfilt 2016-4489 2016-4490 2016-4491 2016-4492 2016-6131 \
             2016-4492-crash2" &

wait

cp /benchmark/bin/AFLGo/cxxfilt-2016-4492 /benchmark/bin/AFLGo/cxxfilt-2016-4492-crash1
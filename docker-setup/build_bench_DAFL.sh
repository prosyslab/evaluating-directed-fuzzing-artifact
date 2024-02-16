#!/bin/bash

. $(dirname $0)/build_bench_common.sh

# arg1 : Target project
# arg2~: Fuzzing targets
function build_with_DAFL() {

    for TARG in "${@:2}"; do
        str_array=($TARG)
        BIN_NAME=${str_array[0]}

        # Run Sparrow per target binary.
        python3 /benchmark/scripts/run_sparrow.py $BIN_NAME

        cd /benchmark
        CC="/fuzzer/DAFL/afl-clang-fast"
        CXX="/fuzzer/DAFL/afl-clang-fast++"
        
        for BUG_NAME in "${str_array[@]:1}"; do
            export DAFL_SELECTIVE_COV="/benchmark/DAFL-input/inst-targ/$BIN_NAME/$BUG_NAME"
            export DAFL_DFG_SCORE="/benchmark/DAFL-input/dfg/$BIN_NAME/$BUG_NAME"
            
            # Build with ASAN disabled.
            build_target $1 $CC $CXX " "
            copy_build_result $1 $BIN_NAME $BUG_NAME "DAFL"
            rm -rf RUNDIR-$1
        done

    done

}

# Build with DAFL
mkdir -p /benchmark/build_log
mkdir -p /benchmark/bin/DAFL
build_with_DAFL "libming-4.7" \
    "swftophp 2016-9827 2016-9829 2016-9831 2017-9988 2017-11728 2017-11729"
build_with_DAFL "binutils-2.26" \
    "cxxfilt 2016-4487 2016-4489 2016-4490 2016-4491 2016-4492 2016-6131 \
             2016-4489-crash 2016-4492-crash2"

# Copy duplicates
cp /benchmark/bin/DAFL/cxxfilt-2016-4489 /benchmark/bin/DAFL/cxxfilt-2016-4489-caller
cp /benchmark/bin/DAFL/cxxfilt-2016-4492 /benchmark/bin/DAFL/cxxfilt-2016-4492-crash1
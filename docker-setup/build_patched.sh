#!/bin/bash

. $(dirname $0)/build_bench_common.sh

# arg1 : build target name
# arg2 : string for CC
# arg3 : string for CXX
# arg4 : additional string for CFLAGS (optional)
# arg5 : patch version
function build_patched_target() {
    # Strangely, some C programs use CXX for compiler. So set CXX* vars, too.
    export CC=$2
    export CXX=$3
    export CFLAGS="$DEFAULT_FLAGS $4"
    export CXXFLAGS="$DEFAULT_FLAGS $4"
    #while true; do
    #    /benchmark/project/build-target.sh $1 || continue
    #    break
    #done
    # Do not run in loop until our initial integration is completed.
    /benchmark/triage/build_target_patched.sh $1 $5
}

# arg1 : Target project
# arg2~: Fuzzing targets
function build_patched() {
    for TARG in "${@:2}"; do
        str_array=($TARG)
        BIN_NAME=${str_array[0]}
        for BUG_NAME in "${str_array[@]:1}"; do
            build_patched_target $1 "clang" "clang++" "$ASAN_FLAGS" "$BUG_NAME"
            copy_build_result $1 $BIN_NAME $BUG_NAME "patched"
            rm -rf RUNDIR-$1 || exit 1
        done
    done
}

# Build patched binary
mkdir -p /benchmark/bin/patched
build_patched "libming-4.7" \
    "swftophp 2016-9827 2016-9829 2016-9831 2017-9988 2017-11728 2017-11729"
build_patched "binutils-2.26" \
    "cxxfilt 2016-4487 2016-4489 2016-4490 2016-4491-a 2016-4491-b 2016-4492 2016-6131"

# Make duplicates
cp /benchmark/bin/patched/cxxfilt-2016-4489 /benchmark/bin/patched/cxxfilt-2016-4489-crash
cp /benchmark/bin/patched/cxxfilt-2016-4489 /benchmark/bin/patched/cxxfilt-2016-4489-caller
cp /benchmark/bin/patched/cxxfilt-2016-4492 /benchmark/bin/patched/cxxfilt-2016-4492-crash1
cp /benchmark/bin/patched/cxxfilt-2016-4492 /benchmark/bin/patched/cxxfilt-2016-4492-crash2

# Set default binary for cxxfilt-2016-4491
cp /benchmark/bin/patched/cxxfilt-2016-4491-b /benchmark/bin/patched/cxxfilt-2016-4491
#!/bin/bash

. $(dirname $0)/build_bench_common.sh

# arg1 : Binary name
# arg2 : Bug name
# arg3 : Bit option
# arg4 : Compiler
# arg5 : Compile Options
function parallel_build() {
    BIN_NAME=$1
    BUG_NAME=$2
    COMP=$3
    COMPILE_OPT=$4

    mkdir outputs_$BUG_NAME
    cd outputs_$BUG_NAME

    /fuzzer/Beacon/precondInfer ../$BIN_NAME.bc --target-file=/benchmark/target/line/$BIN_NAME/$BUG_NAME --join-bound=5 >precond_log 2>&1
    /fuzzer/Beacon/Ins -output=../$BIN_NAME-$BUG_NAME.bc -byte -blocks=bbreaches__benchmark_target_line_${BIN_NAME}_${BUG_NAME} -afl -log=log.txt -load=./range_res.txt ./transed.bc

    $COMP ../$BIN_NAME-$BUG_NAME.bc -o ../$BIN_NAME-$BUG_NAME $COMPILE_OPT /fuzzer/Beacon/afl-llvm-rt.o

    cp ../$BIN_NAME-$BUG_NAME /benchmark/bin/Beacon/$BIN_NAME-$BUG_NAME || exit 1
    cd ..
    rm -r outputs_$BUG_NAME


}

# arg1 : Target project
# arg2 : Compiler to use for the final build.
# arg3 : Additional compiler options (e.g. LDFLAGS) for the final build.
# arg4 : Path to the bytecode
# arg5~: Fuzzing targets
function build_with_Beacon() {

    for TARG in "${@:5}"; do
        str_array=($TARG)
        BIN_NAME=${str_array[0]}
        
        arr=(${BIN_NAME//-/ })
        SIMPLE_BIN_NAME=${arr[0]}

        cd /benchmark
        CC="clang"
        CXX="clang++"
        ADDITIONAL="-flto -fuse-ld=gold -Wl,-plugin-opt=save-temps"
        build_target $1 $CC $CXX "$ADDITIONAL"
        
        cd RUNDIR-$1
        cp $4/$SIMPLE_BIN_NAME.0.0.preopt.bc $BIN_NAME.bc || exit 1
        
        for BUG_NAME in "${str_array[@]:1}"; do
            parallel_build $BIN_NAME $BUG_NAME $2 "$3" &
        done
        wait
        cd ..

        rm -rf RUNDIR-$1
    done

}

export PATH=/fuzzer/Beacon/llvm4/bin:$PATH
export PATH=/fuzzer/Beacon/llvm4/lib:$PATH

# Build with Beacon
mkdir -p /benchmark/bin/Beacon
build_with_Beacon "libming-4.7" "clang" "-lm -lz" "BUILD/util" \
    "swftophp 2016-9827 2016-9829 2016-9831 2017-9988 2017-11728 2017-11729" &
build_with_Beacon "binutils-2.26" "clang" "-ldl" "binutils-2.26/binutils" \
    "cxxfilt 2016-4487 2016-4489 2016-4490 2016-4491 2016-4492 2016-6131 \
             2016-4489-crash 2016-4492-crash2" &

wait

# Make duplicates
cp /benchmark/bin/Beacon/cxxfilt-2016-4489 /benchmark/bin/Beacon/cxxfilt-2016-4489-caller
cp /benchmark/bin/Beacon/cxxfilt-2016-4492 /benchmark/bin/Beacon/cxxfilt-2016-4492-crash1
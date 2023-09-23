#!/bin/bash

FUZZER_NAME='SelectFuzz'
. $(dirname $0)/common-setup.sh

# Set exploitation time as 7/8 of 24 hours.
# timeout $4 /fuzzer/SelectFuzz/afl-fuzz \
#   $DICT_OPT -m none -d -z exp -c 21h -i seed -o output -- ./$1 $2
timeout $4 /fuzzer/SelectFuzz/afl-fuzz \
  $DICT_OPT -m none -d -i seed -o output -- ./$1 $2


. $(dirname $0)/common-postproc.sh

#!/bin/bash

# First, run smake on all projects to generate preprocessed files.
cd /
git clone https://github.com/prosyslab/smake.git smake
cd smake
git checkout 4820d08fc1e43555c2be842984d9a7043d42d07b

cd /benchmark
. $(dirname $0)/build_bench_common.sh
mkdir -p /benchmark/smake-out

### Program: libming-4.7
cd /benchmark
build_target libming-4.7 clang clang++ " "
cd /benchmark/RUNDIR-libming-4.7/BUILD
make clean
yes | /smake/smake --init
/smake/smake -j 1
cp -r sparrow/util/swftophp /benchmark/smake-out/swftophp || exit 1


### Program: binutils-2.26
cd /benchmark
build_target binutils-2.26 clang clang++ " "
cd /benchmark/RUNDIR-binutils-2.26/binutils-2.26
make clean
yes | /smake/smake --init
/smake/smake -j 1
cp -r sparrow/binutils/cxxfilt /benchmark/smake-out/cxxfilt || exit 1


# Then, setup Sparrow
cd /
git clone https://github.com/prosyslab/sparrow.git

cd /sparrow
git checkout dafl
export OPAMYES=1

apt-get update
apt-get install -y opam libclang-cpp12-dev libgmp-dev libclang-12-dev llvm-12-dev libmpfr-dev

sed -i '/^opam init/ s/$/ --disable-sandboxing/' build.sh
./build.sh
opam install ppx_compare yojson ocamlgraph memtrace lymp clangml conf-libclang.12 batteries apron conf-mpfr cil linenoise claml

eval $(opam env)
make clean
make


# Finally, build DAFL
cd /fuzzer
git clone https://github.com/prosyslab/DAFL.git DAFL || exit 1
cd DAFL && make && cd llvm_mode && make

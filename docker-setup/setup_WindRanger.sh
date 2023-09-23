#!/bin/bash

# unzip WindRanger
cd /fuzzer
tar -xzf /fuzzer/windranger.tar.gz
rm /fuzzer/windranger.tar.gz
mv windranger WindRanger

## install required llvm
cd /fuzzer/WindRanger

wget https://github.com/llvm/llvm-project/releases/download/llvmorg-10.0.0/clang+llvm-10.0.0-x86_64-linux-gnu-ubuntu-18.04.tar.xz || exit 1
tar -C /fuzzer/WindRanger -xf clang+llvm-10.0.0-x86_64-linux-gnu-ubuntu-18.04.tar.xz
rm clang+llvm-10.0.0-x86_64-linux-gnu-ubuntu-18.04.tar.xz
mv /fuzzer/WindRanger/clang+llvm-10.0.0-x86_64-linux-gnu-ubuntu-18.04 /fuzzer/WindRanger/clang+llvm


## install wclang and gclang
if ! [ -x "$(command -v wllvm)"  ]; then
    pip3 install --upgrade pip==9.0.3
    pip3 install wllvm
    export LLVM_COMPILER=clang
fi
if ! [ -x "$(command -v gclang)"  ]; then
    mkdir /root/go
    go get github.com/SRI-CSL/gllvm/cmd/...
    cd /root/go/src/github.com/SRI-CSL/gllvm/
    git checkout v1.3.0
    cd -
    go get github.com/SRI-CSL/gllvm/cmd/...
    export PATH=/root/go/bin:$PATH
fi
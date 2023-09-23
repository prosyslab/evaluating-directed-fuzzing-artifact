FROM ubuntu:20.04
ENV DEBIAN_FRONTEND noninteractive

# (Temporary: replace URL for fast download during development)
RUN sed -i 's/archive.ubuntu.com/ftp.daumkakao.com/g' /etc/apt/sources.list

ENV DEBIAN_FRONTEND="noninteractive"
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -yy libc6-dev binutils libgcc-9-dev
RUN apt-get install -yy \
      wget apt-transport-https git unzip \
      build-essential libtool libtool-bin gdb \
      automake autoconf bison flex python python3 sudo vim

# Copied from OSS-FUZZ
ENV OUT=/out
ENV SRC=/src
ENV WORK=/work
ENV PATH="$PATH:/out"
RUN mkdir -p $OUT $SRC $WORK
ENV CMAKE_VERSION 3.21.1
RUN wget https://github.com/Kitware/CMake/releases/download/v$CMAKE_VERSION/cmake-$CMAKE_VERSION-Linux-x86_64.sh && \
    chmod +x cmake-$CMAKE_VERSION-Linux-x86_64.sh && \
    ./cmake-$CMAKE_VERSION-Linux-x86_64.sh --skip-license --prefix="/usr/local" && \
    rm cmake-$CMAKE_VERSION-Linux-x86_64.sh && \
    rm -rf /usr/local/doc/cmake /usr/local/bin/cmake-gui
COPY docker-setup/checkout_build_install_llvm.sh /root/
RUN /root/checkout_build_install_llvm.sh
RUN rm /root/checkout_build_install_llvm.sh

# Install packages needed for fuzzers and benchmark
RUN apt-get update && \
    apt-get install -yy \
      # Several packages get uninstalled after LLVM setup.
      git build-essential bc \
      # For ParmeSan
      golang \
      # For Beacon
      libncurses5 \
      # For libming
      libfreetype6 libfreetype6-dev \
      # For libxml
      python-dev \
      # For libjpeg
      nasm \
      # For lrzip
      libbz2-dev liblzo2-dev

# Create a benchmark directory setup basic stuff.
RUN mkdir -p /benchmark/bin && \
    mkdir -p /benchmark/seed && \
    mkdir -p /benchmark/runtime && \
    mkdir -p /benchmark/poc &&\
    mkdir -p /benchmark/dict
COPY docker-setup/seed/empty /benchmark/seed/empty
ENV ASAN_OPTIONS=allocator_may_return_null=1,detect_leaks=0
WORKDIR /benchmark

# To use ASAN during the benchmark build, these option are needed.
ENV ASAN_OPTIONS=allocator_may_return_null=1,detect_leaks=0

COPY docker-setup/benchmark-project /benchmark/project
COPY docker-setup/target/line /benchmark/target/line
COPY docker-setup/build_bench_common.sh /benchmark/build_bench_common.sh


# Create a fuzzer directory and setup fuzzers there.
RUN mkdir /fuzzer
WORKDIR /fuzzer

# Setup AFLGo.
COPY docker-setup/setup_AFLGo.sh /fuzzer/setup_AFLGo.sh
RUN ./setup_AFLGo.sh

# Setup Beacon.
COPY docker-setup/pre-builts/Beacon /fuzzer/Beacon
COPY docker-setup/setup_Beacon.sh /fuzzer/setup_Beacon.sh
RUN ./setup_Beacon.sh

# Setup WindRanger.
COPY docker-setup/pre-builts/WindRanger/windranger.tar.gz /fuzzer/windranger.tar.gz
COPY docker-setup/setup_WindRanger.sh /fuzzer/setup_WindRanger.sh
RUN ./setup_WindRanger.sh

# Setup SelectFuzz.
COPY docker-setup/pre-builts/SelectFuzz/SelectFuzz.tar.gz /fuzzer/SelectFuzz.tar.gz
COPY docker-setup/setup_SelectFuzz.sh /fuzzer/setup_SelectFuzz.sh
RUN ./setup_SelectFuzz.sh

# Setup DAFL.
COPY docker-setup/setup_DAFL.sh /fuzzer/setup_DAFL.sh
RUN ./setup_DAFL.sh


# Reset the working directory to start building benchmarks.
WORKDIR /benchmark

# Build benchmarks with ASAN.
COPY docker-setup/build_bench_ASAN.sh /benchmark/build_bench_ASAN.sh
RUN ./build_bench_ASAN.sh

# Build benchmarks with AFLGo.
COPY docker-setup/build_bench_AFLGo.sh /benchmark/build_bench_AFLGo.sh
RUN ./build_bench_AFLGo.sh

# Build benchmarks with Beacon.
COPY docker-setup/build_bench_Beacon.sh /benchmark/build_bench_Beacon.sh
RUN ./build_bench_Beacon.sh

# Build benchmarks with WindRanger.
COPY docker-setup/build_bench_WindRanger.sh /benchmark/build_bench_WindRanger.sh
RUN ./build_bench_WindRanger.sh

# Build benchmarks with SelectFuzz.
COPY docker-setup/build_bench_SelectFuzz.sh /benchmark/build_bench_SelectFuzz.sh
RUN ./build_bench_SelectFuzz.sh

# Build benchmarks with DAFL.
COPY scripts /benchmark/scripts
COPY docker-setup/build_bench_DAFL.sh /benchmark/build_bench_DAFL.sh
RUN ./build_bench_DAFL.sh

# Build patched binaries
COPY docker-setup/triage /benchmark/triage
COPY docker-setup/build_patched.sh /benchmark/build_patched.sh
RUN ./build_patched.sh

# Copy tool running scripts.
COPY docker-setup/tool-script /tool-script

# Reset the working directory to top-level directory.
WORKDIR /

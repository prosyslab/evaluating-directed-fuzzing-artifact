# Evaluating Directed Fuzzers: Are We Heading in the Right Direction? (Paper Artifact)

This is the artifact of the paper *Evaluating Directed Fuzzers: Are We Heading in the Right Direction?* submitted to FSE 2024.

## __1. Getting started__
### __1.1. System requirements__
To run the experiments in the paper, we used a 64-core (Intel Xeon Processor Gold 6226R, 2.90 GHz) machine
with 192 GB of RAM and Ubuntu 20.04. Out of 64 cores, We utilized 40 cores with 4 GB of RAM assigned for each core.

The system requirements depend on the desired experimental throughput.
For example, if you want to run 10 fuzzing sessions in parallel,
we recommend using a machine with at least 16 cores and 64 GB of RAM.

You can set the number of iterations to be run in parallel and the amount of RAM to assign to each fuzzing session
by modifying the `MAX_INSTANCE_NUM` and `MEM_PER_INSTANCE` variables in `scripts/common.py`.
The default values are 40 and 4, respectively.

Additionally, we assume that the following environment settings are met.
- Ubuntu 20.04
- Docker
- python 3.8+
- pip3

For the Python dependencies required to run the experiment scripts, run
```
yes | pip3 install -r requirements.txt
```

&nbsp;

### __1.2. System configuration__

To run AFL-based fuzzers, you should first fix the core dump name pattern.
```
$ echo core | sudo tee /proc/sys/kernel/core_pattern
```

If your system has `/sys/devices/system/cpu/cpu*/cpufreq` directory, AFL may
also complain about the CPU frequency scaling configuration. Check the current
configuration and remember it if you want to restore it later. Then, set it to
`performance`, as requested by AFL.
```
$ cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
powersave
powersave
powersave
powersave
$ echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

&nbsp;

### __1.3. Preparing the Docker image__

**Notice:** If you only want to reuse the raw data and reproduce the results in the paper, you can skip this section.

Our artifact is composed of two parts: the Docker image and the framework to build and utilize it.
The Docker image contains all the necessary tools and dependencies to run the fuzzing experiments.
The framework, which holds this README file, is used to build the Docker image and orchestrate the fuzzing experiments.

You can build the docker image yourself. Run
```
./build.sh
```
It will take up to 6 hours to build.

&nbsp;

## 2. __Directory structure__


### __2.1. Local framework structure__

```
├─ README.md                     <- The top-level README (this file)
│  │ 
├─ docker-setup                  <- All scripts and data required to build the Docker image
│  │
│  ├─ benchmark-project          <- Directory to build each benchmark project-wise
│  │  ├─ binutils-2.26
│  │  │  ├─ poc                  <- POC files for each target in binutils-2.26
│  │  │  └─ build.sh             <- The build script to build binutils-2.26
│  │  ├─ ...
│  │  │
│  │  └─ build-target.sh         <- A wrapper script to build each benchmark project
│  │
│  ├─ target                     <- Target program locations for each target
│  │  └─ line                    <- Target lines
│  │
│  ├─ pre-builts                 <- Directory for pre-built binaries of baseline fuzzers
│  │  ├─ Beacon                  <- Binaries extracted from the provided Docker image
│  │  │                             (yguoaz/beacon: Docker SHA256 hash a09c8cb)
│  │  ├─ WindRanger              <- Implementation of WindRanger extracted from the provided Docker image
│  │  │                             (ardu/windranger: Docker SHA256 hash 8614ceb)
│  │  └─ SelectFuzz              <- Implementation of SelectFuzz (commit 9dea54f) built in the provided Docker image
│  │                                (selectivefuzz1/selectfuzz: Docker SHA256 hash 3bc05ff)
│  │
│  ├─ triage                     <- The patches we used for patch-based triage
│  │
│  ├─ tool-script                <- Directory for fuzzing scripts
│  │  └─ run_*.sh                <- The fuzzing scripts to run each fuzzing tool
│  │
│  ├─ setup_*.sh                 <- The setup scripts to setup each fuzzing tool
│  └─ build_bench_*.sh           <- The build scripts to build the target programs
│
│
├─ scripts                       <- Directory for scripts
│
├─ output                        <- Directory where outputs are stored
│
├─ scripts                       <- Directory for scripts
│
├─ Dockerfile                    <- Docker file used to build the Docker image
│
├─ sa_overhead.csv               <- Static analysis overheads for each tool
│
└─ requirements.txt              <- Python requirements for the scripts
```


### __2.2. Docker directory structure__

```
├─ benchmark                     <- Directory for benchmark data
│  │
│  ├─ bin                        <- Target binaries built for each fuzzing tool
│  │  ├─ AFL
│  │  ├─ ...
│  │
│  ├─ target                     <- Target program locations for each target
│  │  └─ line                    <- Target lines
│  │
│  │
│  ├─ poc                        <- Proof of concept inputs for each target
│  │
│  ├─ seed                       <- Seed inputs for each target
│  │
│  └─ build_bench_*.sh           <- The build scripts to build the target programs
│                                   for each fuzzing tool
│
├─ fuzzer                        <- Directory for fuzzing tools
│  ├─ AFL                        <- The initial rule used for
│  ├─ ...
│  └─ setup_*.sh                 <- The setup scripts to setup each fuzzing tool
│
└─ tool-script                   <- Directory for fuzzing scripts
   └─ run_*.sh                   <- The fuzzing scripts to run each fuzzing tool
```


## 3. __Reproducing the results in the paper__

In this version of the artifact, we provide the raw data of the experiments in the paper under the directory `output`.
Each table or figure has its own directory, and the relevant data is stored under the directory.

We also provide a Python script to reproduce the tables and figures as exactly in the paper.
You can simply run
```
$ python3 ./scripts/reproduce.py [target]
```
Note that`[target]` can be one of the following: `table3`, `table4`, `table5`, `table6`, `table8`, `table9`, `figure6`, `figure7`.
We do not support `table7` because `sa_overhead.csv` file is equivalent to the table.
The result, whether in CSV or PDF format, will be stored under the corresponding output directory.


Each table or figure would take a few minutes to reproduce, except for Table 9, which takes about 30 minutes.

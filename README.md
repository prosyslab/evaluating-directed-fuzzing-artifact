# Evaluating Directed Fuzzers: Are We Heading in the Right Direction? (Paper Artifact)

This is the artifact of the paper *Evaluating Directed Fuzzers: Are We Heading in the Right Direction?* to appear in FSE 2024.

The following contents subsumes the contents in `INSTALL` and `REQUIREMENTS` files. Thus, if carefully read, reading this document is sufficient to understand everything about the artifact.

## 0. __Step for Zenodo Only__
Download the file `evaluating-directed-fuzzing-artifact.tar.gz` and extract the contents.
```
tar -zxf evaluating-directed-fuzzing-artifact.tar.gz
```
If you wish to use the most recent version of the artifact, please visit [GitHub](https://github.com/prosyslab/evaluating-directed-fuzzing-artifact) where the artifact is maintained.

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
- available disk space of at least 25 GB

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
Our artifact is composed of two parts: the Docker image and the framework to build and utilize it.
The Docker image contains all the necessary tools and dependencies to run the fuzzing experiments.
The framework, which holds this README file, is used to build the Docker image and orchestrate the fuzzing experiments.

**Recommended**
You can pull the pre-built Docker image from Dockerhub.

To do so, run
```
$ docker pull prosyslab/directed-fuzzing-benchmark
```
The image is big (around 25 GB) and it may take a while to download.

#### __DIY__
If you want to build the docker image yourself, run
```
$ docker build -t prosyslab/directed-fuzzing-benchmark -f Dockerfile .
```

or simply run

```
$ ./build.sh
```

However, we do not recommend this because it will take a long time (up to 6 hours, perhapse more depending on your system) to build.
Nonetheless, we provide the Docker file and the relevant scripts to show how the Docker image was built.

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
│  │  ├─ AFLGo
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
│  ├─ AFLGo                      <- Each fuzzing tool
│  ├─ ...
│  └─ setup_*.sh                 <- The setup scripts to setup each fuzzing tool
│
└─ tool-script                   <- Directory for fuzzing scripts
   └─ run_*.sh                   <- The fuzzing scripts to run each fuzzing tool
```



&nbsp;

## 3. __Running the experiments__

### __3.0. Testing the environment__

Run the following command to check if your environment is ready for the experiment.
```
$ python3 ./scripts/reproduce.py run cxxfilt-2016-4487 60 40 "AFLGo WindRanger Beacon SelectFuzz DAFL"
```
This will run the experiment for 60 seconds with 40 iterations for the target `cxxfilt-2016-4490` using the tools `AFLGo`, `WindRanger`, `Beacon`, `SelectFuzz`, and `DAFL`.
If you are using 40 cores in parallel, the experiment will take approximately 15 minutes to complete.
As a result, you will see a table with the results of the experiment (`output/cxxfilt-2016-4490/cxxfilt-2016-4490.csv`)



### __3.1. Running the experiments for each table and figure__

We provide a predefined set of scaled down versions of the experiments in the paper.
In order to provide a reasonable runtime for the artifact, we reduced the number of iterations and the time limit for each experiment.
Thus, the results may not be exactly the same as in the paper, but they should still be able to demonstrate the main findings.
For more information, check out the `EXP_ENV` dictionary in `scripts/benchmark.py`. You can uniformaly set the `TIMELIMITS` to `86400` and `ITERATIONS` to `160` for the full-scale experiments.

Each table and figure in the paper can be reproduced with the script `scripts/reproduce.py` as the following.
```
$ python3 ./scripts/reproduce.py run [table/figure]
```

Here is a brief overview on what happens when you run the command.
1) First, the corresponding fuzzing experiment will be run. The raw fuzzing data are saved under `output/data`.
2) Second, the crashing inputs will be replayed against the patched binary in order to triage the crashes (see Section 5 in the paper).
3) Finally, the result will be summarized in a CSV file, `[table/figure].csv`, under the corresponding output directory, `output/[table/figure]`.
4) If the target is a figure, both a csv file and a figure will be generated.

Here are the supported predefined targets. Note that we do not support Table 7 because `sa_overhead.csv` file is equivalent to the table.
- Table 3 (`table3`)
   - Expected duration: 14 hours
   - Expected output: `output/table3/table3.csv`, corresponding to Table 3 in the paper.
- Table 4 (`table4`)
   - Expected duration: 2 hours
   - Expected output: `output/table4/table4.csv`, corresponding to Table 4 in the paper.
- Table 5 (`table5`)
   - Expected duration: 7 hours
   - Expected output: `output/table5/table5.csv`, corresponding to Table 5 in the paper.
- Table 6 (`table6`)
   - Expected duration: 60 hours
   - Expected output: `output/table6/table6.csv`, corresponding to Table 6 in the paper.
- Table 8 (`table8`)
   - Expected duration: 1 hour
   - Expected output: `output/table8/table8.csv`, corresponding to Table 8 in the paper.
- Table 9 (`table9`)
   - Expected duration: 60 days
   - Expected output: `output/table9/table9.csv`, corresponding to Table 9 in the paper.
- Minimal version of Table 9 (`table9-minimal`)
   - Table 9 is a large-scale experiment and takes a long time to complete even with reduced iterations and time limit. Thus, we provide a minimal version of Table 9 to reduce the runtime to a reasonable level.
   We restrict the target to `cxxfilt-2016-4492` which is suitable to illustrate the original message of Table 9, that is, the intense randomness in directed fuzzing. The median TTE and the maximum TTE of each tool will reveal the randomness in directed fuzzing.
   - Expected duration: 60 hours
   - Expected output: `output/table9-minimal/table9-minimal.csv`, corresponding to the minimal version of Table 9 in the paper.
- Figure 6 (`figure6`)
   - Expected duration: 6 hours
   - Expected output: `output/figure6/figure6.csv` and `output/figure6/figure6.pdf`, corresponding to Figure 6 in the paper.
- Figure 7 (`figure7`)
   - Expected duration: 33 hours
   - Expected output: `output/figure7/figure7.csv` and `output/figure7/figure7.pdf`, corresponding to Figure 7 in the paper.


If you run the minimal version of Table 9, all experiment should take about 7 and a half day to complete in total. Note that the expected duration is calculated based on the assumption that 40 fuzzing sessions are run in parallel.


&nbsp;

### __3.2. Drawing tables and figure from data__
If you have already run the experiements and have the raw data, you can draw the tables and figures using the following command.
```
$ python3 ./scripts/reproduce.py draw [table/figure]
```
Note that the `run` command subsumes the `draw` command, so you do not need to run the `draw` command separately after running the `run` command.

&nbsp;

### __3.3. Reproduce the exact results in the paper__ ###
You can also reproduce the exact results in the paper.

First, retrieve the raw data from [here](https://zenodo.org/doi/10.5281/zenodo.8373765).
Download the file `original_data.tar.gz`, extract the files, and move them to the appropriate
location with the following commands.

```
## wget or download the archived file
$ tar -xvf original_data.tar.gz
$ mkdir output
$ mv original_data output
```
Note that the size of the file after extraction is about 152GB, so be sure to have enough storage space.

Now you can use the command `draw-original` to get the same results as in the paper.
```
$ python3 ./scripts/reproduce.py draw-original [figure/table]
```

&nbsp;

### __3.4. Running the experiment on specific targets__

We provide the option to run the experiment on specific targets.
For example, to run the experiment on CVE-2016-4487 in cxxfilt, run
```
$ python3 ./scripts/reproduce.py run cxxfilt-2016-4487
```
Check out the list of available targets from the dictionary `FUZZ_TARGETS` in `scripts/benchmark.py`.

The default experiment settings are 86400 seconds(24 hours) and 160 iterations with all the available tools.
You may adjust them by providing the desired setting as the following.
```
$ python3 ./scripts/reproduce.py [run/draw] [target] [timelimit] [iterations] "[tool list]"
```
For example,
```
$ python3 ./scripts/reproduce.py run cxxfilt-2016-4487 3600 40 "AFLGo WindRanger Beacon SelectFuzz DAFL"
```
Or you can modify the values associated with the key `custom` in `EXP_ENV` dictionary in `scripts/benchmark.py`.

For the experiement with specific targets, a simple table with the results of the experiment will be produced as an
output.


&nbsp;

### __3.5. Tips__

- There is a hidden command `replay`. You may use this command when the fuzzing step was successfull, but steps after the replay goes wrong. This command will resume your experiment from step 2 described in Section 3.1 of this document.
- After launching the experiment, you better check if the fuzzing is running properly with `htop`. Since we fully assign a core to each Docker container, you should see 100% utilization of the number of cores corresponding to the parallel fuzzing sessions.
- If fuzzing is not running, check section 1.2 of this document to see if your system is properly configured.
- If you have terminated the experiment, for example, by pressing `Ctrl+C`, you may need to clean up the Docker containers before running next experiment. This is because the name of the Docker container is fixed and the new experiment will fail if the old containers are still running. You can clean up the containers by running `docker kill $(docker ps -q)`. Note that this will kill all the running containers, so be careful when running this command.
- New results (ex. cxxfilt-2016-4487-AFLGo) will overwrite the old results in `output/data`. If you want to keep the old results, you should make a backup.


&nbsp;

### __4. Expanding the artifact__

#### __4.1. Adding new targets__
You can add new targets to the artifact by following the steps below.

1. Add the target program to the `docker-setup/benchmark-project` directory.
- `build.sh` to build the project that contains the target program and `seeds` directory to store the seed inputs for the target program is required. `poc` directory to store the proof of concept inputs is optional.
- FYI, the structure of `docker-setup/benchmark-project` is similar to Google's [Fuzzer Test Suite](https://github.com/google/fuzzer-test-suite).

2. Add necessary target information.
- Add the target line information to `docker-setup/target/line`.
- Add a asan-based triage logic to `scripts/triage.py`.
- Add a patch to `docker-setup/triage` for patch-based triage.

3. Add target to build scripts.
- To build script for each fuzzing tool in `docker-setup/build_bench_*.sh`.
- To build script for the patched binaries `docker-setup/build_patched.sh`.
- For DAFL, you need to support target in `docker-setup/setup_DAFL.sh`.

4. Rebuild the Docker image. This step is necessary because the Docker image must contain all the target binaries to run the experiments.

5. Add the target to experiment scripts
- To the dictionary `FUZZ_TARGETS` and `SLICE_TARGETS` in `scripts/benchmark.py`.

6. Add the static analysis overhead to `sa_overhead.csv`.


#### __4.2. Adding new fuzzing tools__
You can add new fuzzing tools to the artifact by following the steps below.

1. Write a setup script for the new fuzzing tool in `docker-setup` with the name `setup_*.sh`.

2. Write a build script for the new fuzzing tool in `docker-setup` with the name `build_bench_*.sh`.

3. Write a run script for the new fuzzing tool in `docker-setup/tool-script` with the name `run_*.sh`.

4. Add lines in the Docker script to install the new fuzzing tool.

5. Add the new fuzzing tool to the dictionary `SUPPORTED_TOOLS` in `scripts/reproduce.py`.



&nbsp;

### __5. Citation__
If you use this artifact in scientific work, please cite our work as follows.

```bibtex
@MISC{kim:fse-artifact:2024,
  author = {Tae Eun Kim and Jaeseung Choi and Seongjae Im and Kihong Heo and Sang Kil Cha},
  title = {Reproduction Package for the FSE 2024 Article `Evaluating Directed Fuzzers: Are We Heading in the Right Direction?'},
  howpublished = {\url{https://doi.org/10.5281/zenodo.10669580}},
  year=2024
}
```



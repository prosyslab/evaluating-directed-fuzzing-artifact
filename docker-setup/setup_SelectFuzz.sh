#!/bin/bash

# We could not build SelectFuzz in our environment.
# Therefore, we clone the 9dea54fc999f7f5198a6f81d09707b2854df042c version of SelectFuzz,
# which is the latest commit that we could find, then built it in the official docker image.
# Then, the prebuilt SelectFuzz is copied to docker by the Dockerfile.

# unzip SelectFuzz
cd /fuzzer
tar -zxf /fuzzer/SelectFuzz.tar.gz
rm /fuzzer/SelectFuzz.tar.gz

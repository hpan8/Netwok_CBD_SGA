#!/bin/bash

for i in {0..9}; do qsub ./pbs/pbs.script.$i; done

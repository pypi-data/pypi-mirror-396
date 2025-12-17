#!/bin/bash
filename=${0%.sh}
job_dir=`dirname "$(realpath $0)"`
# Faking an execution
touch $job_dir/$filename/.pm.done
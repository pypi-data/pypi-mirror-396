#!/bin/bash
#
#SBATCH -J climix
#SBATCH -A climix
#SBATCH -t 10:00:00
#SBATCH -n 1 --mem=64g
#SBATCH hetjob
#SBATCH -N 2 --exclusive --cpus-per-task=2 --mem=346g
#SBATCH hetjob
#SBATCH -n 1 --mem=64g

# General approach
# ----------------
# We use slurm's heterogeneous job support for climix, using three components.
# The first component contains the dask scheduler, the second component runs
# the workers, and the third the client, i.e. climix itself. The scheduler
# and client are given 64GB each, but this can be adjusted if needed.
# The workers bring the scaling parallelism and can be run on an arbitrary
# number of nodes, depending on the size of the data and time and memory
# contraints. Note that we often want to use several nodes purely to gain
# access to sufficient memory.
#
# Freja specific notes
# -----------------
# Memory
# ~~~~~~
# Every normal (`thin`) node has 384GB of memory and there is a small number of
# `fat` nodes with 768GB of memory.
# The workers are run on normal nodes. To allow for a little bit of breathing
# room for the system and other programs, we use 90% of the available memory,
# equally distributed among the worker processes (or equivalently slurm tasks).
# Scheduler and client run on their own nodes. If, for any reason, memory becomes
# a limiting factor, nodes can be chosen as `fat` nodes by adding the `-C fat`
# switch to the corresponding SBATCH line at the top of this file.

# The default scheduler port is 8786, and for the dask dashboard 8787.
SCHEDULER_PORT=8786
DASHBOARD_PORT=$(echo "$SCHEDULER_PORT+1" | bc)

NO_SCHEDULERS=1
NO_PROGRAM=1

TOTAL_WORKER_CPUS=$(echo $SLURM_JOB_CPUS_PER_NODE_HET_GROUP_1 |sed 's/(x\([0-9]*\))/*\1/g;s/,/+/g'|bc)
echo "$TOTAL_WORKER_CPUS from $SLURM_JOB_CPUS_PER_NODE_HET_GROUP_1"
NO_WORKERS=$(($TOTAL_WORKER_CPUS / $SLURM_CPUS_PER_TASK_HET_GROUP_1))
MEM_PER_WORKER=$(echo "$SLURM_MEM_PER_NODE_HET_GROUP_1 * $SLURM_JOB_NUM_NODES_HET_GROUP_1 / $NO_WORKERS" | bc)

echo "Total number of workers: $NO_WORKERS"
echo "Memory per worker in MB: $MEM_PER_WORKER"

module load Mambaforge/23.3.1-1-hpc1
conda activate climix-devel

COORDINATE_DIR=/nobackup/...

cd $COORDINATE_DIR

SCHEDULER_FILE=$COORDINATE_DIR/scheduler-$SLURM_JOB_ID.json

# Start scheduler

SCHEDULER_COMMAND="--het-group=0 --ntasks $NO_SCHEDULERS --kill-on-bad-exit=1 \
                   dask scheduler \
                   --interface ib0 \
                   --scheduler-file $SCHEDULER_FILE \
                   --port $SCHEDULER_PORT \
                   --dashboard-address $DASHBOARD_PORT"

WORKERS_COMMAND="--het-group=1 --ntasks $NO_WORKERS --kill-on-bad-exit=1 \
                 dask worker \
                 --interface ib0 \
                 --scheduler-file $SCHEDULER_FILE \
                 --memory-limit ${MEM_PER_WORKER}MB \
                 --death-timeout 120 \
                 --nthreads 2"

srun $SCHEDULER_COMMAND : \
     $WORKERS_COMMAND : \
     --het-group=2 --ntasks $NO_PROGRAM --kill-on-bad-exit=1 \
     climix -s -d external@scheduler_file=$SCHEDULER_FILE \
       -x tn90pctl \
       /home/rossby/imports/cordex/EUR-11/CLMcom-CCLM4-8-17/v1/ICHEC-EC-EARTH/r12i1p1/rcp85/bc/links-hist-scn/day/tasmin_EUR-11_ICHEC-EC-EARTH_rcp85_r12i1p1_CLMcom-CCLM4-8-17_v1_day_*.nc

# wait


# Script ends here

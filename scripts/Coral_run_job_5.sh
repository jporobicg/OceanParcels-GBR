#!/bin/bash
#SBATCH --account=OD-232538
#SBATCH --time=4:00:00
#SBATCH --mem=5g
#SBATCH --cpus-per-task=1
#SBATCH --array=0-3805  # 3806 jobs

module load python

(( run = SLURM_ARRAY_TASK_ID ))

python ../src/main.py     $run 2016-12-16 T20:00 2016-12-20 T23:59 1000

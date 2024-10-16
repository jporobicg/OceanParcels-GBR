#!/bin/bash
#SBATCH --account=OD-232538
#SBATCH --time=4:00:00
#SBATCH --mem=5g
#SBATCH --cpus-per-task=1
#SBATCH --array=0-3805  # 3806 jobs

module load python

(( run = SLURM_ARRAY_TASK_ID ))

python ../src/main.py     $run 2021-12-21 T20:00 2021-12-25 T23:59 1000

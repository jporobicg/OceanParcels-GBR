#!/bin/bash
#SBATCH --account=OD-232538
#SBATCH --time=7:00:00
#SBATCH --mem=5g
#SBATCH --cpus-per-task=1
#SBATCH --array=0-3805%700  # 3806 jobs
#SBATCH --output=/dev/null  # Discard output files
#SBATCH --error=/dev/null   # Discard error files

module load python

(( run = SLURM_ARRAY_TASK_ID ))

python ../src/main.py     $run 2018-11-25 T20:00 2018-11-30 T23:59 1000

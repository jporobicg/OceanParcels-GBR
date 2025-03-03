#!/bin/bash
#SBATCH --account=OD-232538
#SBATCH --time=10:00:00
#SBATCH --mem=7g
#SBATCH --cpus-per-task=1
#SBATCH --output=/dev/null  # Discard output files
#SBATCH --error=/dev/null   # Discard error files
#SBATCH --array=0-3805%700
module load python

(( run = SLURM_ARRAY_TASK_ID ))

python ../src/main.py     $run 2018-10-27 T20:00 2018-10-31 T23:59 1000

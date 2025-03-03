#!/bin/bash
#SBATCH --account=OD-232538
#SBATCH --time=10:00:00
#SBATCH --mem=7g
#SBATCH --cpus-per-task=1
##SBATCH --output=/dev/null  # Discard output files
##SBATCH --error=/dev/null   # Discard error files
#SBATCH --array=2237,2891,3471%700  # Only run failed jobs

module load python

(( run = SLURM_ARRAY_TASK_ID ))

python ../src/main.py     $run 2015-10-29 T20:00 2015-11-02 T23:59 1000

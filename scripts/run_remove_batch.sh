#!/bin/bash
#SBATCH --account=OD-232538
#SBATCH --time=4:00:00
#SBATCH --mem=5g
#SBATCH --cpus-per-task=1
#SBATCH --array=0-18
(( run = SLURM_ARRAY_TASK_ID ))


./remove_zarr.sh $run



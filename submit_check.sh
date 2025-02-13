#!/bin/bash
#SBATCH --job-name=check_files
#SBATCH --output=check_files_%j.log
#SBATCH --error=check_files_%j.err
#SBATCH --time=02:00:00
#SBATCH --mem=4GB
#SBATCH --ntasks=1

bash Failed_runs.sh 
#!/bin/bash
#SBATCH --account=OD-232538
#SBATCH --time=4:00:00
#SBATCH --mem=5g
#SBATCH --cpus-per-task=1

module load python

dates=(
    "2015-10-29 T20:00 2015-11-02 T23:59"
    "2015-11-28 T20:00 2015-12-02 T23:59"
    "2015-12-27 T20:00 2015-12-31 T23:59"
    "2016-10-18 T20:00 2016-10-22 T23:59"
    "2016-11-17 T20:00 2016-11-21 T23:59"
    "2016-12-16 T20:00 2016-12-20 T23:59"
    "2017-10-08 T20:00 2017-10-12 T23:59"
    "2017-11-06 T20:00 2017-11-10 T23:59"
    "2017-12-06 T20:00 2017-12-10 T23:59"
    "2018-10-27 T20:00 2018-10-31 T23:59"
    "2018-11-25 T20:00 2018-11-30 T23:59"
    "2018-12-25 T20:00 2018-12-30 T23:59"
    "2019-10-16 T20:00 2019-10-20 T23:59"
    "2019-11-15 T20:00 2019-11-19 T23:59"
    "2019-12-14 T20:00 2019-12-18 T23:59"
    "2020-10-04 T20:00 2020-10-08 T23:59"
    "2020-11-03 T20:00 2020-11-07 T23:59"
    "2020-12-02 T20:00 2020-12-06 T23:59"
    "2021-01-01 T20:00 2021-01-05 T23:59"
    "2021-10-23 T20:00 2021-10-27 T23:59"
    "2021-11-21 T20:00 2021-11-25 T23:59"
    "2021-12-21 T20:00 2021-12-25 T23:59"
)
num_particles_per_day=1000

for i in ${!dates[@]}; do
    # Create a job script for this date
    echo "#!/bin/bash
#SBATCH --account=OD-232538
#SBATCH --time=7:00:00
#SBATCH --mem=5g
#SBATCH --cpus-per-task=1
#SBATCH --array=0-3805%700  # 3806 jobs
#SBATCH --output=/dev/null  # Discard output files
#SBATCH --error=/dev/null   # Discard error files

module load python

(( run = SLURM_ARRAY_TASK_ID ))

python ../src/main.py \
    \$run ${dates[i]} $num_particles_per_day" > ../jobs/Coral_run_job_$i.sh

done

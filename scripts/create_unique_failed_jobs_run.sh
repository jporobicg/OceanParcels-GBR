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

# Initialize arrays to store all failed runs and their corresponding dates
all_failed_runs=()
corresponding_dates=()

for i in ${!dates[@]}; do
    current_day=${dates[i]%% T*}
    
    # Check if failed runs file exists and read it
    failed_runs_file="../checks/Failed_run_${current_day}.txt"
    if [ ! -f "$failed_runs_file" ]; then
        echo "No failed runs file found for $current_day, skipping..."
        continue
    fi
    
    # Read failed runs into an array (only first column)
    mapfile -t failed_runs < <(cut -f1 "$failed_runs_file")
    if [ ${#failed_runs[@]} -eq 0 ]; then
        echo "No failed runs found in $failed_runs_file, skipping..."
        continue
    fi
    
    # Add each failed run and its corresponding date to the arrays
    for run in "${failed_runs[@]}"; do
        all_failed_runs+=("$run")
        # Quote the date string to preserve it as a single element
        corresponding_dates+=("\"${dates[i]}\"")
    done
done

# Create a single job script for all failed runs
output_dir="../jobs"
total_jobs=$((${#all_failed_runs[@]} - 1))

echo "#!/bin/bash
#SBATCH --account=OD-232538
#SBATCH --time=10:00:00
#SBATCH --mem=7g
#SBATCH --cpus-per-task=1
#SBATCH --output=/dev/null  # Discard output files
#SBATCH --error=/dev/null   # Discard error files
#SBATCH --array=0-$total_jobs%700  # Array for all failed jobs

module load python

# Create arrays with all failed runs and their dates
failed_runs=(${all_failed_runs[*]})
date_array=(${corresponding_dates[*]})

# Get the current array index
idx=\$SLURM_ARRAY_TASK_ID

python ../src/main.py \
    \${failed_runs[\$idx]} \${date_array[\$idx]} $num_particles_per_day" > $output_dir/Failed_Coral_run_job_all.sh

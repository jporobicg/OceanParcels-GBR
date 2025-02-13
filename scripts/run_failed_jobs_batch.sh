#!/bin/bash

# Create or clear the log file
echo "" > run.log

# Loop over the job scripts
for id in {0..19}; do
  script="jobs/Failed_Coral_run_job_${id}.sh"
  
  # Record the start time
  start_time=$(date +%s)

  # Print a message and append it to the log file
  echo "Starting job $id at $(date)" | tee -a run.log

  # Submit the job and get the job id
  jobid=$(sbatch --parsable "$script")

  # Wait for the job to finish
  while squeue -j $jobid | grep -q $jobid; do
    sleep 60
  done

  # Record the end time
  end_time=$(date +%s)

  # Calculate the time difference
  time_diff=$((end_time - start_time))

  # Print a message and append it to the log file
  echo "Job $id finished at $(date). Duration: $time_diff seconds." | tee -a run.log
done

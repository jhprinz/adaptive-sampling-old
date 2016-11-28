#!/bin/bash
#SBATCH -J testjob
#SBATCH -D /storage/mi/jprinz
#SBATCH -o testjob.%j.out
#SBATCH -p micro
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=500M
#SBATCH --time=00:30:00
#SBATCH --mail-type=end
#SBATCH --mail-user=jan-hendrik.prinz@fu-berlin.de

hostname
date
cd /home/jprinz/celery/adaptive-sampling/celerymd/celerymd
celery worker -A tasks --concurrency=1

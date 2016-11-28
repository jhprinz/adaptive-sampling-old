#!/bin/bash
#SBATCH -J test-celery
#SBATCH -D /home/jprinz/NO_BACKUP/
#SBATCH -o celery.%j.out
#SBATCH -p micro
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=500M
#SBATCH --time=00:30:00
#SBATCH --mail-type=end
#SBATCH --mail-user=jan-hendrik.prinz@fu-berlin.de

hostname
date


bash
cd /home/jprinz/celery/adaptive-sampling/celerymd/celerymd
celery worker -A tasks --concurrency=1

#!/usr/bin/env bash

conda config add channels conda-forge
conda install --yes redis
conda install --yes celery
conda install --yes flower
conda install --yes sshtunnel
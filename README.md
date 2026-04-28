# NASA Meteorite Landing Pipeline

A batch data pipeline that ingests NASA's meteorite
landing dataset, applies data quality checks, transforms
and loads to BigQuery. A simple project that will hopefully myself and others learn about building data pipelines with Python, GCS, BigQuery, Terraform, and GitHub Actions.

## Architecture

[Simple diagram or description of the flow]

## Why I Built This

I'm currently working as a junior data engineer at a bank. The system is complex, stack is fairly deep, and most of my work revolves around contributing to a data pipeline I didn't design. The purpose of this project to own something end-to-end.

## Stack

Python · BigQuery · GCS · Terraform · GitHub Actions

## Pipeline Stages

1. Ingest — hits NASA Open Data API, lands raw JSON to GCS
2. Quality — validates 5 rules, flags failures separately
3. Transform — normalises fields, casts types, snake_case
4. Load — explicit schema load to BigQuery, partitioned by year

## What I Learned

[Fill this in at the end — be specific about what broke]

## How to Run

[Step by step, assume nothing]

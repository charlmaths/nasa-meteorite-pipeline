# NASA Meteorite Landing Pipeline

GCP & AWS Stack.

A simple batch data pipeline that ingests NASA's meteorite
landing dataset, applies data quality checks, transforms
and loads to BigQuery. Extended to also pull NASA's Near Earth Object (NeoWS) feed on a daily schedule, so the project covers both a static historical load (GCP Pipeline) and a live incremental pull through the same pipeline shape (AWS Pipeline). A simple(ish?) project that will hopefully myself and others learn about building data pipelines with Python, GCS, BigQuery, Terraform, Lambda, S3, and GitHub Actions.

## Architecture

[Simple diagram or description of the flow]

## Why I Built This

As a Junior Data Engineer, I wanted to try and build something that I could actually own E2E. I currently work at a bank and the system is ciomplicated, the stack is fairly deep, and most of my work revolves around contributing to a data pipeline I didn't design. I wanted to build something that I could own from start to finish, and this project was a good opportunity to do that.

## Data Sources

This project intentionally uses two NASA datasets with different update patterns, to practice both batch and incremental pipeline design:

| Dataset                    | Update pattern     | Pipeline pattern           |
| -------------------------- | ------------------ | -------------------------- |
| Meteorite Landings         | Static / irregular | One-off batch load         |
| NeoWS (Near Earth Objects) | Daily              | Scheduled incremental pull |

Since the meteorite dataset barely changes, so it's not really useful for testing scheduling or idempotency. NeoWS updates daily, which makes it a better fit for practicing orchestration, dedup logic, and failure handling on a real flow of data.

## Stack

Python · BigQuery · GCS · Terraform · GitHub Actions · Docker · Airflow · AWS Lambda · S3

## Pipeline Stages

1. Ingest — hits NASA Open Data API, lands raw JSON to GCS
2. Quality — validates 5 rules, flags failures separately
3. Transform — normalises fields, casts types, snake_case
4. Load — explicit schema load to BigQuery, partitioned by year

### NeoWS incremental pipeline

1. Extract — scheduled pull from NeoWS API, [daily / cron cadence]
2. Dedup — checks [what key/logic] against already-landed records
   before writing, since the job may run more than once
3. Quality — [reuse existing rules / new rules specific to NeoWS shape]
4. Load — appends new records to BigQuery, partitioned by [date field]

Orchestrated with [Apache Airflow, self-hosted via Docker Compose /
GitHub Actions scheduled workflow].

## How to Run

1. Clone the repo
2. Set up GCP project and credentials
3. Run Terraform to create infrastructure
4. Trigger pipeline via GitHub Actions or run locally
5. Check BigQuery for results

## Commit cheeatsheet:

- feat: add meteorite data ingestion script
- feat: implement transformation pipeline
- fix: handle missing coordinates in dataset
- refactor: split pipeline into ingestion and transformation modules
- docs: add pipeline architecture diagram
- test: add tests for transformation logic
- build: add pandas and requests dependencies

## What I Learned

### Week - 1:

Created a simple ingetion script that uses basic ingestion fundamentals. ingest.py uses requests and json libraries to parse the json files loaded from an api request. api_ingestor method uses try and except to extract the file and handle error codes, if succesful, we then use 'open' and json.loads method to land the json payload into the specific path we've established

### Week - 2:

Created a new script within the pipeline directory, this script is used for data quality checks to ensure that the we get good quality data. The initial methods inside the script are for basic null check, timestamp check (year), mass and coordinate checks, and finally, if failed file exist, we qurantine it.

# cloud-scanner

A modular cloud security scanner built in Python. Scans TCP ports, HTTP security headers, and S3 bucket configurations from a unified CLI. Results are persisted to AWS S3 as timestamped JSON. Infrastructure is provisioned with Terraform and the pipeline runs on GitHub Actions.

---

## Overview

cloud-scanner bundles three independent scanners behind a single CLI entry point:

| Scanner | What it checks |
|---|---|
| TCP port scanner | Open ports on a host |
| HTTP header checker | Presence and correctness of security headers |
| S3 misconfiguration checker | Public access, ACLs, versioning, encryption, logging |

Each scan writes a timestamped JSON result to an S3 bucket under a path that reflects the scan type (`port-scans/`, `header-checks/`, `s3-checks/`).

---

## Features

- Three focused scanners, each independently usable
- Unified CLI — one entry point for all scan types
- Docker-packaged for consistent execution
- Results stored in S3 with timestamped filenames
- Terraform-managed AWS infrastructure (S3 + ECR)
- CI/CD pipeline: lint → test → build → push to ECR

---

## Project Structure

```
cloud-scanner/
├── app/
│   ├── cli.py             # unified CLI entry point
│   ├── scanner.py         # TCP port scanner
│   ├── header_checker.py  # HTTP security header checker
│   ├── s3_checker.py      # S3 misconfiguration checker
│   ├── utils.py           # shared utilities (S3 upload, JSON formatting)
│   ├── test_scanner.py    # pytest test suite
│   └── requirements.txt
├── terraform/
│   ├── main.tf            # S3 bucket and ECR repository resources
│   ├── variables.tf
│   └── outputs.tf
├── Dockerfile
└── .github/workflows/ci.yml
```

---

## Prerequisites

- Python 3.11+
- Docker
- Terraform
- AWS account with credentials configured (`~/.aws/credentials` or environment variables)

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Ksashav/cloud-scanner.git
cd cloud-scanner
```

### 2. Provision AWS infrastructure

```bash
cd terraform
terraform init
terraform apply
```

This creates:
- An S3 bucket for scan results (versioning enabled, server-side encryption, public access blocked, access logging enabled)
- An ECR repository for the Docker image (immutable tags, vulnerability scanning enabled)

### 3. Build the Docker image

```bash
docker build -t cloud-scanner .
```

### 4. Configure environment

The scanner needs AWS credentials and the target S3 bucket name at runtime. Pass them as environment variables:

```bash
export AWS_ACCESS_KEY_ID=<your-key>
export AWS_SECRET_ACCESS_KEY=<your-secret>
export AWS_DEFAULT_REGION=eu-west-2
export S3_RESULTS_BUCKET=<bucket-name-from-terraform-output>
```

---

## Usage

Run scans locally with Python:

```bash
# TCP port scan
python app/cli.py ports <host>

# HTTP security header check
python app/cli.py headers <url>

# S3 misconfiguration check
python app/cli.py s3 <bucket>
```

Or via Docker:

```bash
docker run --env-file .env cloud-scanner ports <host>
docker run --env-file .env cloud-scanner headers <url>
docker run --env-file .env cloud-scanner s3 <bucket>
```

Results are printed to stdout and saved to S3 at:

```
s3://<bucket>/port-scans/<timestamp>.json
s3://<bucket>/header-checks/<timestamp>.json
s3://<bucket>/s3-checks/<timestamp>.json
```

### Run tests

```bash
pip install -r app/requirements.txt pytest
python -m pytest app/test_scanner.py -v
```

---

## CI/CD

The GitHub Actions pipeline (`.github/workflows/ci.yml`) runs on every push and pull request to `main`:

1. **test** — installs dependencies, lints with `flake8` (max line length 120), runs `pytest`
2. **deploy** — authenticates to ECR, builds the Docker image tagged with the commit SHA, pushes to ECR

Required GitHub Actions secrets:

| Secret | Value |
|---|---|
| `AWS_ACCESS_KEY_ID` | IAM user or role access key |
| `AWS_SECRET_ACCESS_KEY` | Corresponding secret key |

---

## Security Decisions

**S3 bucket (results storage)**
- Public access blocked at the bucket policy level
- Server-side encryption enabled by default
- Versioning enabled so results are not silently overwritten
- Access logging enabled for audit trail

**ECR repository**
- Immutable image tags prevent overwriting a tagged image — each deploy produces a new SHA-tagged image
- Vulnerability scanning runs on every image push

**Scan results**
- Timestamped filenames prevent collisions and preserve history
- Results are namespaced by scan type to make programmatic access and access policies straightforward

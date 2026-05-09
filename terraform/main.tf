terraform {
    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = "~> 5.0"
        }
    }
}

provider "aws" {
    region = "eu-west-2"
}

# S3 bucket to store scanner results
resource "aws_s3_bucket" "scanner_results" {
    bucket = "cloud-scanner-results-250368538184"

    tags = {
        Project     = "cloud-scanner"
        Environment = "dev"
    }
}

# Block all public access to the S3 bucket
resource "aws_s3_bucket_public_access_block" "scanner_results" {
    bucket = aws_s3_bucket.scanner_results.id

    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
}


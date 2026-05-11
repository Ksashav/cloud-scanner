output "bucket_name" {
  description = "Name of the scanner results bucket"
  value       = aws_s3_bucket.scanner_results.bucket
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.cloud_scanner.repository_url
}
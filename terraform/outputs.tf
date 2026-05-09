output "bucket_name" {
  description = "Name of the scanner results bucket"
  value       = aws_s3_bucket.scanner_results.bucket
}
from botocore.exceptions import ClientError
from utils import save_results_to_s3
import sys


def check_bucket_public_access(bucket_name):
    """Check if S3 bucket has public access blocked"""
    s3 = boto3.client('s3')
    try:
        response = s3.get_public_access_block(Bucket=bucket_name)
        config = response['PublicAccessBlockConfiguration']
        all_blocked = all([
            config['BlockPublicAcls'],
            config['BlockPublicPolicy'],
            config['IgnorePublicAcls'],
            config['RestrictPublicBuckets']
        ])
        return "secure" if all_blocked else "misconfigured"
    except Exception as e:
        print(f"Error checking public access: {e}")
        return "unknown"


def check_bucket_versioning(bucket_name):
    """Check if S3 bucket has versioning enabled"""
    s3 = boto3.client('s3')
    try:
        response = s3.get_bucket_versioning(Bucket=bucket_name)
        status = response.get('Status', 'Disabled')
        return "enabled" if status == "Enabled" else "disabled"
    except Exception as e:
        print(f"Error checking versioning: {e}")
        return "unknown"


def check_bucket_encryption(bucket_name):
    """Check if S3 bucket has encryption enabled"""
    s3 = boto3.client('s3')
    try:
        s3.get_bucket_encryption(Bucket=bucket_name)
        return "enabled"
    except ClientError as e:
        if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
            return "disabled"
        print(f"Error checking encryption: {e}")
        return "unknown"


def check_bucket_logging(bucket_name):
    """Check if S3 bucket has logging enabled"""
    s3 = boto3.client('s3')
    try:
        response = s3.get_bucket_logging(Bucket=bucket_name)
        logging_enabled = 'LoggingEnabled' in response
        return "enabled" if logging_enabled else "disabled"
    except Exception as e:
        print(f"Error checking logging: {e}")
        return "unknown"


def main():
    if len(sys.argv) < 2:
        print("Usage: python s3_checker.py <bucket_name>")
        sys.exit(1)

    bucket_name = sys.argv[1]
    results = {
        "public_access": check_bucket_public_access(bucket_name),
        "versioning": check_bucket_versioning(bucket_name),
        "encryption": check_bucket_encryption(bucket_name),
        "logging": check_bucket_logging(bucket_name)
    }
    print(f"Security check results for bucket '{bucket_name}':")
    for key, value in results.items():
        if value == "secure" or value == "enabled":
            print(f" ✓ {key}: {value}")
        elif value == "misconfigured" or value == "disabled":
            print(f" ✗ {key}: {value}")
        else:
            print(f" ? {key}: {value} (unknown)")

    save_results_to_s3(bucket_name, results,
                       "cloud-scanner-results-250368538184", prefix="s3_checks")
    print(f"Results saved to S3 bucket 'cloud-scanner-results-250368538184' with prefix 's3_checks'")


if __name__ == "__main__":
    main()

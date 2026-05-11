import argparse
import sys
import scanner
import header_checker
import s3_checker
from utils import save_results_to_s3 

def main():
    parser = argparse.ArgumentParser(
        description="Cloud Security Scanner"
    )
    
    subparsers = parser.add_subparsers(dest="command")
    
    # Port scanner
    port_parser = subparsers.add_parser("ports", help="Run port scanner")
    port_parser.add_argument("host", help="Target host to scan")
    
    # Header checker
    header_parser = subparsers.add_parser("headers", help="Check HTTP security headers")
    header_parser.add_argument("host", help="Target URL to check")
    
    # S3 checker
    s3_parser = subparsers.add_parser("s3", help="Check S3 bucket security")
    s3_parser.add_argument("bucket", help="S3 bucket name to check")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "ports":
        results = scanner.scan_host(args.host, range(1, 1001))
        scanner.output_results(args.host, results)
        save_results_to_s3(args.host, results, "cloud-scanner-results-250368538184", prefix="port_scans")
    
    elif args.command == "headers":
        results = header_checker.check_security_headers(header_checker.get_headers(args.host))
        header_checker.output_header_results(args.host, results)
        save_results_to_s3(args.host, results, "cloud-scanner-results-250368538184", prefix="header_checks")
    
    elif args.command == "s3":
        results = {
            "public_access": s3_checker.check_bucket_public_access(args.bucket),
            "versioning": s3_checker.check_bucket_versioning(args.bucket),
            "encryption": s3_checker.check_bucket_encryption(args.bucket),
            "logging": s3_checker.check_bucket_logging(args.bucket)
        }
        
        for key, value in results.items():
            if value == "secure" or value == "enabled":
                print(f" ✓ {key}: {value}")
            elif value == "misconfigured" or value == "disabled":
                print(f" ✗ {key}: {value}")
            else:
                print(f" ? {key}: {value} (unknown)")

        save_results_to_s3(args.bucket, results, "cloud-scanner-results-250368538184", prefix="s3_checks")
            
    else:
        print("Unknown command")
        parser.print_help()
        sys.exit(1)
    

if __name__ == "__main__":
    main()
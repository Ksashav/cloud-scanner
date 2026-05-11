from utils import save_results_to_s3
import requests
import sys


def get_headers(host):
    """Get HTTP headers from a host"""

    url = host
    if not host.startswith(("http://", "https://")):
        url = f"https://{url}"
    try:
        response = requests.get(url, timeout=5)
        return dict(response.headers)
    except requests.RequestException as e:
        print(f"Error fetching headers from {host}: {e}")
        return {}


def check_security_headers(headers):
    """Check for common security headers"""
    security_headers = [
        "Content-Security-Policy",
        "Strict-Transport-Security",
        "X-Content-Type-Options",
        "X-Frame-Options",
        "X-XSS-Protection"
    ]
    results = dict()
    for header in security_headers:
        results[header] = headers[header] if header in headers else "missing"
    return results


def output_header_results(host, results):
    """Print header check results to console"""
    print(f"Header check results for {host}:")
    for header, status in results.items():
        if status == "missing":
            print(f" ✗{header}: MISSING")
        else:
            print(f" ✓{header}: {status}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python header_checker.py <host>")
        sys.exit(1)
    host = sys.argv[1]

    headers = get_headers(host)
    if not headers:
        print("No headers found, skipping security header check.")
        return
    results = check_security_headers(headers)
    output_header_results(host, results)
    bucket_name = "cloud-scanner-results-250368538184"
    filename = save_results_to_s3(
        host, results, bucket_name, prefix="header_checks")
    print(
        f"Results saved to S3 bucket '{bucket_name}' with filename '{filename}'")


if __name__ == "__main__":
    main()

import socket
import boto3
import json
from datetime import datetime
import sys
from utils import save_results_to_s3, output_results

def scan_port(host, port, timeout=1):
    """Try to connect to a host:port
    Returns True if open, False if closed"""

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except socket.error:
        return False
    
def scan_host(host, ports):
    """Scan a host for a list of ports
    Returns a dict of port:status"""
    results = {}
    for port in ports:
        is_open = scan_port(host, port)
        results[port] = "open" if is_open else "closed"
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python scanner.py <host>")
        sys.exit(1)
        
    host = sys.argv[1]
    ports = range(1, 10001)
    results = scan_host(host, ports)
    output_results(host, results)
    bucket_name = "cloud-scanner-results-250368538184"
    filename = save_results_to_s3(host, results, bucket_name, prefix="port_scans")
    print(f"Results saved to S3 bucket '{bucket_name}' with filename '{filename}'")


if __name__ == "__main__":
    main()

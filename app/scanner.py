import socket
import boto3
import json
from datetime import datetime

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

def save_results_to_s3(host, results, bucket_name):
    """
    Save scan results as JSON to S3
    """
    s3 = boto3.client('s3')
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"scan_{host}_{timestamp}.json"

    data = {
        "host": host,
        "timestamp": timestamp,
        "results": results
    }

    s3.put_object(
        Bucket=bucket_name,
        Key=filename,
        Body=json.dumps(data, indent=2),
        ContentType='application/json'
        )

    return filename

def output_results(host, results):
    """Print scan results to console"""
    print(f"Scan results for {host}:")
    found_open = False
    for port in results:
        
        if results[port] == "open":
            print(f" Open ports are {port}")
            found_open = True
    if not found_open:
        print(" No open ports found.")

def main():
    #host = input("Enter the host to scan (e.g., 192.168.1.1): ")
    host = "127.0.0.1"
    ports = range(1, 1001)
    results = scan_host(host, ports)
    output_results(host, results)

if __name__ == "__main__":
    main()

import boto3
import json
from datetime import datetime

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
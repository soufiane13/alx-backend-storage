#!/usr/bin/env python3

from pymongo import MongoClient

def main():
    """Main function to analyze nginx logs in MongoDB."""
    # Connect to MongoDB server
    client = MongoClient('mongodb://127.0.0.1:27017')
    nginx_collection = client.logs.nginx

    # Count total number of logs
    n_logs = nginx_collection.count_documents({})
    print(f'{n_logs} logs')

    # List of HTTP methods to analyze
    methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    print('Methods:')
    # Count documents for each HTTP method
    for method in methods:
        count = nginx_collection.count_documents({"method": method})
        print(f'\tmethod {method}: {count}')

    # Count number of GET requests to /status path
    status_check = nginx_collection.count_documents(
        {"method": "GET", "path": "/status"}
    )
    print(f'{status_check} status check')

    # Aggregate top 10 IP addresses by request count
    top_ips = nginx_collection.aggregate([
        {"$group": {"_id": "$ip", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
        {"$project": {"_id": 0, "ip": "$_id", "count": 1}}
    ])

    # Output top IP addresses and their request counts
    print("IPs:")
    for top_ip in top_ips:
        ip = top_ip.get("ip")
        count = top_ip.get("count")
        print(f'\t{ip}: {count}')

if __name__ == "__main__":
    main()

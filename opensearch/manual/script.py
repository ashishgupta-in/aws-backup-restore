"""
Author: Ashish Gupta
Contact: ashishgupta6095@live.com

Description: Script to register a snapshot repository, create snapshots, restore snapshots and delete indices in an opensearch cluster
Prerequisties:
    - S3 bucket for storing the snapshots files
    - IAM role with S3 read, write and delete permissions on the bucket.
    - IAM role with pass role for the S3 role and ESHttpPut permissions for the opensearch cluster
"""

import boto3
import requests
from requests_aws4auth import AWS4Auth

service = 'es'

def main():
    host = input("Enter opensearch domain endpoint : ")
    region = input("Enter aws region : ")

    try:
        aws_auth = generate_auth(region)

    except Exception as e:
        print("Error occured while generating authentication token." + "\n" + str(e))
        return

    print('''
    1. Register a repository
    2. Take snapshot for all indices
    3. Restore indices from snapshot
    4. Delete index
    5. Exit
    ''')

    choice = 0
    while choice != 5:
        choice = int(input("Enter your choice : "))
        match choice:
            case 1:
                register_repo(region, host, aws_auth)
            case 2:
                create_snapshot(host, aws_auth)
            case 7:
                return
            case _:
                print("Invalid choice, please try again.")
    return

# Generate authentication
def generate_auth(region):
    print('''
    1. Generate authentication using IAM role attached (can run on EC2 instance)
    2. Generate authentication using aws profile
    ''')
    auth_choice = int(input("Enter your choice : "))
    
    match auth_choice:
        case 1:
            credentials = boto3.Session().get_credentials()
        case 2:
            profile = input("Enter aws profile name : ")
            credentials = boto3.Session(profile_name=profile).get_credentials()
        case _:
            print("Invalid choice, please try again.")
            exit(1)
    aws_auth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    return aws_auth

# Register backup repository
def register_repo(region, host, aws_auth):

    bucket = input("Enter S3 bucket name : ")
    s3_base_path = input("Enter S3 bucket base path : ")
    role_arn = input("Enter role arn having S3 read, write & delete permissions : ")
    repo_name = input("Enter backup repository name : ")
    
    payload = {
        "type": "s3",
        "settings": {
            "bucket": bucket,
            "base_path": s3_base_path,
            "region": region,
            "role_arn": role_arn
        }
    }
    headers = { "Content-Type": "application/json" }

    path = '/_snapshot/' + repo_name
    url = host + path

    response = requests.put(url, auth=aws_auth, json=payload, headers=headers)
    get_response(response)

# Create snapshot
def create_snapshot(host, aws_auth):
    repo_name = input("Enter repository name : ")
    snapshot_name = input("Enter snapshot name : ")
    
    path = '/_snapshot/' + repo_name + '/' + snapshot_name
    url = host + path

    response = requests.put(url, auth=aws_auth)
    get_response(response)

# Restore snapshot
def restore_snapshot(host, aws_auth):
    repo_name = input("Enter repository name : ")
    snapshot_name = input("Enter snapshot name : ")
    indices = input("Enter indices to restore (seperated by spaces): ")
    
    indices = indices.split(" ").join(",")

    path = '/_snapshot/' + repo_name + '/' + snapshot_name + '/_restore'
    url = host + path

    # payload = {
    #   "indices": "-.kibana*,-.opendistro_security,-.opendistro-*",
    #   "include_global_state": False
    # }

    payload = {
      "indices": indices,
      "include_global_state": False
    }

    headers = { "Content-Type": "application/json" }

    response = requests.post(url, auth=aws_auth, json=payload, headers=headers)
    get_response(response)

# Delete an index in an opensearch cluster
def delete_index(host, aws_auth):
    path = input("Enter index name to delete : ")
    url = host + path

    response  = requests.delete(url, auth=aws_auth)
    get_response(response)

# Print response to stdout
def get_response(response):
    print("Status Code : ", response.status_code, "\n")
    print(response.text)

if __name__ == "__main__":
    main()

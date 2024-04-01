# Methodologies

## Automated Snapshots

## Manual Snapshots

> Script: script.py

For manual snapshots, perform the following steps:
1. Create an IAM roles for registering a snapshot repository. This role will have S3 permissions.
2. Create an  IAM policy to pass iam role created in previous step and having Http permissions to opensearch cluster.
3. Attach IAM policy to an EC2 instance profile role to execute the script on that instance.
4. Execute the script on EC2 instance.

* #### IAM role with S3 read, write and delete permissions.
    **Permission policy:**

    ```
    {
    "Version": "2012-10-17",
    "Statement": [{
        "Action": [
            "s3:ListBucket"
        ],
        "Effect": "Allow",
        "Resource": [
            "arn:aws:s3:::<s3-bucket-name>"
        ]
        },
        {
        "Action": [
            "s3:GetObject",
            "s3:PutObject",
            "s3:DeleteObject"
        ],
        "Effect": "Allow",
        "Resource": [
            "arn:aws:s3:::<s3-bucket-name>/*"
        ]
        }
    ]
    }
    ```
    **Add trust relationships for opensearch to assume this role.**
    ```
    {
    "Version": "2012-10-17",
    "Statement": [{
        "Sid": "",
        "Effect": "Allow",
        "Principal": {
        "Service": "es.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
    }]  
    }
    ```

* #### IAM policy having permissions to pass the role and perform Http requests to the opensearch cluster.
    **Permission policy:**

    ```
    {
    "Version": "2012-10-17",
    "Statement": [
        {
        "Effect": "Allow",
        "Action": "iam:PassRole",
        "Resource": "arn:aws:iam::<account-id>:role/<s3-role>"
        },
        {
        "Effect": "Allow",
        "Action": "es:ESHttpPut",
        "Resource": "arn:aws:es:region:<account-id>:domain/<opensearch-domain-name>/*"
        }
    ]
    }
    ```
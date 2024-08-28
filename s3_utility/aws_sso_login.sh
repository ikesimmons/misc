aws configure set sso_start_url https://aptive.awsapps.com/start --profile PowerPlusUser-458548934557
aws configure set sso_region us-east-1 --profile PowerPlusUser-458548934557
aws configure set sso_account_id 458548934557 --profile PowerPlusUser-458548934557
aws configure set sso_role_name PowerPlusUser --profile PowerPlusUser-458548934557
aws configure set region us-east-1 --profile PowerPlusUser-458548934557

aws sso login --profile PowerPlusUser-458548934557

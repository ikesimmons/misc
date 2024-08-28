#!/bin/bash

# Function to get a presigned URL from the API
getPresignedUrl() {
    fileExtension=$1
    url="https://4x3ak219p7.execute-api.us-east-1.amazonaws.com/staging/presigned_url?file_extension=$fileExtension"
    apiKey="xDqmgOS3Ei2NYCjxZptNb8bCk5LWGmry9UKEnRhL"

    # Perform the request using curl
    response=$(curl -s -w "\n%{http_code}" -H "x-api-key: $apiKey" -X GET "$url" --insecure)

    # Extract the response body and status code
    body=$(echo "$response" | sed '$d')
    httpStatusCode=$(echo "$response" | tail -n1)

    # Check for successful HTTP response
    if [ "$httpStatusCode" -ne 200 ]; then
        echo "Failed to fetch presigned URL. Status code: $httpStatusCode"
        return 1
    fi

    # Decode the JSON response
    presignedUrl=$(echo "$body" | jq -r '.presigned_url // empty')
    fileName=$(echo "$body" | jq -r '.file_name // empty')

    if [ -z "$presignedUrl" ] || [ -z "$fileName" ]; then
        echo "Error decoding JSON or missing fields in the response"
        return 1
    fi

    echo "$presignedUrl" "$fileName"
}

# Usage example
# result=($(getPresignedUrl "jpg"))
# presignedUrl=${result[0]}
# fileName=${result[1]}
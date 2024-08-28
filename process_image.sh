#!/bin/bash

# Step 1: Get Presigned URL
echo "Getting presigned URL..."
response=$(curl -s -H "x-api-key: xDqmgOS3Ei2NYCjxZptNb8bCk5LWGmry9UKEnRhL" -X GET "https://4x3ak219p7.execute-api.us-east-1.amazonaws.com/staging/presigned_url?file_extension=jpg")
presignedUrl=$(echo "$response" | jq -r '.presigned_url')
fileName=$(echo "$response" | jq -r '.file_name')

if [ -z "$presignedUrl" ] || [ -z "$fileName" ]; then
    echo "Failed to get presigned URL."
    exit 1
fi

echo "Presigned URL: $presignedUrl"
echo "File Name: $fileName"

# Step 2: Upload Image to S3
echo "Uploading image to S3..."
uploadResponse=$(curl -s -X PUT --upload-file /Users/ike.simmons/data_science/scrape/images/anax/002_anax.jpg "$presignedUrl")

if [ $? -ne 0 ]; then
    echo "Failed to upload image to S3."
    exit 1
fi

echo "Image uploaded successfully."

# Step 3: Identify Image
echo "Identifying image..."
identifyResponse=$(curl -s -X GET "https://4x3ak219p7.execute-api.us-east-1.amazonaws.com/staging/perdict_pest_identification?file_name=$fileName" \
-H "x-api-key: xDqmgOS3Ei2NYCjxZptNb8bCk5LWGmry9UKEnRhL")

if [ $? -ne 0 ]; then
    echo "Failed to identify the image."
    exit 1
fi

echo "Image identification response:"
echo "$identifyResponse"
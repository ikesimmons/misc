#!/bin/bash

# Function to upload a file to S3 using a pre-signed URL
uploadFileToS3() {
    presignedUrl=$1
    filePath=$2

    # Perform the file upload using curl
    response=$(curl -s -o /dev/null -w "%{http_code}" -T "$filePath" "$presignedUrl")

    # Check the response code
    if [ "$response" -eq 200 ]; then
        echo "File uploaded successfully"
        return 0
    else
        echo "Failed to upload file. Status code: $response"
        return 1
    fi
}

# Usage example
# uploadFileToS3 "https://your-presigned-url" "/path/to/your/file"
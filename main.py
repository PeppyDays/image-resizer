from http import HTTPStatus
from io import BytesIO

import boto3

from image_resizer.image import resize
from image_resizer.request import parse
from image_resizer.response import finalize
from image_resizer.storage import load


def handle(event, _context):
    request = event["Records"][0]["cf"]["request"]
    response = event["Records"][0]["cf"]["response"]
    stream = BytesIO()

    # If the response from S3 is not OK (meaning the object doesn't exist),
    # return the original response
    if response["status"] != str(HTTPStatus.OK.value):
        return response

    try:
        # Parse the request to get the necessary information
        bucket, path, width, height, quality = parse(request)

        # Load the image from S3 and make it BytesIO stream
        # If the image doesn't exist, FileNotFoundError is raised
        client = boto3.client("s3", region_name="ap-northeast-2")
        stream, fmt = load(client, bucket, path)

        # Resize the image
        # If length from request parser is not valid, ValueError is raised
        stream = resize(stream, fmt, width, height, quality)

        # Finalise the response
        response = finalize(response, stream, fmt, None)
    except Exception as exception:
        # Finalise the response with exception
        response = finalize(response, stream, None, exception)
        print("An error occurred:", exception)
        print("Response is finalized:", response)

    return response

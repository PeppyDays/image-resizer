# Image Resizer for Image Download via CloudFront

## Introduction

![CloudFront with Lambda@Edge](https://d2908q01vomqb2.cloudfront.net/5b384ce32d8cdef02bc3a139d4cac0a22bb029e8/2018/02/01/1.png)

This is a simple image resizer for image download via CloudFront. It is implemented as a Lambda@Edge function. Specifically, this Lambda@Edge function is triggered by the `Origin Response` event. When the function is triggered, it checks the requested image size and resizes the image to the requested size. The resized image is then returned to the user.

## Image Resizing Process

From the request via CloudFront, there are some parameters that are used to resize the image. The parameters are as follows:

- S3 bucket name set in CloudFront distribution
- Path of an object in S3 bucket
- Requested image size (width and height) in the query string
  - width: `w` (default is None)
  - height: `h` (default is None)
- Requested quality of the image in the query string
  - quality: `q` (default is 80)

After parsing the parameters from the request, the Lambda function loads the image object from S3 bucket. From the object, the function reads the image data as follows:

- Image format from Content-Type, e.g. `image/jpeg`
- Image data as BytesIO stream

After that, the Lambda function resizes the image to the requested size. Here are specific rules for resizing the image:

- If width and height are both specified, the image is resized to the requested size
  - The maximum width is 2000 px and the maximum height is 5000 px defined in `image.py`
- If width is specified but not height, the image is resized to the requested width keeping the aspect ratio
  - But, if the requested width is larger than the original width, the image is returned as is
- If height is specified but not width, the image is resized to the requested height keeping the aspect ratio
  - But, if the requested height is larger than the original height, the image is returned as is
- If neither width nor height is specified, the image is returned as is
- If the image format is JPEG, the image is compressed to the requested quality

Basically, the image format is kept as is. Here are the supported image formats defined at `ImageFormat` enum in `image.py`:

- JPEG
- PNG
- GIF
- WEBP
- TIFF

If the object doesn't have the supported image format (or the object is not image), the Lambda function returns `Origin Response` as is.

## Development

### Prerequisites

- Python 3.12
- [Poetry](https://python-poetry.org)

### Local Setup

```bash
brew install python@3.12
brew install poetry

# Install dependencies manually via Poetry
# or open the project in Pycharm and let it install the dependencies 
poetry install
```

### Test

```bash
pytest --cov
```

### Deployment

> Should be automated in the future, but for now, it is a manual process.

- Create `artifact.zip` file in the `deploy` directory by running `./build.sh`
- Upload the `artifact.zip` file to the Lambda function in the AWS console
- Deploy the Lambda function as a Lambda@Edge function

## Reference

### Concept

- https://aws.amazon.com/blogs/networking-and-content-delivery/resizing-images-with-amazon-cloudfront-lambdaedge-aws-cdn-blog
- https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/lambda-at-edge-function-restrictions.html

### Implementation

- https://github.com/healingpaper-solution/image-resizer-lambda
- https://github.dev/hoony9x/aws-lambda-edge-img-resize-function
- https://taxijjang.tistory.com/185
- https://velog.io/@kpl5672/python-pillow-resize-thumbnail-%EC%82%AC%EC%9A%A9-%EC%8B%9C-%EC%9D%B4%EB%AF%B8%EC%A7%80-rotate%EB%90%98%EB%8A%94-%EB%AC%B8%EC%A0%9C-%ED%95%B4%EA%B2%B0
- https://stackoverflow.com/questions/50963537/pil-make-image-transparent-on-a-percent-scale

### Deployment

- https://docs.aws.amazon.com/lambda/latest/dg/python-package.html

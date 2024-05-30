rm -rf deploy/artifact.zip

pip install --platform manylinux2014_x86_64 --target ./deploy/packages --implementation cp --python-version 3.12 --only-binary=:all: --upgrade pillow

cd ./deploy/packages
zip -r ../artifact.zip .

cd ../..
zip ./deploy/artifact.zip main.py
zip -g ./deploy/artifact.zip image_resizer/__init__.py
zip -g ./deploy/artifact.zip image_resizer/image.py
zip -g ./deploy/artifact.zip image_resizer/request.py
zip -g ./deploy/artifact.zip image_resizer/response.py
zip -g ./deploy/artifact.zip image_resizer/storage.py

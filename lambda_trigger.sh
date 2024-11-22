# Create a new directory for dependencies
mkdir package
cd package

# Install required dependencies
pip install boto3 -t .

# Add your Lambda handler
cp ../deploy_handler.py .

# Create the zip file
zip -r ../deploy_handler.zip .

# Go back and clean up
cd ..
rm -rf package
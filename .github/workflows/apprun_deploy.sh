# save as: .github/workflows/deploy.yml
name: Deploy to AWS App Runner

on:
  push:
    branches: [ main ]

env:
  AWS_REGION: us-west-2
  ECR_REPOSITORY: nvda-2hr
  APP_RUNNER_SERVICE: nvda-2hr

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read

    steps:
    - name: Checkout code
      uses: actions/checkout@v2

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v1
      with:
        role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
        aws-region: ${{ env.AWS_REGION }}

    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1

    - name: Build and push image to Amazon ECR
      id: build-image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        IMAGE_TAG: ${{ github.sha }}
      run: |
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
        echo "image=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" >> $GITHUB_OUTPUT

    - name: Deploy to App Runner
      id: deploy
      run: |
        ECR_IMAGE="${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:${{ github.sha }}"
        
        if ! aws apprunner list-services --region ${{ env.AWS_REGION }} | grep -q "${{ env.APP_RUNNER_SERVICE }}"; then
          echo "Creating new App Runner service..."
          aws apprunner create-service \
            --region ${{ env.AWS_REGION }} \
            --service-name ${{ env.APP_RUNNER_SERVICE }} \
            --source-configuration "{
              \"AuthenticationConfiguration\": {
                \"AccessRoleArn\": \"${{ secrets.AWS_APPRUNNER_ECR_ACCESS_ROLE }}\"
              },
              \"AutoDeploymentsEnabled\": true,
              \"ImageRepository\": {
                \"ImageIdentifier\": \"${ECR_IMAGE}\",
                \"ImageRepositoryType\": \"ECR\",
                \"ImageConfiguration\": {
                  \"Port\": \"8000\"
                }
              }
            }" \
            --instance-configuration "{
              \"Cpu\": \"1024\",
              \"Memory\": \"2048\"
            }"
        else
          echo "Updating existing App Runner service..."
          aws apprunner update-service \
            --region ${{ env.AWS_REGION }} \
            --service-name ${{ env.APP_RUNNER_SERVICE }} \
            --source-configuration "{
              \"AuthenticationConfiguration\": {
                \"AccessRoleArn\": \"${{ secrets.AWS_APPRUNNER_ECR_ACCESS_ROLE }}\"
              },
              \"AutoDeploymentsEnabled\": true,
              \"ImageRepository\": {
                \"ImageIdentifier\": \"${ECR_IMAGE}\",
                \"ImageRepositoryType\": \"ECR\",
                \"ImageConfiguration\": {
                  \"Port\": \"8000\"
                }
              }
            }"
        fi

    - name: Get App Runner URL
      id: get-url
      run: |
        aws apprunner wait service-updated --service-name ${{ env.APP_RUNNER_SERVICE }} --region ${{ env.AWS_REGION }}
        URL=$(aws apprunner describe-service --service-name ${{ env.APP_RUNNER_SERVICE }} --region ${{ env.AWS_REGION }} --query "Service.ServiceUrl" --output text)
        echo "APP_URL=https://${URL}" >> $GITHUB_OUTPUT
        echo "::notice title=Deployment URL::https://${URL}"

    - name: Display App URL
      run: |
        echo "🚀 Application deployed successfully!"
        echo "📝 Application URL: ${{ steps.get-url.outputs.APP_URL }}"
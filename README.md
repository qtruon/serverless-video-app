# serverless video application
This is a first project to study on:
- [x] Lambda Serverless, API Gateway and S3
- [x] Use SAM to deploy lambda and related resources
- [x] CI process from GitHub to CodePipeline with CodeBuild and CodeDeploy
- [x] Support Dev/Prod deployment
- [ ] Set private Gateway API and access via AWS ClientVPN

## *Status:*
- Use swagger template to define query string and header for API Gateway method
- Add CodeBuild and CodePipeline into CloudFormation template
- Use Parameters, Mappings in CloudFormation for Dev/Prod deployment support
- Apply Secrets Manager to store GitHub OAuth Token for GitHub integration with CodePipeline

## *Next Steps:*
- Create shell script to update website config with new API Gateway
- Integrate the website (not in scope of study) into the deployment into S3 hosted
- Add function to view video by presigned url (limitation of Isengard not able to public S3 bucket)
- Use different AWS accounts to deploy Dev/Prod

## *Usage:*

Runtime: 
- Python3.8
- aws-cli/1.18.16
- botocore/1.15.16
- SAM CLI, version 0.43.0

Source structure:
```
root
  |_ disney.mp4                                 : sample video file
  |_ lambda
        |_ create_presigned_url                 : create presigned url to post video by authorized user
        |_ custom_authorizer                    : custom authorizer via Auth0
        |_ dependencies                         : dependencies layer of import libraries
        |_ update_transcode                     : post transcode update status to Firebase DB
        |_ user_info                            : get user profile information
        |_ video_transcode                      : upload video to S3 then create transcode job and DB record
                  |_ serviceAccountKey.json     : service account credential to Firebase DB (skip this out of git)
                  |_ video_transcode.py         : main lambda handler here
        |_ buildspec.yaml                       : CodeBuild buildspec action
        |_ env_prep.yaml                        : CloudFormation template for other resources
        |_ swagger.yaml                         : Swagger configuration for API Gateway CORS
        |_ template.yaml                        : SAM template for all lambda functions
  |_ website                                    : front-end nodejs app
```

- To create the dependencies.zip for dependencies layer, create a temporary folder for package installation (ex: packages/python/lib/python3.8/site-packages, refer Resource#3) then install the needed packages into this folder (check the list of existing modules in AWS and be awared of the version dependencies for awscli) then zip this folder content into the zip file (use the 'dependencies.zip' within the SAM template)
```
mkdir ./packages/python/lib/python3.8/site-packages
pip3 install -t ./packages rsa==3.4.2 requests==2.22.0 python-dateutil==2.8.0 firebase-admin python-jose
cd ./packages
zip -r9 ../dependencies/dependencies.zip .
```
- Create GitHub OAuth token in Secrets Manager (see Resources #13)
- Prepare the environment such as the sam deployment bucket with CloudFormation (we crete IAM role in this template so need CAPABILITY_NAMED_IAM) then use sam deploy which will refer to the bucket created in the CloudFormation template for deployment
```
aws cloudformation create-stack --stack-name video-env-stack --template-body file://env_prep.yaml --capabilities CAPABILITY_NAMED_IAM
sam deploy --s3-bucket video-app-deploy --stack-name video-app-stack --capabilities CAPABILITY_IAM
```
- Update the Auth0 information and the Gateway API into website/js/config.js
```
var configConstants = {
    auth0: {
        domain: [auth0_domain],
        clientId: [auth0_clientId]
    },
    apiBaseUrl: [GatewayAPI_StateUrl]
};
```
- Update the Firebase connection for front-end to display the data in website/js/video-controller.js (line 65). Go to Project settings (the clog icon next to Project Overview on the left navigation), in General tab, scroll down to Firebase SDK snippet/CDC, copy the  script // Your web app's Firebase configuration 
```
        var firebaseConfig = {
            apiKey: "[ApiKey]",
            authDomain: "[FirebaseDomain]",
            databaseURL: "[DbUrl]",
            projectId: "[ProjectId]",
            storageBucket: "[]StorageBucket",
            messagingSenderId: "[MsgId]",
            appId: "[AppId]"
        };
        firebase.initializeApp(firebaseConfig);
```
- Install required modules for Nodejs application and start the web, open browser: http://127.0.0.1:8100/
```
cd website
npm install
npm start
```
- External application like Auth0 and Firebase need to manually configure (refer to resource lesson from ACloudGuru in Lab2 and Lab5)

## *Resources:*
Original project from [Serverles for Beginers from ACloudGuru](https://acloud.guru/learn/serverless-for-beginners)

  1. Refer to [boto3 module](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html) for aws client object
  2. How to [deploy Python lambda packages](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html) (manual)
  3. Use [Library Dependencies in a Layer](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html#configuration-layers-manage) or read this [thread](https://towardsdatascience.com/introduction-to-amazon-lambda-layers-and-boto3-using-python3-39bd390add17)
  4. Refer to this [existing modules list in AWS lambda](https://gist.github.com/gene1wood/4a052f39490fae00e0c3#file-all_aws_lambda_modules_python-md) to reduce the dependencies package when deploy
  5. [Best practices for error handling in Python](https://stackoverflow.com/questions/2052390/manually-raising-throwing-an-exception-in-python)
Deploy lambda with SAM
  6. [Package and deploy using SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-deploying.html)
  7. [SAM template documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-resource-function.html)
  8. Create [custom authorizer for API Gateway](https://medium.com/carsales-dev/api-gateway-with-aws-sam-template-c05afdd9cafe) via SAM template (also create API Gateway + method attach lambda)
  9. Create [lambda event trigger by S3](https://docs.aws.amazon.com/lambda/latest/dg/with-s3-example-use-app-spec.html) via SAM template
  10. [Custom role, policy for lambda](https://aws.amazon.com/premiumsupport/knowledge-center/lambda-sam-template-permissions/) via SAM template
  11. [CloudFormation documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/AWS_ApiGateway.html)
  12. Detail [samples for API Gateway](https://blog.jayway.com/2016/08/17/introduction-to-cloudformation-for-api-gateway/) via CloudFormation
  13. [GitHub authentication](https://docs.aws.amazon.com/codepipeline/latest/userguide/GitHub-authentication.html)
  14. How to [get stack output via CLI](https://stackoverflow.com/questions/51686580/how-to-get-stack-output-from-aws-sam)
  15. SAM deploy will always create 'Stage' stage, [how to eleminate this stage](https://github.com/awslabs/serverless-application-model/issues/191)
  16. [Using Secrets Manager with CloudFormation](https://docs.amazonaws.cn/en_us/AWSCloudFormation/latest/UserGuide/dynamic-references.html)
  17. [Using Parameter Store with CloudFormation](https://start.jcolemorrison.com/using-ssm-parameters-with-cloudformation-templates-and-terraform-projects/)
  18. Create [CodeBuild and CodePipeline source by GitHub](https://github.com/symphoniacloud/github-codepipeline/blob/master/pipeline.yaml) via CloudFormation
  19. Detail [samples of CodePipeline and CodeBuild](https://code.amazon.com/packages/AWSProServe_CloudFormationMarketplace/trees/mainline/--/cloudformation-templates/CICD/CICD-Pipeline-for-Containers-Demo/CICD)
  20. Define [query string and header via swagger](https://swagger.io/docs/specification/describing-parameters/#header-parameters) template
  21. [Issue when create new S3 CORS configuration](https://stackoverflow.com/questions/16908983/does-amazon-s3-need-time-to-update-cors-settings-how-long)

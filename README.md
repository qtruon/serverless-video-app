# serverless video application
This is a first project to study on:
- [x] Lambda Serverless, API Gateway and S3
- [x] Use SAM to deploy lambda and related resources
- [ ] CI process from GitHub to CodePipeline with CodeBuild and CodeDeploy
- [ ] Set private Gateway API and access via AWS ClientVPN

## *Status:*
- First commit for SAM template deploy works with expected resources
- Not yet testing on the application

## *Next Steps:*
- Run application test
- Create Method request query string and header in API gateway
- Refine SAM template to use System Management Parameters Store
- Create CodePipeline and deploy application via CodeBuild and CodeDeploy
- Create CloudFormation template for other resources (if needed)
- Integrate the website (not in scope of study) into the deployment into S3 hosted
- Add function to view video by presigned url (limitation of Isengard not able to public S3 bucket)

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
                  |_ requirements.txt           : **each** lambda has to have this manifest for SAM build (???)
                  |_ serviceAccountKey.json     : service account credential to Firebase DB
                  |_ video_transcode.py         : main lambda handler here
        |_ template.yaml                        : SAM template for all lambda functions
  |_ website                                    : front-end nodejs app
```

- To create the dependencies.zip for dependencies layer (as we don't use requirements.txt for each lambda and share the common dependency layer so we don't need to create the virtual environment), create a temporary folder for package installation (ex: packages) then install the needed packages into this folder (check the list of existing modules in AWS and be awared of the version dependencies for awscli) then zip this folder content into the zip file (use the 'dependencies.zip' within the SAM template)
```
mkdir ./packages
pip3 install -t ./packages rsa==3.4.2 requests==2.22.0 python-dateutil==2.8.0 firebase-admin python-jose
zip -r9 ./dependencies/dependencies.zip ./packages/*
```
- Create sam build and sam deploy (not sure if we need sam build because we use layer for all dependencies), make sure have the deployment bucket to let sam upload the packages for deployment process (ex: video-app-sam-deploy)
```
sam build
sam deploy --s3-bucket video-app-sam-deploy --stack-name video-app-stack --capabilities CAPABILITY_IAM
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
- Install required modules for Nodejs application and start the web (no need to run npm install now as the source code already in runable mode), open browser: http://127.0.0.1:8100/
```
cd website
npm install
npm start
```
- External application like Auth0 and Firebase need to manually configure (refer to resource lesson from ACloudGuru in Lab2 and Lab5)

## *Resources:*
Original project from [Serverles for Beginers from ACloudGuru](https://acloud.guru/learn/serverless-for-beginners)

Convert the lambda serverless function into Pyhton: 
  - Refer to [boto3 module](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html) for aws client object

  - How to [deploy Python lambda packages (manual)](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html)

  - Use [Library Dependencies in a Layer](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html#configuration-layers-manage) or read this [thread](https://towardsdatascience.com/introduction-to-amazon-lambda-layers-and-boto3-using-python3-39bd390add17)

  - Refer to this [existing modules list in AWS lambda](https://gist.github.com/gene1wood/4a052f39490fae00e0c3#file-all_aws_lambda_modules_python-md) to reduce the dependencies package when deploy

  - [Best practices for error handling in Python](https://stackoverflow.com/questions/2052390/manually-raising-throwing-an-exception-in-python)

Deploy lambda with SAM
  - [Package and deploy using SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-deploying.html)

  - [SAM template documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-resource-function.html)

  - Create [custom authorizer for API Gateway](https://medium.com/carsales-dev/api-gateway-with-aws-sam-template-c05afdd9cafe) via SAM template (also create API Gateway + method attach lambda)

  - Create [lambda event trigger by S3](https://docs.aws.amazon.com/lambda/latest/dg/with-s3-example-use-app-spec.html) via SAM template
  
  - [Custom role, policy for lambda](https://aws.amazon.com/premiumsupport/knowledge-center/lambda-sam-template-permissions/) via SAM template
  
CloudFormation documentation which is used by SAM template
  - [CloudFormation documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/AWS_ApiGateway.html)

  - Detail [samples for API Gateway](https://blog.jayway.com/2016/08/17/introduction-to-cloudformation-for-api-gateway/) via CloudFormation

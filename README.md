# **AI Job Search Agent**

## **1\. Project Overview**

This serverless application automates the job search process by finding relevant openings, analyzing them with AI, and sending a daily report to the user. **This project now includes a complete authentication system using AWS Cognito.**

## **2\. Architecture**

The system is built on a serverless architecture in AWS, featuring:

* **Authentication:** AWS Cognito for user registration and sign-in (Email/Password, Google, Microsoft).  
* **Frontend:** A static web application hosted on S3 (or Amplify) for user configuration.  
* **Backend:** A set of AWS Lambda functions for orchestration, data collection, AI analysis, and notifications.  
* **Database:** Amazon DynamoDB to store user settings and job leads.  
* **Storage:** Amazon S3 for storing user CVs.  
* **Scheduling:** Amazon EventBridge to trigger the daily job search.  
* **AI Services:** Amazon Comprehend and Amazon Bedrock.

## **3\. NEW: Authentication Setup (Crucial Step)**

To enable Google and Microsoft sign-in, you must configure them as Federated Identity Providers in your Cognito User Pool after it's created.

1. **Deploy the template.yaml** using AWS SAM or CloudFormation.  
2. Go to the **Amazon Cognito** console and find your new User Pool (AI-Job-Agent-Users).  
3. Navigate to the **"Sign-in experience"** tab and click **"Add identity provider"**.  
4. **For Google:**  
   * Select **Google**.  
   * You will need a **Client ID** and **Client secret** from the [Google Cloud Console](https://console.cloud.google.com/apis/credentials). Create OAuth 2.0 credentials and ensure the authorized redirect URI matches the one provided by Cognito.  
5. **For Microsoft:**  
   * Select **Azure Active Directory**.  
   * You will need an **Application (client) ID** and a **Client secret** from the [Microsoft Azure Portal](https://www.google.com/search?q=https://portal.azure.com/). Register a new application and configure the redirect URIs.  
6. Go to the **"App integration"** tab in your User Pool, find your App Client (AI-Job-Agent-Web-Client), and edit the **"Hosted UI"** settings to enable the new identity providers.

## **4\. Frontend Configuration**

After deployment, you must update the amplifyConfig object in frontend/auth.html and frontend/dashboard.html with the UserPoolId, UserPoolClientId, and CognitoDomain from the CloudFormation stack outputs.

## **5\. Deployment**

This project is built to be deployed using the AWS SAM CLI and an AWS CodePipeline. Follow the Guia\_Despliegue\_Pipeline.md for instructions.

1. 

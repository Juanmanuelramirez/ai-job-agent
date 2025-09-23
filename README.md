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



# **Guía de Despliegue Automatizado con AWS Parameter Store**

Esta guía describe el método profesional para desplegar tu aplicación. Usaremos **AWS Systems Manager (SSM) Parameter Store** para gestionar las variables de entorno de forma segura y **AWS CodePipeline** para la automatización.

### **Prerrequisitos**

1. **Repositorio de Código:** Tu proyecto en GitHub (o similar) con el buildspec.yml actualizado que te he proporcionado.  
2. **Bucket de S3 para Artefactos:** Un bucket de S3 creado para almacenar los paquetes de código (ej. mi-agente-ia-artefactos).

### **Paso 1: Configurar las Variables en Parameter Store**

Este es el paso más importante para la automatización. Aquí centralizas tu configuración.

1. Ve a la consola de AWS y busca el servicio **Systems Manager**.  
2. En el menú de la izquierda, ve a **"Parameter Store"**.  
3. Haz clic en **"Crear parámetro"** y crea los siguientes tres parámetros:  
   * **Parámetro 1: Identidad de SES (Remitente)**  
     * **Nombre:** /ai-job-agent/prod/ses-identity  
     * **Tipo:** String (o SecureString para mayor seguridad)  
     * **Valor:** tu-correo-verificado-en-ses@ejemplo.com  
     * Haz clic en **"Crear parámetro"**.  
   * **Parámetro 2: URL del Frontend**  
     * **Nombre:** /ai-job-agent/prod/frontend-url  
     * **Tipo:** String  
     * **Valor:** https://www.tu-dominio-de-produccion.com/auth.html  
     * Haz clic en **"Crear parámetro"**.  
   * **Parámetro 3: Bucket de Artefactos**  
     * **Nombre:** /ai-job-agent/prod/artifact-bucket  
     * **Tipo:** String  
     * **Valor:** El nombre de tu bucket de S3 para artefactos (ej. mi-agente-ia-artefactos).  
     * Haz clic en **"Crear parámetro"**.

### **Paso 2: Crear el Pipeline**

Sigue los pasos del asistente de CodePipeline como antes.

1. **Iniciar el Asistente:** Ve a **CodePipeline**, haz clic en "Crear pipeline", dale un nombre y crea un nuevo rol de servicio.  
2. **Fase de Origen (Source):** Conecta tu repositorio de GitHub y selecciona la rama main.

### **Paso 3: Configurar la Fase de Build (Con Variables Automatizadas)**

Aquí es donde conectamos el pipeline con Parameter Store.

1. **Proveedor de compilación:** Elige **AWS CodeBuild**.  
2. Haz clic en **"Crear proyecto"**.  
   * **Nombre del proyecto:** AI-Job-Agent-Build-Prod.  
   * **Entorno:** Elige una imagen de Amazon Linux 2 estándar, runtime Python 3.9.  
   * **Rol de servicio:** Nuevo rol de servicio. **¡Importante\!** Después de crear el rol, tendrás que ir a IAM y añadirle permisos para leer desde Parameter Store (ssm:GetParameter).  
   * **Buildspec:** Deja la opción por defecto ("Usar un archivo buildspec").  
   * **Variables de Entorno (Sección Avanzada):** Aquí está la magia.  
     * Haz clic en "Añadir variable de entorno".  
     * **Nombre:** SES\_IDENTITY  
     * **Valor:** /ai-job-agent/prod/ses-identity  
     * **Tipo:** Parameter Store  
     * Repite este proceso para las otras dos variables:  
       * FRONTEND\_URL \-\> /ai-job-agent/prod/frontend-url  
       * ARTIFACT\_BUCKET \-\> /ai-job-agent/prod/artifact-bucket  
3. Haz clic en **"Continuar a CodePipeline"** y luego en **"Siguiente"**.

### **Paso 4: Configurar la Fase de Despliegue (Deploy)**

1. **Proveedor de despliegue:** Elige **AWS CloudFormation**.  
2. **Acción:** Crear o actualizar una pila.  
3. **Nombre de la pila:** AI-Job-Agent-Prod-Stack.  
4. **Nombre de artefacto:** BuildArtifact.  
5. **Nombre de archivo:** packaged.yaml.  
6. **Modo de plantilla:** Parámetros.  
7. **Anulaciones de parámetros (Parameter overrides):** Aquí le pasas los valores desde CodeBuild a CloudFormation.  
   * En la sección "Anulaciones de parámetros", escribe:

```
{
  "SESVerifiedIdentity" : "#{BuildVariables.SES_IDENTITY}",
  "FrontendProdURL" : "#{BuildVariables.FRONTEND_URL}"
}
```

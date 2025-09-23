# **Agente de Búsqueda de Empleo con IA (AI Job Search Agent)**

Este proyecto es un sistema serverless construido en AWS que automatiza y optimiza la búsqueda de empleo. El agente utiliza IA para analizar las vacantes en función del CV de un usuario, priorizarlas y generar informes personalizados.

## **Características Principales**

* **Configurable por el Usuario:** A través de una interfaz web, el usuario puede subir su CV, definir la frecuencia de los informes, el idioma y las plataformas a monitorear.  
* **Búsqueda Multi-Plataforma:** Agrega vacantes de sitios como LinkedIn, OCC Mundial y Computrabajo.  
* **Validación de URLs:** El sistema verifica que todos los enlaces a las vacantes estén activos antes de procesarlos, eliminando los enlaces rotos.  
* **Análisis con IA:** Utiliza Amazon Comprehend y Bedrock para analizar semánticamente cada vacante, extraer habilidades clave y calcular una puntuación de relevancia.  
* **Notificaciones Personalizadas:** Envía informes por correo electrónico con las mejores oportunidades, resúmenes generados por IA y borradores de mensajes de contacto.

## **Arquitectura en AWS**

El sistema utiliza una arquitectura serverless basada en eventos para ser eficiente, escalable y de bajo costo.

* **Frontend:** AWS Amplify para alojar la página de configuración.  
* **Base de Datos:** Amazon DynamoDB para almacenar las configuraciones de los usuarios y los resultados de las vacantes.  
* **Almacenamiento:** Amazon S3 para guardar los CVs de los usuarios.  
* **Cómputo:** AWS Lambda para todas las funciones de backend (recolección, análisis, notificación).  
* **IA y Machine Learning:** Amazon Comprehend para la extracción de entidades y Amazon Bedrock para la generación de texto.  
* **Programación:** Amazon EventBridge para ejecutar el agente según la frecuencia definida por el usuario.  
* **Notificaciones:** Amazon SES para enviar los informes por correo electrónico.

## **Estructura del Repositorio**

ai-job-agent/  
│  
├── frontend/             \# Interfaz de usuario  
├── infrastructure/       \# Scripts y plantillas de IaC  
└── src/                  \# Código fuente de las funciones Lambda

## **Puesta en Marcha (Setup)**

1. **Configurar Credenciales de AWS:** Asegúrate de tener tus credenciales de AWS configuradas en tu entorno local.  
2. **Crear la Base de Datos:** Ejecuta el script de Python en la carpeta infrastructure para crear las tablas de DynamoDB.  
   python infrastructure/create\_dynamodb\_tables.py

3. **Desplegar la Infraestructura:** Utiliza el AWS SAM CLI para desplegar la plantilla de CloudFormation.  
   sam build  
   sam deploy \--guided

4. **Configurar el Frontend:** Sube el archivo index.html a un servicio de hosting como AWS Amplify.

## **Uso**

1. Accede a la página web alojada.  
2. Introduce tu correo, sube tu CV y establece tus preferencias.  
3. Haz clic en "Activar Agente".  
4. Recibirás tu primer informe por correo según la frecuencia que hayas elegido.

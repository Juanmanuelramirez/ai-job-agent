import boto3
import os
from boto3.dynamodb.conditions import Key

# --- Configuration ---
JOB_LEADS_TABLE = os.environ.get('JOB_LEADS_TABLE_NAME', 'JobLeads')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'your-verified-email-in-ses@example.com')

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')
table = dynamodb.Table(JOB_LEADS_TABLE)

def generate_html_email(user_email, top_jobs):
    """Generates the HTML content for the report email."""
    # This function remains the same as your original version.
    # ... (omitted for brevity, assume it's the same as your file)
    # For this example, we'll create a simplified version
    body_html = f"<html><body><h1>Hi {user_email.split('@')[0]},</h1>"
    body_html += "<p>Your AI agent has analyzed the market. Here are your top opportunities today:</p>"
    
    for job in top_jobs:
        analysis_html = job.get('aiAnalysis', 'Not available.').replace('\n', '<br>')
        body_html += (
            f"<hr>"
            f"<h2>{job.get('title', 'No Title')} @ {job.get('company', 'No Company')}</h2>"
            f"<p><b>Validated URL:</b> <a href='{job['jobUrl']}'>{job['jobUrl']}</a></p>"
            f"<p><b>Relevance Score:</b> {job.get('relevanceScore', 'N/A')}%</p>"
            f"<h3>AI Analysis:</h3>"
            f"<div style='background-color:#f0f0f0; padding:10px; border-radius:5px;'>{analysis_html}</div>"
        )

    body_html += "<br><p>Good luck with your applications!</p></body></html>"
    return body_html


def lambda_handler(event, context):
    """
    This handler queries DynamoDB for the top job leads and sends an email.
    """
    user_email = event.get('user_email')
    if not user_email:
        print("Error: user_email not provided in the event.")
        return {'statusCode': 400, 'body': 'User email is missing.'}
        
    print(f"Preparing report for: {user_email}")

    try:
        # --- IMPROVED QUERY ---
        # This query now uses the Global Secondary Index for efficient sorting.
        response = table.query(
            IndexName='RelevanceScoreIndex',
            KeyConditionExpression=Key('userEmail').eq(user_email),
            ScanIndexForward=False,  # Sorts relevanceScore in descending order (highest first)
            Limit=5
        )
        top_jobs = response.get('Items', [])
        
    except Exception as e:
        print(f"Error querying DynamoDB with GSI: {e}")
        return {'statusCode': 500, 'body': 'Database query error.'}

    if not top_jobs:
        print(f"No high-relevance jobs found for {user_email}. No email will be sent.")
        return {'statusCode': 200, 'body': 'No report to send.'}

    # Generate and send the email
    email_html_body = generate_html_email(user_email, top_jobs)
    
    try:
        ses.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': [user_email]},
            Message={
                'Subject': {'Data': 'Your Daily AI Job Report'},
                'Body': {'Html': {'Data': email_html_body}}
            }
        )
        print(f"Report email sent successfully to {user_email}.")
    except Exception as e:
        print(f"Error sending email with SES: {e}")
        return {'statusCode': 500, 'body': 'Error sending email.'}

    return {'statusCode': 200, 'body': 'Report sent successfully.'}


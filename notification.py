# notification module
# This module is responsible for sending notifications to the user when the charger is toggled on or off

import os
import json
import requests
with open('credentials.json', 'r') as f:
    credentials = json.load(f)
# email module
# This module is responsible for sending emails to the user when the charger is toggled on or off

# The email address and password of the sender
email_address = credentials["email"]["email"]
email_password = credentials["email"]["password"]
host = credentials["email"]["host"]
# The email address of the recipient

# The subject of the email
subject = "Charger status update"

# The body of the email
body = "The charger has been toggled on or off"

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, body, is_charging_on, recipient_email):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = email_address
    msg['To'] = recipient_email

    # Update the charging status dynamically in the email body
    charging_status = "AAN" if is_charging_on else "UIT"
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; }}
            .container {{ background-color: #fff; padding: 20px; }}
            .header {{ background-color: #000; color: #0078d6; padding: 10px; text-align: center; }}
            .body {{ padding: 10px; }}
            .footer {{ background-color: #000; color: #fff; padding: 10px; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">Mercedes A250 Oplader automatisatie</div>
            <div class="body">
                <p>{body}</p>
                <p>Charger status: <strong style="color: #0078d6;">{charging_status}</strong></p>
            </div>
            <div class="footer">This is an automated message, please do not reply.</div>
        </div>
    </body>
    </html>
    """

    part1 = MIMEText(body, 'plain')
    part2 = MIMEText(html, 'html')

    msg.attach(part1)
    msg.attach(part2)

    try:
        # Use SMTP_SSL for SSL. Change to smtplib.SMTP if using TLS on port 587.
        server = smtplib.SMTP_SSL(host, 465)
        server.login(email_address, email_password)
        server.sendmail(email_address, recipient_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


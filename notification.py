# notification module
# This module is responsible for sending notifications to the user when the charger is toggled on or off

import os
import json
from discord_webhook import DiscordEmbed, DiscordWebhook
import requests
with open('credentials.json', 'r') as f:
    credentials = json.load(f)
# email module
# This module is responsible for sending emails to the user when the charger is toggled on or off

# The email address and password of the sender
email_address = credentials["email"]["email"]
email_password = credentials["email"]["password"]
host = credentials["email"]["host"]
port = credentials["email"]["port"]
dc_webhook = credentials["discord"]["webhook"]
dc_username = credentials["discord"]["username"]
dc_avatar = credentials["discord"]["avatar"]
dc_color = credentials["discord"]["color"]
# The email address of the recipient

# The subject of the email
subject = "Charger status update"

# The body of the email
body = "The charger has been toggled on or off"

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(body, is_charging_on, recipient_email, subject="[AUTO] Oplader status update"):
    msg = MIMEMultipart('alternative')
    # place [AUTO] in front of the subject if it's not already there
    msg['Subject'] = subject if subject.startswith("[AUTO]") else f"[AUTO] {subject}"
    msg['From'] = email_address
    msg['To'] = recipient_email

    # Update the charging status dynamically in the email body
    charging_status = "AAN" if is_charging_on else "UIT"
    html = f"""
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                margin: 0;
                padding: 0;
                color: #333;
                background-color: #f4f4f4;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #fff;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }}
            .header {{
                background-color: #0078d6;
                color: #ffffff;
                padding: 20px;
                text-align: center;
                font-size: 24px;
            }}
            .body {{
                padding: 20px;
                line-height: 1.6;
                text-align: center;
            }}
            .status {{
                color: #0078d6;
                font-weight: bold;
            }}
            .footer {{
                background-color: #333;
                color: #ffffffc0;
                padding: 10px;
                text-align: center;
                font-size: 13px;
            }}
            a {{
                color: #0078d6;
                text-decoration: none;
                display: block;
                text-align: center;
                font-size: 10px;
                background-color: #333;
                padding-bottom: 10px;
                padding-top: 5px;
            }}

            /*dark mode*/
            @media (prefers-color-scheme: dark) {{
                body {{
                    color: #fff;
                    background-color: #000000;
                }}
                .container {{
                    background-color: #444;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }}
                .header {{
                    background-color: #0078d6;
                }}
                .footer {{
                    background-color: #222;
                }}
                a {{
                    color: #0078d6;
                    background-color: #222;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">Mercedes A250 Charger Automation</div>
            <div class="body">
                <p>Hey,</p>
                <p>{body}</p>
                <p>De lader staat <span class="status">{charging_status}</span></p>
            </div>
            <div class="footer"><i>Automatisch gegenereerde e-mail. Reageren is niet mogelijk.</i></div>
            <a href="http://192.168.0.125/settings">Afmelden</a>
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
        send_webhook(subject.replace("[AUTO] ",""), f"{body}", status="on" if is_charging_on else "off")
        server = smtplib.SMTP_SSL(host, port)
        server.login(email_address, email_password)
        server.sendmail(email_address, recipient_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_webhook(title:str, message:str, color:str=dc_color, status:str="on"):
    webhook = DiscordWebhook(url=dc_webhook, username=dc_username, avatar_url=dc_avatar)
    embed = DiscordEmbed(title=f"{title}", description=f"{message}", color=f"{color if status.lower() == 'on' else 'ff0000'}")
    embed.set_timestamp()
    embed.set_footer(text=dc_username+" | "+ "Status: AAN⚡" if status.lower() == "on" else dc_username+" | "+ "STATUS: UIT⌛", icon_url=dc_avatar)

    # add embed object to webhook
    webhook.add_embed(embed)

    response = webhook.execute()
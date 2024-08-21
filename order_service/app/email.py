import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from MongoDB import mongodb

smtp_server = 'smtp.gmail.com'
smtp_port = 587
sender_email = 'sample@gmail.com'
sender_password = '12345678'

subject = 'Daily Order Logs'
body = 'This is the body of the email.'

def send_mail(recipient_email, subject, body):
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject

    message.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()

        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())

        print("Email sent successfully")

    except Exception as e:
        print(f"Failed to send email: {e}")

    finally:
        server.quit()
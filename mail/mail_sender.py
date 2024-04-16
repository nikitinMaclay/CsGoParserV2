import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_mail_message(message_body):
    try:
        sender_email = "nic1tin-maclay@yandex.ru"
        sender_password = "vjytwojntpkwfnze"

        recipient_email = "nic1tin-maclay@yandex.ru"
        subject = "-----"

        body = message_body

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.yandex.ru", 587) as server:
            server.starttls()

            server.login(sender_email, sender_password)

            server.send_message(message)

        print("Сообщение успешно отправлено!")
    except Exception as e:
        print("Сообщение не отправлено")
        print(e)

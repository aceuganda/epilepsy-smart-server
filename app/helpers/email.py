import os
from flask_mail import Mail, Message
from threading import Thread

mail = Mail()


def async_mail(app, message):
    with app.app_context():
        mail.send(message)


def send_email(to, subject, template, sender, app):
    msg = Message(
        f'[Epilepsy App] {subject}',
        recipients=[to],
        html=template,
        sender=sender,
    )
    Thread(target=async_mail, args=(app, msg)).start()

from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail


def send_async_mail(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, reply_to=None, **kwargs):
    app = current_app._get_current_object()

    msg = Message(subject=app.config['MAIL_SUBJECT_PREFIX'] + subject, sender=app.config['MAIL_SENDER'], \
        reply_to=reply_to, recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    print(f'the message sender is: {msg.sender}')

    #async email
    thr = Thread(target=send_async_mail, args=[app, msg])
    thr.start()
    return thr

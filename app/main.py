"""
Base blueprint for flask app, returning main site functionality
"""
from . import forms
from .app_mail import send_email

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/visual-thesaurus')
def visual_thesaurus():
    return redirect('http://localhost:3000/')


@bp.route('/blog')
def blog():
    pass


@bp.route('/videos')
def videos():
    return render_template('video.html')


@bp.route('/about')
def about():
    pass


@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = forms.ContactForm()

    if request.method == 'POST' and form.validate_on_submit():
        app = current_app

        print('Form was Submitted!')
        print(f'Name: {form.name.data}')
        print(f'Email: {form.email.data}')
        print(f'Message: {form.message.data}')
        send_email(app.config['APP_ADMIN_MAIL'], f'New Message from {form.name.data}', 'mail/contact', \
            reply_to=form.email.data, message_text=form.message.data, name=form.name.data)
        return redirect(url_for('index'))

    return render_template('contact.html', form=form)

@bp.route('/newsletter-signup')
def newsletter_signup():
    form = forms.NewsletterForm()
    return render_template('newsletter_form.html', form=form)

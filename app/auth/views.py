from flask import render_template, request, url_for, redirect, flash
from flask_login import (
    login_user, logout_user, login_required, current_user
)
from . import auth
from .. import db
from ..models import User
from .forms import (
    LoginForm, RegistrationForm, EditPasswordForm, EditUserInfo,
    EditEmailForm
)
from ..app_mail import send_email

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')

            # Require a relative url to prevent malicious users from 
            # using this to redirect to an external site
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)

    print('signin page reached or failed')
    flash('Invalid username or password')

    return render_template('auth/login.html', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    print('user has been logged out.')
    flash('You have successfully logged out')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data,
            first_name=form.first_name.data, last_name=form.last_name.data,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
            'auth/email/confirm', user=user, token=token)
        print('a confirmation email has been sent')
        flash('A confirmation email has been sent to the email you provided - please follow link in email to finish updating your email address.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('Thanks! Your account is confirmed.')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.route('/update-email/<token>')
@login_required
def update_email(token):

    if current_user.confirm(token):
        db.session.commit()
        flash('Thanks! Your email address is updated.')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.route('/edit-account', methods=['GET', 'POST'])
@login_required
def edit_account():
    password_form = EditPasswordForm()
    info_form = EditUserInfo()
    email_form = EditEmailForm()

    # change password
    #TODO: create email template
    if password_form.validate_on_submit():
        if current_user.verify_password(password_form.old_password.data):
            current_user.password = password_form.new_password.data
            flash('Successfully changed password.')
            send_email(current_user.email, 'Password Changed',
                'auth/email/password_changed', user=current_user)
            return redirect(url_for('auth.edit_account'))
        flash('Invalid password.')
        return redirect(url_for('auth.edit_account'))

    # change general bio info
    elif info_form.validate_on_submit():
        if info_form.first_name.data != '':
            current_user.first_name = info_form.first_name.data
        if info_form.last_name.data != '':
            current_user.last_name = info_form.last_name.data
        if info_form.bio.data != '':
            current_user.bio = info_form.bio.data
        if info_form.location.data != '':
            current_user.location = info_form.location.data
        if info_form.username.data != '':
            current_user.username = info_form.username.data
        db.session.add(current_user)
        db.session.commit()
        flash('Successfully updated your information.')
        return redirect(url_for('auth.edit_account'))

    # change email
    #TODO: how to pass email to update_email view? database table or token?
    #TODO: create email template
    elif email_form.validate_on_submit():
        flash('Confirmation email sent to the email you provided - please follow link in email to finish updating your email address.')
        token = current_user.generate_confirmation_token()
        send_email(current_user.email, 'Confirm Updated Email',
            'auth/email/email-update', user=current_user, token=token)
        print('a confirmation email has been sent')
        flash('A confirmation email has been sent to the email you provided.')
        return redirect(url_for('auth.edit_account'))

    return render_template(
        'auth/edit_account.html', user=current_user,
        password_form=password_form, info_form=info_form,
        email_form=email_form
    )
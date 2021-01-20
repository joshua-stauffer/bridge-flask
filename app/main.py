"""
Base blueprint for flask app, returning main site functionality
"""
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, 
    current_app, send_from_directory, abort
)
from . import forms
from .models import Video, Post, Resource, Node
from .app_mail import send_email


bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    page = 'home'
    return render_template('index.html', page=page)


@bp.route('/visual-thesaurus')
def visual_thesaurus():
    return render_template('thesaurus.html')


@bp.route('/alt-thesaurus')
def alt_thesaurus():
    term = Node.get_alt_term(None)
    page = 'thesaurus'
    return render_template('alt_thesaurus.html', term=term, page=page)


@bp.route('/alt-thesaurus-<id>')
def alt_thesaurus_by_id(id):
    term = Node.get_alt_term(id)
    page = 'thesaurus'
    return render_template('alt_thesaurus.html', term=term, page=page)


@bp.route('/blog-<post_id>', methods=['GET'])
def blog(post_id):
    page = 'blog'
    if post_id == '0':
        response = Post.get_most_recent()
    else:
        response = Post.get_by_id(post_id)

    return render_template(
            'blog.html', 
            post_content=response.content,
            post_metadata=response.metadata,
            prev_post_id=response.prev_post_id,
            next_post_id=response.next_post_id,
            page=page
        )


@bp.route('/blog', methods=['GET'])
def blog_index():
    page = 'blog'

    posts = Post.get_all()
    return render_template('blog_index.html', posts=posts, page=page)


@bp.route('/resources', methods=['GET'])
def resources():
    resources = Resource.get_all()
    page = 'resources'
    return render_template('resources.html', resources=resources, page=page)


@bp.route('/videos')
def videos():
    video_list = Video.get_all()
    page = 'videos'
    return render_template('videos.html', video_list=video_list, page=page)


@bp.route('/about')
def about():
    page = 'about'
    return render_template('about.html', page=page)


@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = forms.ContactForm()
    page = 'contact'

    if request.method == 'POST' and form.validate_on_submit():
        app = current_app

        app.logger.info(f'Form was submitted: Name {form.name.data} Email {form.email.data} Message {form.message.data}')
        send_email(app.config['MAIL_DEFAULT_SENDER'], f'New Message from {form.name.data}', 'mail/contact', \
            reply_to=form.email.data, message_text=form.message.data, name=form.name.data)
        return redirect((url_for('.msg_confirm')))

    return render_template('contact.html', form=form, page=page)


@bp.route('/msg-confirm')
def msg_confirm():
    return render_template('msg_confirm.html')


@bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@bp.app_errorhandler(404)
def not_found(e):
    current_app.logger.info(f'404 Error: {e}')
    return render_template('404.html')

@bp.app_errorhandler(500)
def internal_server_error(e):
    current_app.logger.error(f'500 Error: {e}')
    return render_template('500.html')

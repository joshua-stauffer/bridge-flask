"""
Base blueprint for flask app, returning main site functionality
"""
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from . import forms
from .models import Video, Post, Resource
from .app_mail import send_email


bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    page = 'home'
    return render_template('index.html', page=page)


@bp.route('/visual-thesaurus')
def visual_thesaurus():
    return redirect('http://localhost:3000/visual-thesaurus')


@bp.route('/blog-<post_id>', methods=['GET'])
def blog(post_id):
    page = 'blog'
    print('got post id ', post_id)
    if post_id == '0':
        response = Post.get_most_recent()
    else:
        response = Post.get_by_id(post_id)

    print('content is: ', response.content)

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

        print('Form was Submitted!')
        print(f'Name: {form.name.data}')
        print(f'Email: {form.email.data}')
        print(f'Message: {form.message.data}')
        send_email(app.config['APP_ADMIN_MAIL'], f'New Message from {form.name.data}', 'mail/contact', \
            reply_to=form.email.data, message_text=form.message.data, name=form.name.data)
        return redirect(url_for('index'))

    return render_template('contact.html', form=form, page=page)

@bp.route('/newsletter-signup')
def newsletter_signup():
    form = forms.NewsletterForm()
    return render_template('newsletter_form.html', form=form)

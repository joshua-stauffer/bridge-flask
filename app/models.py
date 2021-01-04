
from datetime import datetime
from flask import current_app, request, url_for, abort
from flask_login import UserMixin
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from . import db
from . import login_manager
from .utils.blog_tuple import BlogResponse
from .utils.constants import empty_blog_error, empty_resources_error, empty_video_error
from .utils.get_preview_text import get_preview_text
from .utils.prettify_date import prettify_date
from .utils.to_json import node_to_json


# relationship goes in parent
# foreign key goes in the child class


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), index=True, nullable=False)
    username = db.Column(db.String(32), index=True, nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post', backref='user')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=86400):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    # add password reset

    def __repr__(self):
        return f'{self.first_name} {self.last_name}'


class Quote(db.Model):
    __tablename__ = 'quotes'
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(128), nullable=False)
    text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'"{self.text}" \n-{self.author}'

    # API access point
    @staticmethod
    def to_dict_list():
        return [
            {'author': q.author, 'text': q.text}
            for q in Quote.query.all()
        ]


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(User.id))
    title = db.Column(db.String(128), nullable=False)
    sub_title = db.Column(db.String(128), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, nullable=True)
    contents = db.relationship('PostContents', backref='post')
    published = db.Column(db.Boolean)

    @property
    def pub_date(self):
        return prettify_date(self.date_created)

    @property
    def edit_date(self):
        return prettify_date(self.date_updated)

    def update_timestamp(self):
        self.date_updated = datetime.utcnow()

    def get_contents(self):
        """returns a list of dicts for each content element of given post"""
        post_contents = [p.to_json() for p in self.contents]
        post_contents.sort(key=lambda p: p['order'])
        return post_contents

    def get_metadata(self):
        return {
            'author': f'{self.user.first_name} {self.user.last_name}',
            'pub_date': self.pub_date,
            'updated': self.edit_date,
            'title': self.title,
            'subtitle': self.sub_title
        }

    def __repr__(self):
        return f'{self.title} - {self.pub_date} - {self.user.first_name} {self.user.last_name}'

    @classmethod
    def get_all(cls):
        return [
                {
                    'author': f'{p.user.first_name} {p.user.last_name}',
                    'title': p.title,
                    'pub_date': p.pub_date,
                    'text': get_preview_text(' '.join(
                        [c.payload for c in p.contents if c.content_type == 'p']
                    ), max_char_count=200),
                    'id': p.id
                }
                for p in cls.query.order_by(Post.date_created).all()
            ]

    @classmethod
    def get_all_published_posts(cls):
        # This should maybe just return titles and links (ids)
        posts = cls.query \
                    .filter_by(published=True) \
                    .order_by(Post.date_created) \
                    .all()
        return [post.get_contents() for post in posts]

    @classmethod
    def get_most_recent(cls):
        print('entered get most recent')
        
        posts = cls.query.order_by(Post.date_created).all()
        if not posts:
            content = empty_blog_error
            metadata = None
            prev_post_id = None
        else:
            latest_post = posts[-1]
            content = latest_post.get_contents()
            metadata = latest_post.get_metadata()
        
            if len(posts) > 1:
                prev_post_id = posts[-2].id
            else:
                prev_post_id = None

        return BlogResponse(
            content=content,
            metadata=metadata,
            prev_post_id=prev_post_id
        )

    @classmethod
    def get_by_id(cls, id):
        post = cls.query.filter_by(id=id).first_or_404()
        post_id_by_date = [p.id for p in cls.query.order_by(Post.date_created).all()]
        print(f' all posts: {post_id_by_date}')
        post_index = post_id_by_date.index(int(id))
        if post_index == 0:
            prev_post_id = None
        else:
            prev_post_id = post_id_by_date[post_index - 1]
        if post_index == len(post_id_by_date) - 1:
            next_post_id = None
        else:
            next_post_id = post_id_by_date[post_index + 1]
        content = post.get_contents()
        metadata = post.get_metadata()
        return BlogResponse(
            content=content,
            metadata=metadata,
            prev_post_id=prev_post_id,
            next_post_id=next_post_id
        )


class PostContents(db.Model):
    __tablename__ = 'post_contents'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey(Post.id))
    order = db.Column(db.Integer)
    content_type = db.Column(db.String(8))
    payload = db.Column(db.Text)
    uri = db.Column(db.String(128))
    css = db.Column(db.String(128))

    def to_json(self):
        return {
            'id': self.id,
            'order': self.order,
            'type': self.content_type,
            'payload': self.payload,
            'uri': self.uri,
            'css': self.css
        }


class Node(db.Model):
    """
    params:
        title: string, max-length 32, required
        definition: string
        example: string
        synonyms: list
        antonyms: list
    methods:
        add_synonym(string: <value_to_add>)
        add_antonym(string: <value_to_add>)
        del_synonym(int: <index_to_delete>)
        del_antonym(int: <index_to_delete>)
    """
    __tablename__ = 'nodes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32), nullable=False)
    definition = db.Column(db.Text(), nullable=True)
    example = db.Column(db.Text(), nullable=True)

    _synonyms = db.Column(db.Text(), nullable=True)
    _antonyms = db.Column(db.Text(), nullable=True)

    # methods for getting and setting synonyms and antonyms
    @property
    def synonyms(self):
        if self._synonyms:
            return self._synonyms.split(',')
        return []
    
    def add_synonym(self, value):
        if self._synonyms:
            self._synonyms += ',' + value
        else:
            self._synonyms = value
        print(f'synonyms is now {self._synonyms}')

    def del_synonym(self, index):
        if not self._synonyms:
            print('no synonyms to delete')
            return False
        if index > len(self.synonyms):
            raise IndexError()
        updated_synonyms = self.synonyms
        del updated_synonyms[index]
        self._synonyms = ''
        for w in updated_synonyms:
            self.add_synonym(w)
        return True

    @property
    def antonyms(self):
        if self._antonyms:
            return self._antonyms.split(',')
        return []
    
    def add_antonym(self, value):
        if self._antonyms:
            self._antonyms += ',' + value
        else:
            self._antonyms = value
        print(f'antonyms is now {self._antonyms}')

    def del_antonym(self, index):
        if not self._antonyms:
            print('no antonyms to delete')
            return False
        if index > len(self.antonyms):
            raise IndexError()
        updated_antonyms = self.antonyms
        del updated_antonyms[index]
        self._antonyms = ''
        for w in updated_antonyms:
            self.add_synonym(w)
        return True

    def __repr__(self):
        return f'{self.title}\nSynonyms: {self.synonyms}\nAntonyms: {self.antonyms}'

    # API access point
    @staticmethod
    def to_dict():
        """Returns a dictionary of all available Node data."""
        data = Node.query.all()
        return {d.title: node_to_json(d) for d in data}


class Video(db.Model):
    __tablename__ = 'videos'
    id = db.Column(db.Integer, primary_key=True)
    order = db.Column(db.Integer)
    url = db.Column(db.String(128))
    title = db.Column(db.String(128))
    description = db.Column(db.Text())

    def to_json(self):
        return {
            'url': self.url,
            'title': self.title,
            'description': self.description
        }

    @classmethod
    def get_all(cls):
        video_list = cls.query.order_by(Video.order).all()
        return [video.to_json() for video in video_list]


class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    text = db.Column(db.Text())
    order = db.Column(db.Integer)
    uri = db.Column(db.String(128))
    uri_title = db.Column(db.String(128))

    @classmethod
    def get_all(cls):
        results =  [{
            'title': r.title,
            'text': r.text,
            'id': r.id,
            'order': r.order,
            'uri': r.uri,
            'uri_title': r.uri_title
        } for r in cls.query.order_by(Resource.order).all()]

        if not len(results):
            return [empty_resources_error]
        return results


# user loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
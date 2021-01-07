
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
    author = db.Column(db.String(128), nullable=True, default='')
    text = db.Column(db.Text, nullable=True, default='')
    published = db.Column(db.Boolean, default=False)

    def to_json(self):
        return {
            'id': self.id,
            'author': self.author,
            'text': self.text,
            'published': self.published
        }

    def __repr__(self):
        return f'"{self.text}" \n-{self.author}'

    # dashboard api methods
    @classmethod
    def get_all_private(cls):
        return [
            {
                'secondary': q.author, 
                'primary': get_preview_text(q.text, 50),
                'id': q.id,
                'published': q.published
            } for q in cls.query.all()]

    @classmethod
    def get_by_id(cls, id):
        quote = cls.query.filter_by(id=id).first_or_404()
        return quote.to_json()

    @classmethod
    def delete(cls, id):
        quote = cls.query.filter_by(id=id).first_or_404()
        db.session.delete(quote)
        db.session.commit()

    @classmethod
    def update_by_id(cls, id, data):
        quote = cls.query.filter_by(id=id).first_or_404()

        # could do this more programatically, but prefer the explicit approach for now
        quote.text = data['text']
        quote.author = data['author']
        quote.published = data['published']

        db.session.add(quote)
        db.session.commit()

        # remember, this needs to return the object
        return quote.to_json()

    @classmethod
    def update_batch(cls, data):
        edited_quotes = list()
        for d in data:
            quote = cls.query.filter_by(id=d.id).first_or_404()
            quote.text = d['text']
            quote.author = d['author']
            quote.published = d['published']
            edited_quotes.append(quote)

        db.session.add_all(edited_quotes)
        db.session.commit()

    @classmethod
    def new(cls):
        quote = cls()
        db.session.add(quote)
        db.session.commit()
""" 

    # old API access point
    @classmethod
    def to_dict_list(cls):
        return [
            {'author': q.author, 'text': q.text, 'id': q.id}
            for q in cls.query.all()
        ]

    @classmethod
    def get_edit_list(cls):
        return [
            {
                'secondary': q.author, 
                'primary': get_preview_text(q.text, 50),
                'id': q.id,
                'published': q.published
            } for q in cls.query.all()
        ]

    @classmethod
    def get_by_id(cls, id):
        quote = cls.query.filter_by(id=id).first_or_404()
        return {
            'id': quote.id,
            'text': quote.text,
            'author': quote.author,
            'published': quote.published
        }

    @classmethod
    def get_new(cls):
        new_quote = cls()
        db.session.add(new_quote)
        db.session.commit()
        return {
            'id': new_quote.id,
            'text': new_quote.text,
            'author': new_quote.author,
            'published': new_quote.published
        }

    @classmethod
    def delete(cls, id):
        quote = cls.query.filter_by(id=id).first_or_404()
        db.session.delete(quote)
        db.session.commit()

    @classmethod
    def save(cls, data):
        quote = cls.query.filter_by(id=data['id']).first_or_404()
        quote.published = data['published']
        quote.author = data['author']
        quote.text = data['text']
        db.session.add(quote)
        db.session.commit()
        return {
            'id': quote.id,
            'text': quote.text,
            'author': quote.author,
            'published': quote.published }
 """       


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(User.id))
    title = db.Column(db.String(128), nullable=True, default='')
    sub_title = db.Column(db.String(128), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, nullable=True)
    contents = db.relationship('PostContents', backref='post')
    published = db.Column(db.Boolean, default=False)

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
    payload = db.Column(db.Text, default='')
    uri = db.Column(db.String(128))
    css = db.Column(db.String(128))
    published = db.Column(db.Boolean, default=False)

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
    title = db.Column(db.String(32), nullable=True, default='')
    definition = db.Column(db.Text(), nullable=True, default='')
    example = db.Column(db.Text(), nullable=True, default='')
    published = db.Column(db.Boolean, default=False)

    _synonyms = db.Column(db.Text(), nullable=True)
    _antonyms = db.Column(db.Text(), nullable=True)
    # methods for getting and setting synonyms and antonyms
    # both synonyms and antonyms can be treated as a list, and 
    # internally will be converted to/from a comma separated string
    @property
    def synonyms(self):
        if self._synonyms:
            return self._synonyms.split(',')
        return []

    @synonyms.setter
    def synonyms(self, synonyms_list):
        self._synonyms = ','.join(synonyms_list)
    
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

    @antonyms.setter
    def antonyms(self, antonyms_list):
        self._antonyms = ','.join(antonyms_list)
    
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
            self.add_antonym(w)
        return True

    def __repr__(self):
        return f'{self.title}\nSynonyms: {self.synonyms}\nAntonyms: {self.antonyms}'

    # create text property so api is consistent
    @property
    def text(self):
        return self.definition

    @text.setter
    def text(self, val):
        self.definition = val

    def to_json(self):
        word_list = Node.get_all_words()
        return {
            'id': self.id,
            'title': self.title,
            'text': self.text,
            'example': self.example,
            'published': self.published,
            'synonyms': self.synonyms,
            'antonyms': self.antonyms,
            'word_list': word_list
        }

    # API access point
    @classmethod
    def to_dict(cls):
        """Returns a dictionary of all available Node data."""
        data = cls.query.all()
        return {d.title: node_to_json(d) for d in data}

    # dashboard api methods
    @classmethod
    def get_all_private(cls):
        return [
            {
                'secondary': d.title, 
                'primary': get_preview_text(d.text, 50),
                'id': d.id,
                'published': d.published
            } for d in cls.query.all()]

    @classmethod
    def get_by_id(cls, id):
        node = cls.query.filter_by(id=id).first_or_404()
        return node.to_json()

    @classmethod
    def delete(cls, id):
        node = cls.query.filter_by(id=id).first_or_404()
        db.session.delete(node)
        db.session.commit()

    @classmethod
    def update_by_id(cls, id, data):
        node = cls.query.filter_by(id=id).first_or_404()

        # could do this more programatically, but prefer the explicit approach for now
        node.title = data['title']
        node.text = data['text']
        node.published = data['published']
        node.example = data['example']
        node.synonyms = data['synonyms']
        node.antonyms = data['antonyms']

        db.session.add(node)
        db.session.commit()
    
        # remember, this view needs to return the saved item
        return node.to_json()
        

    @classmethod
    def update_batch(cls, data):
        edited_nodes = list()
        for d in data:
            node = cls.query.filter_by(id=d.id).first_or_404()
            node.title = data['title']
            node.text = data['text']
            node.published = data['published']
            node.example = data['example']
            node.synonyms = data['synonyms']
            node.antonyms = data['antonyms']
            edited_nodes.append(node)

        db.session.add_all(edited_nodes)
        db.session.commit()

    @classmethod
    def new(cls):
        node = cls()
        db.session.add(node)
        db.session.commit()

    @classmethod
    def get_all_words(cls):
        return [w.title for w in cls.query.all()]


class Video(db.Model):
    __tablename__ = 'videos'
    id = db.Column(db.Integer, primary_key=True)
    order = db.Column(db.Integer)
    url = db.Column(db.String(128), default='')
    title = db.Column(db.String(128), default='')
    description = db.Column(db.Text(), default='')
    published = db.Column(db.Boolean, default=False)

    @property
    def text(self):
        return self.description

    @text.setter
    def text(self, val):
        self.description = val

    def to_json(self):
        return {
            'id': self.id,
            'uri': self.url,
            'title': self.title,
            'text': self.description,
            'published': self.published,
        }

    @classmethod
    def get_all(cls):
        video_list = cls.query.order_by(Video.order).all()
        return [video.to_json() for video in video_list]


    # dashboard api methods
    @classmethod
    def get_all_private(cls):
        return [
            {
                'secondary': v.title, 
                'primary': get_preview_text(v.text, 50),
                'id': v.id,
                'published': v.published
            } for v in cls.query.all()]

    @classmethod
    def get_by_id(cls, id):
        video = cls.query.filter_by(id=id).first_or_404()
        return video.to_json()

    @classmethod
    def delete(cls, id):
        video = cls.query.filter_by(id=id).first_or_404()
        db.session.delete(video)
        db.session.commit()

    @classmethod
    def update_by_id(cls, id, data):
        video = cls.query.filter_by(id=id).first_or_404()

        # could do this more programatically, but prefer the explicit approach for now
        video.title = data['title']
        video.text = data['text']
        video.url = data['uri']
        video.published = data['published']

        db.session.add(video)
        db.session.commit()
    
        # remember, this view needs to return the saved item
        return video.to_json()
        

    @classmethod
    def update_batch(cls, data):
        edited_videos = list()
        for d in data:
            video = cls.query.filter_by(id=d.id).first_or_404()
            video.title = d['title']
            video.text = d['text']
            video.order = d['order']
            video.uri = d['uri']
            video.uri_title = d['uri_title']
            video.published = d['published']
            edited_videos.append(video)

        db.session.add_all(edited_videos)
        db.session.commit()

    @classmethod
    def new(cls):
        video = cls()
        db.session.add(video)
        db.session.commit()

    @classmethod
    def new_by_order(cls, order_id):
        cur_videos = cls.query.all()
        for r in cur_videos:
            if r.order >= order_id:
                r.order += 1
        new_video = cls(order=order_id)
        db.session.add_all([*cur_videos, new_video])
        db.session.commit()


class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), default='')
    text = db.Column(db.Text(), default='')
    order = db.Column(db.Integer)
    uri = db.Column(db.String(128), default='')
    uri_title = db.Column(db.String(128), default='')
    published = db.Column(db.Boolean, default=False)

    def to_json(self):
        return {
            'title': self.title,
            'id': self.id,
            'text': self.text,
            'order': self.order,
            'uri': self.uri,
            'uri_title': self.uri_title,
            'published': self.published
        }

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

    # dashboard api methods
    @classmethod
    def get_all_private(cls):
        return [
            {
                'secondary': r.title, 
                'primary': get_preview_text(r.text, 50),
                'id': r.id,
                'published': r.published
            } for r in cls.query.all()]

    @classmethod
    def get_by_id(cls, id):
        resource = cls.query.filter_by(id=id).first_or_404()
        return resource.to_json()

    @classmethod
    def delete(cls, id):
        resource = cls.query.filter_by(id=id).first_or_404()
        db.session.delete(resource)
        db.session.commit()

    @classmethod
    def update_by_id(cls, id, data):
        resource = cls.query.filter_by(id=id).first_or_404()

        # could do this more programatically, but prefer the explicit approach for now
        resource.title = data['title']
        resource.text = data['text']
        resource.order = data['order']
        resource.uri = data['uri']
        resource.uri_title = data['uri_title']
        resource.published = data['published']

        db.session.add(resource)
        db.session.commit()

        # remember, this view needs to return the saved item
        return resource.to_json()


    @classmethod
    def update_batch(cls, data):
        edited_resources = list()
        for d in data:
            resource = cls.query.filter_by(id=d.id).first_or_404()
            resource.title = d['title']
            resource.text = d['text']
            resource.order = d['order']
            resource.uri = d['uri']
            resource.uri_title = d['uri_title']
            resource.published = d['published']
            edited_resources.append(resource)

        db.session.add_all(edited_resources)
        db.session.commit()

    @classmethod
    def new(cls):
        resource = cls()
        db.session.add(resource)
        db.session.commit()

    @classmethod
    def new_by_order(cls, order_id):
        cur_resources = cls.query.all()
        for r in cur_resources:
            if r.order >= order_id:
                r.order += 1
        new_resource = cls(order=order_id)
        db.session.add_all([*cur_resources, new_resource])
        db.session.commit()


# user loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
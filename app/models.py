
from datetime import datetime
from flask import current_app, request, url_for, abort

from . import db, guard

from .utils.blog_tuple import BlogResponse
from .utils.get_preview_text import get_preview_text
from .utils.prettify_date import prettify_date
from .utils.to_json import node_to_json


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), index=True, nullable=False)
    username = db.Column(db.String(32), index=True, nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    password_hash = db.Column(db.Text)
    confirmed = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post', backref='user')
    roles = db.Column(db.String(64))
    is_active = db.Column(db.Boolean, default=True)

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, password):
        self.password_hash = guard.hash_password(password)

    @property
    def identity(self):
        return self.id

    @classmethod
    def lookup(cls, username):
        return cls.query.filter_by(username=username).first_or_404()

    @classmethod
    def identify(cls, id):
        return cls.query.get(id)

    def is_valid(self):
        return self.is_active

    @property
    def rolenames(self):
        try:
            return self.roles.split(',')
        except Exception:
            return []

    def __repr__(self):
        return f'{self.first_name} {self.last_name}'


class APIMixin:
    """
    Defines an API for the view to access models.
    Requires that models have an id (int) and order (int) fields defined.
    Individual models must define to_json, get_all_private, and update_by_id with their own logic.
    """

    def to_json(self):
        pass
    
    @classmethod
    def get_all_private(cls):
        pass

    @classmethod
    def update_by_id(cls, id, data):
        pass

    @classmethod
    def get_by_id(cls, id):
        entry = cls.query.filter_by(id=id).first_or_404()
        return entry.to_json()

    @classmethod
    def get_by_order(cls, order):
        entry = cls.query.filter_by(order=order).first_or_404()
        return entry.to_json()

    @classmethod
    def delete(cls, id):
        to_del = cls.query.filter_by(id=id).first_or_404()
        order = to_del.order
        entries = [
            r for r in cls.query.all()
            if r.id != id and r.order > order
        ]
        for r in entries:
            r.order -= 1
        db.session.delete(to_del)
        db.session.add_all(entries)
        db.session.commit()

    @classmethod
    def update_batch(cls, data):
        edited_entries = list()
        for d in data:
            entry = cls.query.filter_by(id=d['id']).first_or_404()
            entry.order = d['order']
            edited_entries.append(entry)

        db.session.add_all(edited_entries)
        db.session.commit()

    @classmethod
    def new(cls):
        entry = cls()
        db.session.add(entry)
        db.session.commit()

    @classmethod
    def new_by_order(cls, order_id):
        order = int(order_id)
        current = cls.query.all()
        for entry in current:
            if entry.order >= order:
                entry.order += 1
        new_entry = cls(order=order)
        db.session.add_all([*current, new_entry])
        db.session.commit()


class Quote(APIMixin, db.Model):
    __tablename__ = 'quotes'
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(128), nullable=True, default='')
    text = db.Column(db.Text, nullable=True, default='')
    published = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer)

    def to_json(self):
        return {
            'id': self.id,
            'author': self.author,
            'text': self.text,
            'published': self.published,
            'order': self.order
        }

    def __repr__(self):
        return f'"{self.text}" \n-{self.author}'

    @classmethod
    def to_dict_list(cls):
        return [
            {'author': q.author, 'text': q.text, 'id': q.id}
            for q in cls.query \
                .filter_by(published=True) \
                .order_by(cls.order)
                .all()
        ]

    # dashboard api methods
    @classmethod
    def get_all_private(cls):
        return [
            {
                'primary': q.author, 
                'secondary': get_preview_text(q.text, 50),
                'id': q.id,
                'published': q.published,
                'order': q.order
            } for q in cls.query.all()]

    @classmethod
    def update_by_id(cls, id, data):
        quote = cls.query.filter_by(id=id).first_or_404()

        quote.text = data['text']
        quote.author = data['author']
        quote.published = data['published']

        db.session.add(quote)
        db.session.commit()

        # this needs to return the object
        return quote.to_json()


class Post(APIMixin, db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(User.id))
    title = db.Column(db.String(128), nullable=True, default='')
    sub_title = db.Column(db.String(128), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, nullable=True)
    contents = db.relationship('PostContents', backref='post')
    published = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer)

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
            for p in cls.query \
                .filter_by(published=True) \
                .order_by(cls.date_created.desc()) \
                .all()
        ]

    @classmethod
    def get_all_published_posts(cls):
        posts = cls.query \
                    .filter_by(published=True) \
                    .order_by(Post.date_created) \
                    .all()
        return [post.get_contents() for post in posts]

    @classmethod
    def get_most_recent(cls):
        print('entered get most recent')
        
        posts = cls.query \
            .filter_by(published=True) \
            .order_by(Post.date_created).all()
        if not posts:
            content = None
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
    def get_by_id_public(cls, id):
        post = cls.query.filter_by(id=id).first_or_404()
        if not post.published:
            abort(404)
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

    # dashboard api methods
    def to_json(self):
        blog_contents = sorted(self.contents, key=lambda d: d.order)
        if not blog_contents:
            blog_contents = []
        return {
            'title': self.title,
            'sub_title': self.sub_title,
            'date_created': self.date_created,
            'date_updated': self.date_updated,
            'published': self.published,
            'order': self.order,
            'contents': [c.to_json() for c in blog_contents]
        }

    @classmethod
    def get_all_private(cls):
        return [
            {
                'primary': d.title, 
                'secondary': d.date_created,
                'id': d.id,
                'published': d.published,
                'order': d.order
            } for d in cls.query.all()]

    @classmethod
    def update_by_id(cls, id, data):
        post = cls.query.filter_by(id=id).first_or_404()

        post.title = data['title']
        post.sub_title = data['sub_title']
        post.published = data['published']
        if data['update_timestamp']:
            post.date_updated = datetime.utcnow()
        post.contents = PostContents.update_contents(id, data['contents'])

        db.session.add(post)
        db.session.commit()
    
        # remember, this view needs to return the saved item
        return post.to_json()

    # new and new_by_order need to override APIMixin because of user_id
    @classmethod
    def new(cls, user_id):
        order = len(cls.query.all())
        post = cls(order=order, author_id=user_id)
        db.session.add(post)
        db.session.commit()

    @classmethod
    def new_by_order(cls, order_id, user_id):
        order = int(order_id)
        cur_posts = cls.query.all()
        for r in cur_posts:
            if r.order >= order:
                r.order += 1
        new_post = cls(order=order, author_id=user_id)
        db.session.add_all([*cur_posts, new_post])
        db.session.commit()


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
            'post_id': self.post_id,
            'order': self.order,
            'content_type': self.content_type,
            'payload': self.payload,
            'uri': self.uri,
            'css': self.css,
        }

    @classmethod
    def update_contents(cls, id, contents):
        cur_contents = cls.query.filter_by(post_id=id).all()
        contents_dict = {c['id']: c for c in contents if c['id']}

        # no id? create new PostContents row
        to_add = [
            PostContents(
                order=c['order'],
                content_type=c['content_type'],
                payload=c['payload'],
                uri=c['uri'],
                css=c['css'],
                post_id=c['post_id']
                )
            for c in contents if not c['id']
        ]

        to_del = []
        for pc in cur_contents:

            if pc.id in contents_dict.keys():
                d = contents_dict[pc.id]
                pc.order = d['order']
                pc.content_type = d['content_type']
                pc.payload = d['payload']
                pc.uri = d['uri']
                pc.css = d['css']
                to_add.append(pc)

            else:
                to_del.append(pc)
                
        for pc in to_del:
            db.session.delete(pc)
        db.session.add_all(to_add)
        db.session.commit()
        return to_add


    @classmethod
    def edit_post_contents_by_id(cls, id, data):
        p = cls.query.filter_by(id=id).first()
        if not p:
            # in this case, be forgiving with a missing entry and make a new one
            p = PostContents()
        
        p.order=data['order']
        p.post_id=data['post_id']
        p.content_type=data['content_type']
        p.payload=data['payload']
        p.uri=data['uri']
        p.css=data['css']

        # not saving data here
        return p


class Node(APIMixin, db.Model):
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
    order = db.Column(db.Integer)

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

    # alt thesaurus api
    @classmethod
    def get_alt_term(cls, id):
        if not id:
            nodes = cls.query \
                .filter_by(published=True) \
                .order_by(cls.order) \
                .all()
            if not nodes: return None
            # take the one with the lowest order
            node = nodes[0]
        else:
            node = cls.query.filter_by(id=id).first_or_404()

        all_nodes = cls.query.filter_by(published=True).all()
        node_dict = {n.title: n.id for n in all_nodes}

        return {           
            'id': node.id,
            'title': node.title,
            'text': node.text,
            'example': node.example,
            'published': node.published,
            'synonyms': [(n, node_dict.get(n, None)) for n in node.synonyms],
            'antonyms': [(n, node_dict.get(n, None)) for n in node.antonyms]
        }

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
            'word_list': word_list,
            'order': self.order
        }

    # API access point
    @classmethod
    def to_dict(cls):
        """Returns a dictionary of all available Node data."""
        data = cls.query \
            .filter_by(published=True) \
            .all()
        return {d.title: node_to_json(d) for d in data}

    # dashboard api methods
    @classmethod
    def get_all_private(cls):
        return [
            {
                'primary': d.title, 
                'secondary': get_preview_text(d.text, 50),
                'id': d.id,
                'published': d.published,
                'order': d.order
            } for d in cls.query.all()]

    @classmethod
    def update_by_id(cls, id, data):
        node = cls.query.filter_by(id=id).first_or_404()

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
    def get_all_words(cls):
        return [w.title for w in cls.query.all()]


class Video(APIMixin, db.Model):
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
        video_list = cls.query \
            .filter_by(published=True) \
            .order_by(Video.order) \
            .all()
        if not len(video_list):
            return None
        return [video.to_json() for video in video_list]


    # dashboard api methods
    @classmethod
    def get_all_private(cls):
        return [
            {
                'primary': v.title, 
                'secondary': get_preview_text(v.text, 50),
                'id': v.id,
                'published': v.published,
                'order': v.order
            } for v in cls.query.all()]

    @classmethod
    def update_by_id(cls, id, data):
        video = cls.query.filter_by(id=id).first_or_404()

        video.title = data['title']
        video.text = data['text']
        video.url = data['uri']
        video.published = data['published']

        db.session.add(video)
        db.session.commit()
    
        # remember, this view needs to return the saved item
        return video.to_json()


class Resource(APIMixin, db.Model):
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
        } for r in cls.query \
                .filter_by(published=True) \
                .order_by(Resource.order) \
                .all()]

        if not len(results):
            return None
        return results

    # dashboard api methods
    @classmethod
    def get_all_private(cls):
        return [
            {
                'primary': r.title, 
                'secondary': get_preview_text(r.text, 50),
                'id': r.id,
                'published': r.published,
                'order': r.order
            } for r in cls.query.all()]

    @classmethod
    def update_by_id(cls, id, data):
        resource = cls.query.filter_by(id=id).first_or_404()

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

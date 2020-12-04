
from datetime import datetime
from flask import current_app, request, url_for
from flask_login import UserMixin
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from . import db
from . import login_manager


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
    text = db.Column(db.Text(), nullable=False)

    def __repr__(self):
        return f'"{self.text}" \n-{self.author}'


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(User.id))
    title = db.Column(db.String(128), nullable=False)
    sub_title = db.Column(db.String(128), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, nullable=True)

    def update_timestamp(self):
        self.date_updated = datetime.utcnow()

    def __repr__(self):
        return f'{self.title} - {self.date_created} - {self.user.first_name} {self.user.last_name}'


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


# user loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
import unittest
from flask import current_app
from werkzeug.exceptions import HTTPException
from app import create_app, db
from app.models import User, Quote

class QuoteTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        email = 'myemail@gmail.edu'
        username = 'username'
        first_name = 'Hieronymus'
        last_name = 'Kapsberger'
        password = 'never guess this!'

        user = User(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            confirmed=True,
            is_active=True
        )
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user(self):
        email = 'myemail@gmail.edu'
        username = 'username'
        first_name = 'Hieronymus'
        last_name = 'Kapsberger'
        password = 'never guess this!'
        user = User.query.first()
        id = user.id
        self.assertTrue(user.username == username)
        self.assertTrue(user.email == email)
        self.assertTrue(user.first_name == first_name)
        self.assertTrue(user.last_name == last_name)
        self.assertFalse(user.password == password)
        self.assertTrue(user.password == user.password_hash)

        # guard attributes
        self.assertTrue(user.identity == user.id)
        self.assertTrue(User.lookup('username') == user)
        self.assertTrue(User.identify(id) == user)
        self.assertTrue(user.is_valid())

    def test_quote(self):
        author_a = 'Piccinini'
        text_a = "Un giorno o un'altro.."
        author_b = 'Capablanca'
        text_b = 'is the bishop pair really that effective in this position?'

        quotes_list = [
            Quote(
                author=author_a,
                text=text_a,
                published=True,
                order=0
            ),
            Quote(
                author=author_b,
                text=text_b,
                published=False,
                order=1
            )
        ]
        
        db.session.add_all(quotes_list)
        db.session.commit()

        # public api
        json_a = quotes_list[0].to_json()
        self.assertTrue(json_a['author'] == author_a)
        self.assertTrue(json_a['text'] == text_a)
        self.assertTrue(json_a['published'])
        self.assertTrue(json_a['order'] == 0)

        dict_list = Quote.to_dict_list()
        for i, q in enumerate(dict_list):
            self.assertTrue(q['id'])
            self.assertTrue(q['text'])
            self.assertTrue(q['text'])
            # make sure order is correct
            Quote \
                .query \
                .filter_by(id=q['id']) \
                .first() \
                .order == i

        # private api
        def check_json(json):
            self.assertTrue(q['primary'])
            self.assertTrue(q['secondary'])
            self.assertTrue(q['id'])
            self.assertTrue(q['published'] == True or q['published'] == False)
            self.assertTrue(q['order'] == 0 or q['order'])
            with self.assertRaises(KeyError):
                q['another attribute']

        quotes = Quote.get_all_private()
        for q in quotes:
            check_json(q)

        quote = Quote.get_by_id(1)
        check_json(quote)
        # make sure a missing id raises exception
        with self.assertRaises(HTTPException):
            Quote.get_by_id(123)
        
        quote = Quote.get_by_order(1)
        check_json(quote)
        quote_confirm = Quote.query.filter_by(order=1).first()
        self.assertTrue(quote['id']==quote_confirm.id)
        with self.assertRaises(HTTPException):
            Quote.get_by_order(123)

        
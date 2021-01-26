import string
import unittest
from flask import current_app
from werkzeug.exceptions import HTTPException
from app import create_app, db
from app.models import User, Quote, Resource, Video, Post, Node



class MixinTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        models = [Quote, Resource, Video, Node, Post]
        letters = string.ascii_uppercase
        db_content = []

        for i, c in enumerate(letters):
            for Model in models:
                if Model == Quote:
                    data = {
                        'author': c,
                        'text': 'text ' + c,
                        'published': True,
                        'order': i
                    }
                elif Model == Post:
                    data = {
                        'title': c,
                        'order': i,
                        'published': True
                    }
                else:
                    data = {
                        'title': c,
                        'text': 'text ' + c,
                        'published': True,
                        'order': i
                    }
                db_content.append(Model(**data))

        db.session.add_all(db_content)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_all_private(self):
        models = [Quote, Resource, Video, Node, Post]
        for model in models:
            rows = model.get_all_private()
            for r in rows:
                self.assertTrue(r)
                self.assertTrue(r['order'] == 0 or r['order'])
                self.assertTrue(r['id'])
                self.assertTrue(r['published'] == True or r['published'] == False)
                self.assertTrue(r['primary'] == '' or r['primary'])
                self.assertTrue(r['secondary'] == '' or r['primary'])

    def test_to_json(self):
        models = [Quote, Resource, Video, Node, Post]
        for model in models:
            q = model.query.first()
            self.assertTrue(q.to_json())


    def test_update_by_id(self):
        pass # specific logic per model

    def test_get_by_id(self):
        models = [Quote, Resource, Video, Node, Post]
        for model in models:
            self.assertTrue(
                model.get_by_id(1)
            )
            with self.assertRaises(HTTPException):
                model.get_by_id(1234)

    def test_get_by_order(self):
        models = [Quote, Resource, Video, Node, Post]
        for model in models:
            self.assertTrue(
                model.get_by_order(0)
            )
            with self.assertRaises(HTTPException):
                model.get_by_order(1234)

    def test_delete(self):
        models = [Quote, Resource, Video, Node, Post]
        for model in models:
            self.assertTrue(model.get_by_id(1))
            model.delete(1)
            with self.assertRaises(HTTPException):
                model.get_by_id(1)


    def test_update_batch(self):
        models = [Quote, Resource, Video, Node, Post]
        data = [
            {'id': i, 'order': j} 
            for i, j in zip(range(1, 27), range(25, -1, -1))
        ]
        data_check = {m['id']: m['order'] for m in data}
        for model in models:
            start = {
                m['id']: m['order'] 
                for m in model.get_all_private()
            }
            model.update_batch(data)
            end = {
                m['id']: m['order'] 
                for m in model.get_all_private()
            }
            for i in range(1, 27):
                self.assertTrue(
                    end[i] == data_check[i]
                )
                self.assertFalse(
                    start[i] == end[i]
                )
                

    def test_new(self):
        models = [Quote, Resource, Video, Node, Post]
        for model in models:
            current_count = len(model.query.all())
            if model == Post:
                # post needs a user id
                model.new(1)
            else:
                model.new()
            self.assertTrue(
                len(model.query.all()) == current_count + 1
            )

    def test_new_by_order(self):
        models = [Quote, Resource, Video, Node, Post]
        for model in models:
            id_list = {
                d.id: d.order for d in model.query.all()
            }
            # insert at the beginning
            if model == Post:
                model.new_by_order(0, 1)
            else:
                model.new_by_order(0)
            new_list = model.query.all()
            self.assertTrue(
                len(new_list) == len(id_list) + 1
            )
            for d in new_list:
                if id_list.get(d.id, None):
                    self.assertTrue(d.order == id_list[d.id]+1)

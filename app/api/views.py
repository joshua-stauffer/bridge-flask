from datetime import datetime

from flask import render_template, request, url_for, redirect, flash, jsonify
from flask_login import (
    login_user, logout_user, login_required, current_user
)
from . import api
# from .utils.to_json import node_to_json
from .. import db
from ..models import User, Quote, Post, Node, Resource
from ..app_mail import send_email


@api.route('/next-post/<date>')
def next_post(date=datetime.utcnow):
    pass


@api.route('/qt-data')
def qt_data():
    return jsonify(Quote.to_dict_list())


@api.route('/vt-data')
def vt_data():
    return Node.to_dict()


@api.route('/gen-quotes')
def gen_quotes():
    return jsonify(Quote.get_edit_list())


@api.route('/sp-quotes-<id>')
def sp_quotes(id):
    return Quote.get_by_id(id)


@api.route('/new-quotes', methods=['POST'])
def new_quotes():
    # this returns a new quote, but seems easier to just reload the whole list
    Quote.get_new()
    return jsonify(Quote.get_edit_list())

@api.route('/del-quotes-<id>', methods=['DELETE'])
def del_quotes(id):
    Quote.delete(id)
    return jsonify(Quote.get_edit_list())


@api.route('/save-quotes', methods=['PUT'])
def save_quotes():
    data = request.get_json()
    print(data)
    quote = Quote.save(data)
    return quote



@api.route('/gen-resources')
def gen_resources():
    return jsonify(Resource.get_edit_list())
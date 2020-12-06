from datetime import datetime

from flask import render_template, request, url_for, redirect, flash, jsonify
from flask_login import (
    login_user, logout_user, login_required, current_user
)
from . import api
# from .utils.to_json import node_to_json
from .. import db
from ..models import User, Quote, Post, Node
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

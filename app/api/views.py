from datetime import datetime
from flask import render_template, request, url_for, redirect, flash, jsonify, abort, current_app
import flask_praetorian
from time import sleep
from . import api
# from .utils.to_json import node_to_json
from .. import db, guard, limiter
from ..models import User, Quote, Post, Node, Resource, Video
from ..app_mail import send_email


@api.route('/qt-data')
def qt_data():
    return jsonify(Quote.to_dict_list())


@api.route('/vt-data')
def vt_data():
    nodes = Node.to_dict()
    return nodes

@api.route('/get-node', methods=['GET'])
def get_node():
    return Node.get_alt_term(None)

@api.route('/get-node-<id>', methods=['GET'])
def get_node_by_id(id):
    return Node.get_alt_term(id)

#############################

@api.route('/login', methods=['POST'])
@limiter.limit("3/minute;40/hour")
def login():
    r = request.get_json(force=True)
    username = r.get('username', None)
    password = r.get('password', None)
    user = guard.authenticate(username, password)
    if user:
        current_app.logger.info(f'logged in {user}')
    else:
        current_app.logger.info('failed login attempt')
    response = {'access_token': guard.encode_jwt_token(user)}
    return response


@api.route('/quotes', methods=['GET', 'PATCH', 'POST'])
@flask_praetorian.auth_required
@limiter.limit("1/second")
def gen_quotes():

    if request.method == 'GET':
        pass

    elif request.method == 'PATCH':
        data = request.get_json()
        Quote.update_batch(data)

    elif request.method == 'POST':
        Quote.new()
    
    return jsonify(Quote.get_all_private())


@api.route('/quotes-<id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@flask_praetorian.auth_required
@limiter.limit("1/second")
def sp_quotes(id):

    if request.method == 'GET':
        return Quote.get_by_id(id)
    
    elif request.method == 'PUT':
        # remember that this needs to return a single object!
        data = request.get_json()
        print('got json data request: ', data)
        new_quote = Quote.update_by_id(id, data)
        return new_quote

    elif request.method == 'POST':
        # in this case, the id passed is actually order
        Quote.new_by_order(id)

    elif request.method == 'DELETE':
        Quote.delete(id)
        
    return jsonify(Quote.get_all_private())


@api.route('/resources', methods=['GET', 'PATCH', 'POST'])
@flask_praetorian.auth_required
@limiter.limit("1/second")
def gen_resources():
    
    if request.method == 'GET':
        pass

    elif request.method == 'PATCH':
        data = request.get_json()
        Resource.update_batch(data)

    elif request.method == 'POST':
        Resource.new()
    
    return jsonify(Resource.get_all_private())


@api.route('/resources-<id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@flask_praetorian.auth_required
@limiter.limit("1/second")
def sp_resources(id):
    
    if request.method == 'GET':
        return Resource.get_by_id(id)
    
    elif request.method == 'PUT':
        # must return the saved object
        data = request.get_json()
        new_resource = Resource.update_by_id(id, data)
        return new_resource
        
    elif request.method == 'POST':
        # in this case, the id is actually the index where we want to place the new element
        Resource.new_by_order(id)

    elif request.method == 'DELETE':
        Resource.delete(id)
        
    return jsonify(Resource.get_all_private())


@api.route('/videos', methods=['GET', 'PATCH', 'POST'])
@flask_praetorian.auth_required
@limiter.limit("1/second")
def gen_videos():
    
    if request.method == 'GET':
        pass

    elif request.method == 'PATCH':
        data = request.get_json()
        Video.update_batch(data)

    elif request.method == 'POST':
        Video.new()
    
    return jsonify(Video.get_all_private())


@api.route('/videos-<id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@flask_praetorian.auth_required
@limiter.limit("1/second")
def sp_videos(id):
    
    if request.method == 'GET':
        return Video.get_by_id(id)
    
    elif request.method == 'PUT':
        # must return the saved object
        data = request.get_json()
        new_video = Video.update_by_id(id, data)
        return new_video
        
    elif request.method == 'POST':
        Video.new_by_order(id)

    elif request.method == 'DELETE':
        Video.delete(id)
        
    return jsonify(Video.get_all_private())


@api.route('/blog', methods=['GET', 'PATCH', 'POST'])
@flask_praetorian.auth_required
@limiter.limit("1/second")
def gen_blog():
    user_id = flask_praetorian.current_user_id()
    
    if request.method == 'GET':
        pass

    elif request.method == 'PATCH':
        data = request.get_json()
        Post.update_batch(data)

    elif request.method == 'POST':
        Post.new(user_id)
    
    return jsonify(Post.get_all_private())


@api.route('/blog-<id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@flask_praetorian.auth_required
@limiter.limit("1/second")
def sp_blog(id):
    user_id = flask_praetorian.current_user_id()
 
    if request.method == 'GET':
        return Post.get_by_id(id)
    
    elif request.method == 'PUT':
        # must return the saved object
        data = request.get_json()
        new_Post = Post.update_by_id(id, data)
        return new_Post
        
    elif request.method == 'POST':
        Post.new_by_order(id, user_id)

    elif request.method == 'DELETE':
        Post.delete(id)
        
    return jsonify(Post.get_all_private())


@api.route('/thesaurus', methods=['GET', 'PATCH', 'POST'])
@flask_praetorian.auth_required
@limiter.limit("1/second")
def gen_thesaurus():
    print('entered gen_thesaurus with the method ', request.method)

    if request.method == 'GET':
        pass

    elif request.method == 'PATCH':
        data = request.get_json()
        Node.update_batch(data)


    elif request.method == 'POST':
        Node.new()
    
    return jsonify(Node.get_all_private())


@api.route('/thesaurus-<id>', methods=['GET', 'PUT', 'POST', 'DELETE'])
@flask_praetorian.auth_required
@limiter.limit("1/second")
def sp_thesaurus(id):

    if request.method == 'GET':
        return Node.get_by_id(id)
    
    elif request.method == 'PUT':
        # remember that this needs to return a single object!
        data = request.get_json()
        new_node = Node.update_by_id(id, data)
        return new_node

    elif request.method == 'POST':
        # in this case, the id passed is actually order
        Node.new_by_order(id)

    elif request.method == 'DELETE':
        Node.delete(id)
        
    return jsonify(Node.get_all_private())

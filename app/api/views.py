from datetime import datetime

from flask import render_template, request, url_for, redirect, flash, jsonify
from flask_login import (
    login_user, logout_user, login_required, current_user
)
from . import api
# from .utils.to_json import node_to_json
from .. import db
from ..models import User, Quote, Post, Node, Resource, Video
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

#############################

@api.route('/quotes', methods=['GET', 'PUT', 'POST'])
def gen_quotes():
    print('entered gen_quotes with the method ', request.method)

    if request.method == 'GET':
        pass

    #TODO: is this code needed?
    elif request.method == 'PUT':
        data = request.get_json()
        print('found arguments in gen_quotes: ', data)
        Quote.update_batch(data)

    elif request.method == 'POST':
        Quote.new()
    
    return jsonify(Quote.get_all_private())


@api.route('/quotes-<id>', methods=['GET', 'PUT', 'DELETE'])
def sp_quotes(id):
    print('got quote with id ', id)

    if request.method == 'GET':
        return Quote.get_by_id(id)
    
    elif request.method == 'PUT':
        # remember that this needs to return a single object!
        data = request.get_json()
        print('got json data request: ', data)
        new_quote = Quote.update_by_id(id, data)
        return new_quote

    elif request.method == 'DELETE':
        Quote.delete(id)
        
    return jsonify(Quote.get_all_private())


@api.route('/resources', methods=['GET', 'PUT', 'POST'])
def gen_resources():
    
    if request.method == 'GET':
        pass

    elif request.method == 'PUT':
        data = request.get_json()
        Resource.update_batch(data)

    elif request.method == 'POST':
        Resource.new()
    
    return jsonify(Resource.get_all_private())


@api.route('/resources-<id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def sp_resources(id):
    
    if request.method == 'GET':
        return Resource.get_by_id(id)
    
    elif request.method == 'PUT':
        # must return the saved object
        data = request.get_json()
        print('data is ', data)
        new_resource = Resource.update_by_id(id, data)
        return new_resource
        
    elif request.method == 'POST':
        # in this case, the id is actually the index where we want to place the new element
        Resource.new_by_order(id)

    elif request.method == 'DELETE':
        Resource.delete(id)
        
    return jsonify(Resource.get_all_private())


@api.route('/videos', methods=['GET', 'PUT', 'POST'])
def gen_videos():
    
    if request.method == 'GET':
        pass

    elif request.method == 'PUT':
        data = request.get_json()
        Video.update_batch(data)

    elif request.method == 'POST':
        Video.new()
    
    return jsonify(Video.get_all_private())


@api.route('/videos-<id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def sp_videos(id):
    
    if request.method == 'GET':
        return Video.get_by_id(id)
    
    elif request.method == 'PUT':
        # must return the saved object
        data = request.get_json()
        print('data is ', data)
        new_video = Video.update_by_id(id, data)
        return new_video
        
    elif request.method == 'POST':
        # in this case, the id is actually the index where we want to place the new element
        Video.new_by_order(id)

    elif request.method == 'DELETE':
        Video.delete(id)
        
    return jsonify(Video.get_all_private())


@api.route('/blog', methods=['GET', 'PUT', 'POST'])
def gen_blog():
    
    if request.method == 'GET':
        pass

    elif request.method == 'PUT':
        data = request.get_json()
        Post.update_batch(data)

    elif request.method == 'POST':
        Post.new()
    
    return jsonify(Post.get_all_private())


@api.route('/blog-<id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def sp_blog(id):
    
    if request.method == 'GET':
        return Post.get_by_id_private(id)
    
    elif request.method == 'PUT':
        # must return the saved object
        data = request.get_json()
        print('data is ', data)
        new_Post = Post.update_by_id(id, data)
        return new_Post
        
    elif request.method == 'POST':
        # in this case, the id is actually the index where we want to place the new element
        Post.new_by_order(id)

    elif request.method == 'DELETE':
        Post.delete(id)
        
    return jsonify(Post.get_all_private())


@api.route('/thesaurus', methods=['GET', 'PUT', 'POST'])
def gen_thesaurus():
    print('entered gen_thesaurus with the method ', request.method)

    if request.method == 'GET':
        pass

    #TODO: is this code needed?
    elif request.method == 'PUT':
        data = request.get_json()
        print('found arguments in gen_thesaurus: ', data)
        Node.update_batch(data)

    elif request.method == 'POST':
        Node.new()
    
    return jsonify(Node.get_all_private())


@api.route('/thesaurus-<id>', methods=['GET', 'PUT', 'DELETE'])
def sp_thesaurus(id):
    print('got quote with id ', id)

    if request.method == 'GET':
        return Node.get_by_id(id)
    
    elif request.method == 'PUT':
        # remember that this needs to return a single object!
        data = request.get_json()
        print('got json data request: ', data)
        new_node = Node.update_by_id(id, data)
        return new_node

    elif request.method == 'DELETE':
        Node.delete(id)
        
    return jsonify(Node.get_all_private())


"""
get_by_id
get_all_private
update_by_id
update_batch
delete
new
new_by_order




"""
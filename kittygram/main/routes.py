from math import floor
from pickletools import optimize
from re import I
from turtle import pos
from flask import get_flashed_messages, redirect, jsonify,render_template, abort, flash
from sqlalchemy import desc
from werkzeug.utils import secure_filename
from pathlib import Path
from PIL import Image

from . import main
from kittygram.models import Post, User, Like
from kittygram import db

from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
import os
import datetime


UPLOAD_FOLDER = os.path.abspath(os.getcwd()) + '/kittygram/static/images'

class PostForm(FlaskForm):
    file = FileField('', description='Please upload a photo of your cat.',validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Please upload an image')])
    text = StringField('', description='Tell people something about your cutie!', validators=[DataRequired(), Length(5,50, 'Text must have between 5 and 50 characters.')] )
    submit = SubmitField('Upload')

@main.route('/')
def index():
    return render_template('home.html')

@login_required
@main.route('/upload', methods = ['GET', 'POST'])
def upload():
    form = PostForm()
    if form.validate_on_submit():
        f = form.file.data
        
        filename = secure_filename(f.filename) # remove file path for security 
        filename = make_unique(filename) # replace name by unique ID
        
        # resize if necessary
        f = Image.open(f)
        w = f.size[0]
        h = f.size[1]

        MAX_SIZE = 700
        if w > MAX_SIZE:
            resize_factor = w / MAX_SIZE
            w = floor(w / resize_factor)
            h = floor(h / resize_factor)
        elif h > MAX_SIZE:
            resize_factor = h/MAX_SIZE
            w = floor(w / resize_factor)
            h = floor(h / resize_factor)
        f = f.resize((w,h))
        
        f.save(UPLOAD_FOLDER + '/' + filename) 

        post = Post(img_filename=filename, text=form.data['text'], author_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        return redirect('/')
    return render_template('upload.html', form=form)

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    
    print(user.posts)
    return render_template('user.html', user=user)

@main.route('/posts')
def get_posts():
    posts = Post.query.all()
    return jsonify({'posts': [post.to_json() for post in posts]})

@main.route('/posts/<username>')
def get_posts_by_username(username):
    author = User.query.filter_by(username = username).first()
    posts = Post.query.filter_by(author_id = author.id)
    return jsonify({'posts': [post.to_json() for post in posts]})

@main.route('/like/<post_id>', methods=['POST'])
def like(post_id):
    like_query = Like.query.filter(Like.author_id == current_user.id, Like.post_id == post_id)
    like_count = len(Post.query.filter_by(id = post_id).first().likes)
    if like_query.first():

        like_query.delete()
        db.session.commit()

        response = jsonify({'success': False, 'likeCount': like_count - 1})
        return response
    else:
        like = Like(author_id = current_user.id, post_id = post_id)
        db.session.add(like)
        db.session.commit()
        
        response = jsonify({'success': True, 'likeCount': like_count + 1})
        response.status_code = 200
        return response

from uuid import uuid4
def make_unique(string):
    ident = uuid4().__str__()
    return f'{ident}{Path(string).suffix}'
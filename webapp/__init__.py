#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013 Alexandre Bulté <alexandre[at]bulte[dot]net>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import shelve

from flask import Flask, abort, render_template, send_file
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.security import Security, SQLAlchemyUserDatastore, login_required
from flask_mail import Mail

app = Flask(__name__)

app.config.update(
    DEBUG = True,
    SQLALCHEMY_DATABASE_URI = 'sqlite:///gallery.db',
    SECRET_KEY = '\xa1d\x91\xad\xf8y\xf4\xc0\xed\xc8\x16\\n\x12\x04Ss+\x80\xf8\x7f\xfdy\x8d',
    PHOTOS_PATH = '/Users/alexandre/Pictures/gallery',
    THUMBS_PATH = '/Users/alexandre/Pictures/gallery/thumbs',
    MAIL_SERVER = 'localhost',
    MAIL_PORT = 25
)

db = SQLAlchemy(app)
mail = Mail(app)

from .models import User, Album, Photo, Role

admin = Admin(app, name='BPhotos')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Photo, db.session))
admin.add_view(ModelView(Album, db.session))
admin.add_view(ModelView(Role, db.session))

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

@app.route('/thumbs/<path:path>')
@login_required
def thumbs(path):
    """ Files only route, to serve thumbs """
    thumbs_path = app.config.get('THUMBS_PATH')
    req_path = '%s/%s' % (thumbs_path, path)
    if not os.path.isfile(req_path):
        abort(404)
    return send_file(req_path)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
@login_required
def catch_all(path):
    photos_path = app.config.get('PHOTOS_PATH')
    req_path = '%s/%s' % (photos_path, path)
    if not os.path.exists(req_path):
        abort(404)
    if os.path.isdir(req_path):
        if path == '':
            photos = Photo.query.all()
        else:
            photos  = Photo.query.filter(Photo.rpath.startswith('/%s' % path)).all()
    elif os.path.isfile(req_path):
        # TODO verify it is image and access rights
        return send_file(req_path)
    menu_shelve = shelve.open('webapp/menus.shelve')
    if not 'main_menu' in menu_shelve.keys():
        abort(500, 'Main menu has not been stored in shelve, did you index?')
    return render_template('index.html', photos=photos, menu=menu_shelve['main_menu'])


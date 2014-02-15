#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013 Alexandre Bulté <alexandre[at]bulte[dot]net>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from datetime import datetime

from flask.ext.security import UserMixin, RoleMixin

from webapp import db

## USERS AND ROLES

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # username = db.Column(db.String(), unique=True)
    email = db.Column(db.String(), unique=True)
    password = db.Column(db.String())
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return '<User %r>' % self.email

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

## PHOTOS AND ALBUMS

photos_albums = db.Table('photos_albums',
    db.Column('album_id', db.Integer, db.ForeignKey('photo.id')),
    db.Column('photo_id', db.Integer, db.ForeignKey('album.id'))
)

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # relative path rpath is the 'unique key'
    rpath = db.Column(db.String(), unique=True)
    path = db.Column(db.String(), unique=True)
    name = db.Column(db.String())
    taken = db.Column(db.DateTime())
    thumb_path = db.Column(db.String(), unique=True)

    def __repr__(self):
        return '<Photo %r>' % self.path

albums_users = db.Table('albums_users',
    db.Column('album_id', db.Integer, db.ForeignKey('album.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True)
    photos = db.relationship('Photo', secondary=photos_albums,
        backref=db.backref('albums', lazy='dynamic'))
    created = db.Column(db.DateTime(), default=datetime.now())
    users = db.relationship('User', secondary=albums_users,
        backref=db.backref('albums', lazy='dynamic'))

    def __repr__(self):
        return '<Album %r>' % self.name

class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('menu.id'))
    level = db.Column(db.Integer)
    name = db.Column(db.String())
    children = db.relationship("Menu",
                backref=db.backref('parent', remote_side=[id])
            )

    def __repr__(self):
        return '<Menu %r>' % self.name


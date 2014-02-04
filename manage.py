#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013 Alexandre Bulté <alexandre[at]bulte[dot]net>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import sys
from PIL import Image
import exifread
from datetime import datetime

from flask.ext.script import Manager

from webapp import app, db, user_datastore
from webapp.models import Photo, Menu

manager = Manager(app)

ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png']

def get_files_r():
    files = []
    for dirname, dirnames, filenames in os.walk(app.config.get('PHOTOS_PATH')):
        for filename in filenames:
            if not 'pyenv' in dirname and not app.config.get('THUMBS_PATH') in dirname:
                if filename.split('.')[-1] in ALLOWED_EXTENSIONS:
                    files.append(os.path.join(dirname, filename))
    return files

def get_thumbname_from_name(name):
    return name.replace('./', '').replace('/', '_')

def generate_thumbnails(filenames):
    saved_files = []
    counter = 0
    for name in filenames:
        counter+= 1
        # app.logger.debug("Trying to open %s" % name)
        try:
            date = None
            f = open(name, 'rb')
            tags = exifread.process_file(f)
            if 'EXIF DateTimeOriginal' in tags.keys():
                date = tags['EXIF DateTimeOriginal']
                try:
                    date = datetime.strptime(str(date), '%Y:%m:%d %H:%M:%S')
                except:
                    app.logger.error("Can't parse EXIF date %s" % date)

            im = Image.open(name)
            im.thumbnail( (75,75) )
            tname = get_thumbname_from_name(name)
            # app.logger.debug("Saving thumb-%s" % tname)
            tpath = "%s/%s" % (app.config.get('THUMBS_PATH'), tname)
            im.save(tpath)
            saved_files.append({
                'path': name,
                'rpath': name.replace(app.config.get('PHOTOS_PATH'), ''),
                'thumb_path': tname,
                'name': name.split('/')[-1] if '/' in name else name,
                'date': date
            })
            sys.stdout.write("\r%f%%" % (counter*100.0/len(filenames)))
            sys.stdout.flush()
        except IOError:
            app.logger.debug("File %s cannot be parsed by PIL, ignoring" % name)
    return saved_files

def menu_item(path_array, menu):
    if len(path_array) > 0:
        menu[path_array[0]] = {}
        if len(path_array) > 1:
            menu[path_array[0]] = menu_item(path_array[1:], menu[path_array[0]])
    return menu

@manager.command
def build_menu():
    """ Build menu from photos and shelve it """

    # TODO: clean the obsolete paths

    root_len = len(app.config.get('PHOTOS_PATH').split('/'))
    last_items = []
    for dirname, dirnames, filenames in os.walk(app.config.get('PHOTOS_PATH')):
        rel_path = dirname.split(app.config.get('PHOTOS_PATH'))[-1]
        # exclude root
        if rel_path != '':
            name = rel_path.split('/')[-1]
            cur_len = len(dirname.split('/'))
            level = cur_len - root_len - 1
            if level >= 0:
                if level == 0:
                    parent = None
                    query = Menu.query.filter_by(name=name, level=level)
                else:
                    parent = last_items[level-1]
                    query = Menu.query.filter_by(name=name, level=level, parent_id=parent.id)
                if query.first() is None:
                    menu_item = Menu(name=name, level=level, parent=parent)
                    db.session.add(menu_item)
                    db.session.commit()
                else:
                    menu_item = query.first()

                if len(last_items) == level:
                    last_items.append(menu_item)
                elif level + 1 > len(last_items):
                    app.logger.debug('THIS SHOULD NOT HAPPEN')
                else:
                    last_items[level] = menu_item

    print 'Menu is built and stored.'

@manager.command
def clean_index():
    """ Remove photos index and menus """
    photos = Photo.query.all()
    for photo in photos:
        db.session.delete(photo)
    menus = Menu.query.all()
    for menu in menus:
        db.session.delete(menu)
    db.session.commit()
    print "Clean."

@manager.command
def index():
    """ Indexes in DB photos and builds menu """

    # TODO: remove obsolete items

    files = get_files_r()
    saved_files = generate_thumbnails(files)
    for photo in saved_files:
        # relative path rpath is the 'unique key'
        existing = Photo.query.filter_by(rpath=photo['rpath']).first()
        if existing is None:
            photo_rec = Photo(rpath=photo['rpath'], path=photo['path'], name=photo['name'], thumb_path=photo['thumb_path'], taken=photo['date'])
            db.session.add(photo_rec)
            db.session.commit()
        else:
            existing.path = photo['path']
            existing.name = photo['name']
            existing.taken = photo['date']
            existing.thumb_path = photo['thumb_path']
            db.session.commit()
    build_menu()
    print 'Photos are indexed.'

@manager.command
def initdb(clean=False):
    """ Creates db schema """
    if clean:
        clean_index()
    db.create_all()
    print "DB inited."

@manager.command
def create_user(name, password):
    """ Create a test user """
    db.create_all()
    user_datastore.create_user(email=name, password=password)
    db.session.commit()
    print "User created."

if __name__ == "__main__":
    manager.run()


# manage.py

import os
import sys
import shelve
from PIL import Image

from flask.ext.script import Manager

from webapp import app, db, user_datastore
from webapp.models import Photo

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
        app.logger.debug("Trying to open %s" % name)
        try:
            im = Image.open(name)
            im.thumbnail( (75,75) )
            tname = get_thumbname_from_name(name)
            app.logger.debug("Saving thumb-%s" % tname)
            tpath = "%s/%s" % (app.config.get('THUMBS_PATH'), tname)
            im.save(tpath)
            saved_files.append({
                'path': name,
                'rpath': name.replace(app.config.get('PHOTOS_PATH'), ''),
                'thumb_path': tname,
                'name': name.split('/')[-1] if '/' in name else name
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
    menu = {}
    photos = Photo.query.all()
    for photo in photos:
        rpath_base = photo.rpath.split('/')[1:-1]
        menu_item(rpath_base, menu)
    menu_shelve = shelve.open('webapp/menus.shelve')
    menu_shelve['main_menu'] = menu
    menu_shelve.close()
    print 'Menu is built and stored.'

@manager.command
def index():
    files = get_files_r()
    saved_files = generate_thumbnails(files)
    for photo in saved_files:
        # relative path rpath is the 'unique key'
        existing = Photo.query.filter_by(rpath=photo['rpath']).first()
        if existing is None:
            photo_rec = Photo(photo['rpath'], photo['path'], photo['name'], photo['thumb_path'])
            db.session.add(photo_rec)
            db.session.commit()
        else:
            existing.path = photo['path']
            existing.name = photo['name']
            existing.thumb_path = photo['thumb_path']
            db.session.commit()
    build_menu()
    print 'Photos are indexed.'

@manager.command
def initdb():
    db.create_all()
    print "DB inited."

@manager.command
def create_user():
    db.create_all()
    user_datastore.create_user(email='alexandre@bulte.net', password='alexandre')
    db.session.commit()

if __name__ == "__main__":
    manager.run()


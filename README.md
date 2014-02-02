pypobox
=======

PY PhOto BOX - your personal photo sharing and hosting site, in python

#### Quickstart

Edit `webapp/__init__.py` and set `PHOTOS_PATH` and `THUMBS_PATH` values. Edit `manage.py` and modify `create_user` with your desired email address and password.

    pip install -r requirements.txt
    python manage.py initdb
    python manage.py create_user
    python manage.py index
    python manage.py runserver

Visit localhost:5000.

Some parts of the code inspired by [https://github.com/awailly/gallery](https://github.com/awailly/gallery).

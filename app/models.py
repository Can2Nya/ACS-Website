# -*- coding: utf-8 -*-
import logging
import os
import os.path as op
from datetime import datetime

from flask_admin import form
from flask_login import UserMixin, AnonymousUserMixin
from sqlalchemy.event import listens_for

from qnauth import upload_qiniu, del_pic
from . import db
from . import login_manager


@login_manager.user_loader
def user_loader(user_id):
    return Manager.query.get(int(user_id))

login_manager.login_message = u"请先登录！"


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    stu_id = db.Column(db.BigInteger, unique=True)
    name = db.Column(db.String(16))
    stu_class = db.Column(db.String(64))
    qq = db.Column(db.String(20))

    def __repr__(self):
        return '<student %r>' % self.name


class Manager(UserMixin, db.Model):
    __tablename__ = 'manager'
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(128))

    def verify_password(self,password):
        return self.password == password


class AnonymousUser(AnonymousUserMixin):
    pass

login_manager.anonymous_user = AnonymousUser

class PictureWall(db.Model):
    __tablename__='picturewall'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    pic_url= db.Column(db.String(128), unique=True,nullable=False)
    info = db.Column(db.Text)
    remote_url = db.Column(db.String(128), unique=True)
    add_time = db.Column(db.DateTime, default=datetime.now)


file_path = op.join(op.dirname(__file__), 'static')


@listens_for(PictureWall, 'after_delete')
def del_file(mapper, connection, target):
    if target.pic_url:
        # Delete image
        try:
            os.remove(op.join(file_path, target.pic_url))
        except OSError:
            pass

        # Delete thumbnail
        try:
            os.remove(op.join(file_path,
                              form.thumbgen_filename(target.pic_url)))
        except OSError:
            pass
        del_pic(target.pic_url)
        print target.pic_url



@listens_for(PictureWall,'before_insert')
def before_insert(mapper, connection, target):
    try:
        upload_url = upload_qiniu(op.join(file_path, target.pic_url),target.pic_url)
    except:
        logging.warning('upload picture failed')
        return
    print 1
    target.remote_url = upload_url


@listens_for(PictureWall,'after_update')
def after_update(mapper, connection, target):
    pass
    # if not target.pic_url and target.remote_url:
    #     target.remote_url = ''
    #     return
    #
    # if target.remote_url and not  target.remote_url:
    #     try:
    #         upload_url = upload_qiniu(op.join(file_path, target.pic_url),target.pic_url)
    #     except:
    #         logging.warning('upload picture failed')
    #         return
    #     print 2
    #     target.remote = upload_url









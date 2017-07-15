# coding=utf-8
import json

import requests
from flask import render_template, jsonify, request

from . import main
from .. import csrf
from ..models import Student, db


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('website.html')


@csrf.exempt
@main.route("/login", methods=["POST"])
def login():
    info = request.form;
    stu_id = info.get('id')
    name = info.get('name')
    stu_class = info.get('class')
    qq = info.get('qq')
    if not stu_id or not name or not stu_class or not qq:
        return jsonify({'msg': u'报名失败，请检查信息'})
    student = Student.query.filter_by(stu_id=stu_id).first()
    if student is None:
        url = "http://www.jxnugo.com/api/is_jxnu_student"
        post_data = {'student_id': info.get("id")}
        r = requests.post(url, data=json.dumps(post_data), headers={'content-type': 'application/json'})
        if name != 'Label' and name == r.json()['student_name']:
            student = Student(stu_id=stu_id, name=name, qq=qq,
                              stu_class=stu_class)
            db.session.add(student)
            return jsonify({'msg': u'报名成功'})
        else:
            return jsonify({'msg': u'报名失败，请检查信息'})
    else:
        return jsonify({'msg': u'你已经报过名，请勿重复操作'})
    return jsonify({'msg': 'error'})

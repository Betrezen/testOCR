import base64
import os
import os.path as op
import datetime
import json

from flask import Flask
from flask import render_template, redirect, url_for, request, flash
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext import admin
from flask.ext.admin.contrib import sqla
from flask.ext.admin.contrib.sqla import filters
from flask.ext.login import LoginManager
from flask_restful import Api
from werkzeug import secure_filename

import pylib

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.setdefaultencoding('utf-8')

# -*- coding: utf-8 -*-

# Create application
app = Flask(__name__)
#, static_url_path = '/home/ubuntu/ocr/storage',
#                      static_folder = '/home/ubuntu/ocr/storage')

# Create dummy secrey key so we can use sessions
app.secret_key = pylib.get_random_uuid()
app.url_map.strict_slashes = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] =  '/home/ubuntu/ocr/static/storage'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
STATUSES = set(['New', 'Progress', 'Done'])

# Create admin
#login_manager = LoginManager()

# Create database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/ubuntu/ocr/test.db'
api = Api(app)
db = SQLAlchemy(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def output_xml(data, code, headers=None):
    """Makes a Flask response with a XML encoded body"""
    resp = make_response(dumps(data), code)
    resp.headers.extend(headers or {'content-type': 'application/xml'})
    return resp

# Create models
class OCRDoc(db.Model):
    __tablename__ = 'ocrdocs'
    id = db.Column(db.Integer, primary_key=True)
    filepath = db.Column(db.String(128))
    fileobj = db.Column(db.LargeBinary)
    # New, Progress, Done
    status = db.Column(db.String(10))
    filename = db.Column(db.String(128))
    filetype = db.Column(db.String(64), unique=False)
    filesize = db.Column(db.Integer)
    fields = db.Column(db.Text)
    def __init__(self, filepath, status='New'):
        self.filepath = os.path.abspath(filepath)
        self.status = status
        self.filename = os.path.basename(filepath)
        self.filetype = self.filename.split('.')[1]
        self.filesize = os.stat(filepath).st_size
        self.fileobj = pylib.get_base64_from_file(filepath)
    def __unicode__(self):
        return self.filename
    def __repr__(self):
        return self.filename

# Routes
# Main pages
@app.route('/')
def ocrdocs_list_page():
    ocrdocs = OCRDoc.query.all()
    context = {'ocrdocs': ocrdocs}
    return render_template('ocrdocs.html', data=context)

@app.route('/new', methods=['GET'])
def ocrdocs_form():
    context = {'allowed': ALLOWED_EXTENSIONS}
    return render_template('ocradd.html', data=context)

@app.route('/add', methods=['POST'])
def ocrdocs_add():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filel = secure_filename(file.filename).split('.')
            filename = ".".join([pylib.get_random_uuid(), filel[1]])
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            newdoc = OCRDoc(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            db.session.add(newdoc)
            db.session.commit()
            flash ("Item: ID=[{}] FILE={} has been created".format('NA', filename))
            return redirect(url_for('ocrdocs_list_page'))    

@app.route('/delete/<ocr_id>', methods=['DELETE', 'GET'])
def ocrdocs_del(ocr_id=None):
    doc = OCRDoc.query.filter(OCRDoc.id == ocr_id).first()
    if doc:
        db.session.delete(doc)
        db.session.commit()
    flash ("Item: ID=[{}] has been deleted".format(ocr_id))
    return redirect(url_for('ocrdocs_list_page'))

@app.route('/edit/<ocr_id>', methods=['GET'])
def ocrdocs_edit(ocr_id=None):
    doc = OCRDoc.query.filter(OCRDoc.id == ocr_id).first()
    if doc:
        context = {'ocrdocs': doc, 'statuses': STATUSES}
    return render_template('ocredit.html', data=context)

@app.route('/update/<ocr_id>', methods=['POST'])
def ocrdocs_update(ocr_id=None):
    doc = OCRDoc.query.filter(OCRDoc.id == ocr_id).first()
    if doc:
        doc.status = request.form['status']
        db.session.commit()
    flash ("Item: ID=[{}] has been updated. {}".format(ocr_id, request.form['status']))
    return redirect(url_for('ocrdocs_list_page'))

@app.route('/recognize', methods=['GET'])
def ocrdocs_recognize():
    docs = OCRDoc.query.filter(OCRDoc.status == 'New')
    for doc in docs:
        text = pylib.image2text(doc.filepath, 'rus')
        doc.fields = unicode(text)
        doc.status = 'Done'
        db.session.commit()
        flash ("Item: ID=[{}] has been recognized".format(doc.id))
    return redirect(url_for('ocrdocs_list_page'))

@app.route('/help')
def help_page():
    return render_template('help.html')

if __name__ == '__main__':
    #db.drop_all()
    db.create_all()
    app.run('0.0.0.0', 80, debug=True)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys 
import requests,base64,random,time,json
#sys.path.append('')

from modelzoo import model_manager,modelzoo_utils
manager = model_manager.ModelManager(model_manager.API_TOKEN, model_manager.API_URL)

from github import Github
g = Github("0420d62334bbc5bf0ccead2d6b00ebfc6181b093")
repo = g.get_user().get_repo("modelzoo_registry")

DISTANTGIT = 'https://raw.githubusercontent.com/hettk/modelzoo_registry/main/'
UPLOAD_FOLDER = './mdls'
ALLOWED_EXTENSIONS = {'pdf'}

name = sys.argv[1]
filename = sys.argv[9]
doi = sys.argv[2]
version = sys.argv[3]
author = sys.argv[4]
email = sys.argv[5]
location = sys.argv[6]
tag = sys.argv[7]

pdf = os.path.join('mdls',name,version,filename)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




if allowed_file(filename):
    repo.create_file(pdf, "Add pdf", filename)
    dir,base = os.path.split(UPLOAD_FOLDER)
    urlpdf = DISTANTGIT + base + "/" + name + "/" + version + "/" +  filename
    #print (pdf)
    data = {'name': name, 'doi':doi, 'version': version, 'author': author, 'email': email, 'location': location, 'pdf': urlpdf, 'tag': tag}

    mdl = model_manager.ModelInstance.create_instance(data, fromDatabase=False)

    manager.pushmodel(mdl)
else:
    print ("This file is not allowed")






#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import uuid
import threading
import time
#
import requests
import json
# add scp
#from paramiko import SSHClient
#from scp import SCPClient

import sys
sys.path.append('')

# Flask configuration
import flask
# from flask_ngrok import run_with_ngrok
from flask import request,jsonify
app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Start ngrok
# run_with_ngrok(app)

ALLOWED_EXTENSIONS = {'png','jpeg','jpg','pdf'}
ENV_OUTPATH = "/storage"
ENV_TMP  = "/home/kilianhett/tmp"
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from modelzoo import model_manager, modelzoo_utils, inference_manager

manager = model_manager.ModelManager(model_manager.API_TOKEN, model_manager.API_URL)
engine = inference_manager.InferenceEngine(manager, ENV_OUTPATH)


def get_instance(query_parameters):
    mdls = manager.listmodel()
    instance = []
    for m in mdls:
        mdl = mdls[m]
        if query_parameters.__contains__("model_id"):
            if mdl.model_id==query_parameters.get("model_id"):
                instance = mdl
        else:
            if (mdl.model_name==query_parameters.get("model") and mdl.version==query_parameters.get("version") \
                    and mdl.author==query_parameters.get("author")):
                instance = mdl
    return instance

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/list_model', methods=['GET'])
def run_search():
    print('REQUEST LIST')
    return manager.search_to_JSON()


@app.route('/api/add_model', methods=['GET','POST'])
def run_add():
    query_parameters = request.form
    print('REQUEST ADD')
    if request.method == 'POST':
        if 'pdf' not in request.files:
            flask.flash('No file part')
            return flask.redirect('https://straiti3.org/blog/index.php/error/')

        # Store temporary inputs and configs
        wd = os.path.join(ENV_OUTPATH, str(uuid.uuid4()))
        os.mkdir(wd)

        inputfile = request.files['inputs']
        if len(inputfile.filename)>0:
            inputpath = os.path.join(wd, inputfile.filename)
            inputfile.save(inputpath)
            external_data = ""
        else:
            external_data = query_parameters.get('external_inputs')

        configfile = request.files['configs']
        configpath = os.path.join(wd, configfile.filename)
        configfile.save(configpath)

        pdffile = request.files['pdf']
        pdfpath = os.path.join(wd, pdffile.filename)
        pdffile.save(pdfpath)

        if pdffile.filename == '':
            flask.flash('No selected pdf file')
            return flask.redirect('https://straiti3.org/blog/index.php/error/')
        if configfile.filename == '':
            flask.flash('No selected input file')
            return flask.redirect('https://straiti3.org/blog/index.php/error/')

        name        = query_parameters.get('name')
        version     = query_parameters.get('version')
        format      = query_parameters.get('format')
        processor   = query_parameters.get('processor')
        task        = query_parameters.get('task')
        doi         = query_parameters.get('doi')
        author      = query_parameters.get('author')
        email       = query_parameters.get('email')
        location    = query_parameters.get('location')
        tag         = query_parameters.get('tag')

        if len(external_data)==0:
            data = {'name': name, 'doi':doi, 'version': version, 'author': author, 'email': email, 'location': location,
                    'pdf': '', 'tag':tag, 'format':format, 'task_type':task, 'processor_type':processor}
            mdl = model_manager.ModelInstance.create_instance(data, fromDatabase=False)
            manager.pushmodel(mdl, pdf=pdfpath, inputs=inputpath, configs=configpath)
        else:
            data = {'name': name, 'doi': doi, 'version': version, 'author': author, 'email': email,
                    'location': location, 'pdf': '', 'tag': tag, 'format': format, 'task_type': task,
                    'processor_type': processor, 'external_data':external_data}
            mdl = model_manager.ModelInstance.create_instance(data, fromDatabase=False)
            manager.pushmodel(mdl, pdf=pdfpath, configs=configpath)
        os.system('rm -rf {}'.format(wd))

        return flask.redirect("https://straiti3.org/blog/index.php/success/")
    return modelzoo_utils.add_model_html



@app.route('/api/modify_model', methods=['GET','POST'])
def run_modify():
    query_parameters = request.form
    instance = get_instance(query_parameters)
    if instance==[]:
        flask.redirect("https://straiti3.org/blog/index.php/error/")

    if request.method == 'POST':
        wd = os.path.join(ENV_OUTPATH, str(uuid.uuid4()))

        try:
            flag = 0
            if 'pdf' in request.files and request.files['pdf'].filename!="":
                pdffile = request.files['pdf']
                if not os.path.exists(wd):
                    os.mkdir(wd)
                pdfpath = os.path.join(wd, pdffile.filename)
                pdffile.save(pdfpath)
                flag = 1

            if 'inputs' in request.files and request.files['inputs'].filename!="":
                inputfile = request.files['inputs']
                if not os.path.exists(wd):
                    os.mkdir(wd)
                inputpath = os.path.join(wd, inputfile.filename)
                inputfile.save(inputpath)
                flag = flag+10

            if 'configs' in request.files and request.files['configs'].filename!="":
                configfile = request.files['configs']
                if not os.path.exists(wd):
                    os.mkdir(wd)
                configpath = os.path.join(wd, configfile.filename)
                configfile.save(configpath)
                flag = flag+100

            instance.model_name     = query_parameters.get('name')
            instance.version        = query_parameters.get('version')
            instance.format         = query_parameters.get('format')
            instance.processor      = query_parameters.get('processor')
            instance.task           = query_parameters.get('task')
            instance.model_doi      = query_parameters.get('doi')
            instance.author         = query_parameters.get('author')
            instance.email          = query_parameters.get('email')
            instance.location       = query_parameters.get('location')
            instance.tag            = query_parameters.get('tag')
            instance.external_data  = query_parameters.get('external_data')
            instance.verified       = model_manager.MODEL_STATUS['submitted']

            if flag==0:
                manager.pushmodel(instance)
            elif flag == 1:
                manager.pushmodel(instance, pdf=pdfpath)
            elif flag==10:
                manager.pushmodel(instance, inputs=inputpath)
            elif flag==100:
                manager.pushmodel(instance, configs=configpath)
            elif flag==101:
                manager.pushmodel(instance,  pdf=pdfpath,configs=configpath)
            elif flag==11:
                manager.pushmodel(instance,  pdf=pdfpath,inputs=inputpath)
            elif flag==110:
                manager.pushmodel(instance, inputs=inputpath, configs=configpath)
            elif flag==111:
                manager.pushmodel(instance, pdf=pdfpath, inputs=inputpath, configs=configpath)
            if flag>0:
                os.system('rm -rf {}'.format(wd))
        except:
            flask.redirect("https://straiti3.org/blog/index.php/error/")

    return flask.redirect("https://straiti3.org/blog/index.php/success/")


@app.route("/api/change_status",methods=['GET'])
def change_status():
    query_parameters = request.args
    instance = get_instance(query_parameters)
    if instance == []:
        return "{error:model unknown;}"
    new_status = query_parameters.get('status')
    instance.verified = new_status
    manager.pushmodel(instance)
    return flask.redirect("http://straiti3.org/blog")


@app.route("/api/delete",methods=['GET'])
def delete():
    query_parameters = request.args
    instance = get_instance(query_parameters)
    if instance == []:
        return "{error:model unknown;}"
    try:
        manager.deletemodel(instance)
    except:
        return "{return:error}"
    return flask.redirect("http://straiti3.org/blog")


@app.route("/api/build",methods=['GET'])
def run():
    query_parameters = request.args
    instance = get_instance(query_parameters)
    if (instance==[]):
        return "Model {} unknown".format(query_parameters.get("model"))
    engine.submit_job(instance)
    return flask.redirect("http://straiti3.org/blog")    #jsonify({"":torch.cuda.get_device_name(0)})


@app.route("/api/get_results",methods=['GET'])
def get_results():
    query_parameters = request.args
    instance = get_instance(query_parameters)
    if instance == []:
        return "{error:model unknown;}"

    author  = instance.author
    author  = author.replace(' ', '_')
    name    = instance.model_name
    name    = name.replace(' ','_')
    version = instance.version

    # Create folder structure
    wd = os.path.join(ENV_OUTPATH,author)
    wd = os.path.join(wd,name)
    wd = os.path.join(wd,version)
    outpath = os.path.join(wd, 'OUTPUTS')

    # TODO zip output repository
    try:
        outfile = outpath[:len(outpath)] + '.zip'
        cmd = "zip {} -r {}".format(outfile, outpath)
        os.system(cmd)
        return flask.send_file(outfile)
    except:
        return "{return:Error}"


@app.route("/api/get_pdf",methods=['GET'])
def get_pdf():
    query_parameters = request.args
    instance = get_instance(query_parameters)
    if instance == []:
        return "{error:model unknown;}"

    author  = instance.author
    author  = author.replace(' ', '_')
    name    = instance.model_name
    name    = name.replace(' ','_')
    version = instance.version

    # Create folder structure
    wd = os.path.join(ENV_OUTPATH,author)
    wd = os.path.join(wd,name)
    wd = os.path.join(wd,version)
    outpath = os.path.join(wd, 'OUTPUTS')

    # TODO zip output repository
    try:
        outpath = os.path.join(outpath, 'PDF')
        dpdf = os.listdir(outpath)
        fpdf = ""
        for fname in dpdf:
            fn = fname.split('.')
            if fn[len(fn)-1].lower()=='pdf':
                fpdf = fname
        if len(fpdf)==0:
            return "{return:Error no pdf found}"
        outfile = os.path.join(outpath,fpdf)
        return flask.send_file(outfile)
    except:
        return "{return:Error}"


@app.route("/api/download_files",methods=['GET'])
def download_files():
    query_parameters = request.args
    instance = get_instance(query_parameters)
    if instance == []:
        return "{error:model unknown;}"

    author  = instance.author
    author  = author.replace(' ', '_')
    name    = instance.model_name
    name    = name.replace(' ','_')
    version = instance.version

    # Create folder structure
    wd = os.path.join(ENV_OUTPATH,author)
    wd = os.path.join(wd,name)
    wd = os.path.join(wd,version)
    inpath = os.path.join(wd, 'INPUTS')

    # TODO zip output repository
    try:
        outfile = inpath[:len(inpath)] + '.zip'
        cmd = "zip {} -r {}".format(outfile, inpath)
        os.system(cmd)
        return flask.send_file(outfile)
    except:
        return "{return:Error}"


@app.route("/api/download_config",methods=['GET'])
def download_config():
    query_parameters = request.args
    instance = get_instance(query_parameters)
    if instance == []:
        return "{error:model unknown;}"

    author  = instance.author
    author  = author.replace(' ', '_')
    name    = instance.model_name
    name    = name.replace(' ','_')
    version = instance.version

    # Create folder structure
    wd = os.path.join(ENV_OUTPATH,author)
    wd = os.path.join(wd,name)
    wd = os.path.join(wd,version)
    config = os.path.join(wd, 'CONFIGS')

    # TODO zip output repository
    try:
        outfile = config[:len(config)] + '.zip'
        cmd = "zip {} -r {}".format(outfile, config)
        os.system(cmd)
        return flask.send_file(outfile)
    except:
        return "{return:Error}"





@app.route("/api/get_abstract",methods=['GET'])
def get_abstract():
    query_parameters = request.args
    instance = get_instance(query_parameters)
    if instance == []:
        return "{error:model unknown;}"
    wd = os.path.join(ENV_OUTPATH,'_abstract_')
    wd = os.path.join(wd,instance.model_id)
    if not os.path.exists(wd):
        os.mkdir(wd)
    path = manager.download_file(instance, 'pdf_file', wd)
    return flask.send_file(path)



app.run()

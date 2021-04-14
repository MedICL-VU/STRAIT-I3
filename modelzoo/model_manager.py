import os
from . import modelzoo_utils

import json
import yaml
import redcap

from modelzoo import log

import uuid

#config = []
#config['REGISTERY'] = "/Users/kilianhett/Experiments/STRAIT_NSF/modelzoo_registry"
LOGGER = log.setup_debug_logger('manager', None)

API_TOKEN = "07F402346C08493E5945DC7B32F57FA6"
API_URL = "https://redcap.vanderbilt.edu/api/"

MODEL_STATUS = {'submitted':'4','pending':'3', 'rejected':'2', 'built':'5', 'validated':'1'}

class ModelInstance():
    def __init__(self, id, name, location, author, email, pdf, version=None, doi=None, tag=None, verified=None,
                 format=None, processor=None, task=None, external_data=""):
        self.model_id = id
        self.model_doi = doi
        self.model_name = name
        self.location = location
        self.author = author
        self.email = email
        self.version = version
        self.verified = verified
        self.format = format
        self.processor = processor
        self.task = task
        self.pdf = pdf
        self.doi = doi
        self.tag = tag
        self.external_data = external_data

    def run(self):
        with open(self.location+'/mlbox.yaml', 'r') as stream:
            mlbox = yaml.full_load(stream)

        print(mlbox)
        for task in mlbox['tasks']:
            print(task)
            print('mlcommons_box_docker --mlbox=. --plateform={} --task={}'.format(self.location+'/config_dir/docker.yaml',
                                                                                       self.location+'/run/'+task))
            #os.system('mlcommons_box_docker --mlbox=. --plateform={} --task={}'.format(self.location+'/config_dir/docker.yaml',
            #                                                                           self.location+'/run/'+task))

    def getName(self):
        return self.model_name

    def getLocation(self):
        return self.location

    def getFile(self):
        return self.file

    def setFile(self, file):
        self.file = file

    def gen_instance(path,email):
        try:
            #Check config files
            yaml_config = path+'/config_dir/config.yaml'
            if os.path.exists(yaml_config):
                with open(yaml_config) as stream:
                    config = yaml.full_load(stream)
                name = config['model_name']
                version = config['model_version']
                author = config['analytic']['author']
            else:
                raise EOFError('Configuration does match requirements')
            # Run model
            # Generate dictionnary
            data = {}
            data['name'] = name
            data['author'] = author
            data['email'] = email
            data['location'] = path
            data['version'] = version
            data['file'] = modelzoo_utils.init_model_yaml(path, name, author, version)
            return ModelInstance.create_instance(data, False)
        except:
            raise EOFError('OOOO')
        return None


    def create_instance(data,fromDatabase=False):
        try:
            if fromDatabase:
                record_id = data['record_id']
            else:
                record_id = None
                status = '4'
            #

            if data.__contains__('version') and data.__contains__('doi') and data.__contains__('tag') and \
                    data.__contains__('format') and data.__contains__('task_type') and data.__contains__('processor_type') and \
                    data.__contains__('verified') and data.__contains__('external_data'):
                return ModelInstance(record_id, data['name'], data['location'], data['author'], data['email'],
                                     data['pdf'], doi=data['doi'], tag=data['tag'], version=data['version'],
                                     format=data['format'], task=data['task_type'], processor=data['processor_type'],
                                     verified=data['verified'], external_data=data['external_data'])
            elif data.__contains__('version') and data.__contains__('doi') and data.__contains__('tag') and\
               data.__contains__('format') and data.__contains__('task_type') and data.__contains__('processor_type') and\
               data.__contains__('verified'):
                 return ModelInstance(record_id, data['name'], data['location'], data['author'], data['email'],
                                 data['pdf'], doi=data['doi'], tag=data['tag'], version=data['version'],
                                 format=data['format'], task=data['task_type'], processor=data['processor_type'],
                                 verified=data['verified'])
            elif data.__contains__('version') and data.__contains__('doi') and data.__contains__('tag') and\
                data.__contains__('format') and data.__contains__('task_type') and data.__contains__('processor_type'):
                    return ModelInstance(record_id, data['name'], data['location'], data['author'], data['email'],
                                         data['pdf'], doi=data['doi'], tag=data['tag'], version=data['version'],
                                         format=data['format'], task=data['task_type'], processor=data['processor_type'],
                                         verified=status)
            elif data.__contains__('version') and data.__contains__('doi') and data.__contains__('tag'):
                return ModelInstance(record_id, data['name'], data['location'], data['author'], data['email'],
                                     data['pdf'], doi=data['doi'], tag=data['tag'], version=data['version'])
            elif data.__contains__('version') and data.__contains__('tag'):
                return ModelInstance(record_id, data['name'], data['location'], data['author'], data['email'],
                                     data['pdf'], version=data['version'], tag=data['tag'])
            elif data.__contains__('doi'):
                return ModelInstance(record_id, data['name'], data['location'], data['author'], data['email'],
                                     data['pdf'], doi=data['doi'])
        except:
            raise EOFError('Cannot create new instance of model: dictionary doesnt satisfy pre-require fields')
        return None

    def to_dict(self):
        return {'record_id':self.model_id, 'doi':self.model_doi, 'name':self.model_name, 'location':self.location,
                'author':self.author, 'email':self.email, 'version':self.version, 'pdf':self.pdf, 'tag':self.tag,
                'processor_type':self.processor,'format':self.format,'task_type':self.task,'verified':self.verified,
                'external_data':self.external_data}

    def __str__(self):
        return "ID: {}, DOI: {}, Name: {}, Author".format(self.model_id,self.model_doi,self.model_name,self.author)




# Interface REDCAP and manage ModelInstance
class ModelManager():
    def __init__(self, api_key, api_url):
        self._connect(api_url, api_key)

    def _connect(self, redcap_url, redcap_key):
        self._redcap = redcap.Project(redcap_url, redcap_key)

    def listmodel(self):
        data = self._redcap.export_records(fields=['record_id', 'name'])
        models = {}
        for i in range(len(data)):
            models[i] = self.pullmodel(data[i]['record_id'])
        return models

    def search_to_JSON(self):
        mdls = self.listmodel()
        data = {}
        data['modelzoo-version'] = 'v0.0.1'
        data['type-query'] = 'Model listing'
        data['model'] = []
        for l in mdls:
            mdl = mdls[l]
            try:
                data['model'].append({
                    'name':mdl.model_name,
                    'doi':mdl.doi,
                    'version':mdl.version,
                    'author':mdl.author,
                    'email':mdl.email,
                    'location':mdl.location,
                    'tag':mdl.tag,
                    'pdf':mdl.pdf
                })
            except:
                return('{Error}')
        return json.dumps(data, indent=4, sort_keys=False)

    def pullmodel(self, model_id):
        mdata = self._redcap.export_records(records=[model_id])
        data = mdata[0]
        try:
            return ModelInstance.create_instance(data,fromDatabase=True)
        except:
            raise (EOFError('Parameter non valid'))
        return None

    # Store config. files on redcap
    def pushmodel(self, model, pdf=None, inputs=None, configs=None):
        try:
            if model.model_id==None:
                new_id = str(uuid.uuid4())
                model.model_id=new_id
            dict = model.to_dict()
            num_processed = self._redcap.import_records([dict])

            mode = 'rb'
            if not pdf==None:
                with open(pdf, mode) as fobj:
                    self._redcap.import_file(model.model_id, 'pdf_file', pdf, fobj)
            if not inputs==None:
                with open(inputs, mode) as fobj:
                    self._redcap.import_file(model.model_id, 'inputs', inputs, fobj)
            if not configs==None:
                with open(configs, mode) as fobj:
                    self._redcap.import_file(model.model_id, 'configs', configs, fobj)

            return num_processed==1
        except:
            raise(EOFError("Model instanciation failed"))
        return None


    def download_file(self, mdl, file_field, output_dir):
        mdl_id = mdl.model_id
        try:
            content,header = self._redcap.export_file(mdl_id, file_field)
            mode = 'wb'
            print(header['name'])
            output = os.path.join(output_dir, header['name'])
            with open(output, mode) as f:
                f.write(content)
            return output
        except redcap.RedcapError:
            print(redcap.RedcapError)
            return "Error can't load file {}".format(file_field)


    def deletemodel(self, model):
        print(model.model_id)
        try:
            self._redcap.delete_file(model.model_id,'inputs')
        except:
            print('No inputs found')
        try:
            self._redcap.delete_file(model.model_id, 'configs')
        except:
            print('No configs found')
        try:
            self._redcap.delete_file(model.model_id, 'pdf_file')
        except:
            print('No abstract found')
        self._redcap.delete_records([model.model_id])



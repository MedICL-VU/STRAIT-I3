import os
import yaml
# from zipfile import ZipFile as zip
import shutil

# Import smtplib for the actual sending function
import smtplib,ssl
# Import the email modules we'll need
from email.message import EmailMessage

yaml_base = {'schema_type': 'modelzoo_invoke',
             'schema_version': '0.0.1'}
tmppath = './tmp_mdl/'



def init_model_yaml(path,name,author,version):
    try:
        list = os.listdir(path+'/tasks')

        tasks=[]
        if list.__contains__('download.yaml'):
            tasks.append('tasks/download.yaml')
        if list.__contains__('pre_process.yaml'):
            tasks.append('tasks/pre_process.yaml')
        if list.__contains__('run_test.yaml'):
            tasks.append('tasks/run_test.yaml')
        if list.__contains__('post_process.yaml'):
            tasks.append('tasks/post_process.yaml')
        if list.__contains__('gen_results.yaml'):
            tasks.append('tasks/gen_results.yaml')

        gen_mlbox_yaml(path, tasks, name, author, version)
        tpath = tmppath+name
        print(tpath)
        shutil.make_archive(tpath, 'zip', path)
        return tpath
    except:
        raise(EOFError('Cannot init model'))
    return None


def gen_mlbox_yaml(path,tasks,name,author,version):
    dict_file = {'schema_version': '1.0.0',
                 'schema_type': 'mlbox_root',
                 'name': name,
                 'author': author,
                 'version': version,
                 'mlbox_spec_version': '0.1.0',
                 'tasks': tasks}
    print(dict_file)
    try:
        with open(path+'/mlbox.yaml', 'w') as stream:
            documents = yaml.dump(dict_file, stream, sort_keys=False)
        return documents
    except:
        raise (EOFError('Cannot write yaml file'))
    return None


def send_email(mdl,content,subject):

    mdl_description = "Model information\n Name:{}\nVersion:{}\n"
    content = content + '\n\n\n' + mdl_description + '\n\n\n' + email_signature

    gmail_user = 'straiti3.nsf.convergence@gmail.com' #'you@gmail.com'
    gmail_password = 'AnonymPassword2020' #'P@ssword!'

    server_ssl = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server_ssl.ehlo()  # optional
    server_ssl.login(gmail_user, gmail_password)

    msg = EmailMessage()
    msg.set_content(content)#"Model submission have been registered")
    msg['Subject'] = subject #"Modelzoo submission notification"
    msg['From'] = "noreply@straiti3.nsf.convergence.com"
    msg['To'] = mdl.email

    server_ssl.send_message(msg)
    server_ssl.quit()





add_model_html = '''
    <!doctype html>
    <head>
    <style>
    h3 
    {
    margin-top:20px;
    margin-bottom:5px;
    }
    p {
      padding: 0;
      margin: 3px;
    }
    input, select
    {
        float:right;
        width:200px;
    } 
    form
    {
        width:400px
    }
    </style>
    </head>
    <body style="margin-left:30px;margin-top:10px;font-family:verdana;">
    <title>Add new Model</title>
    <h1>Submit model to STRAIT I3</h1>
    <form method=post enctype=multipart/form-data style="margin-left:10px;">
      <h3>Author information</h3>
      <p>Author name&emsp;<input type="text" name="author"></p>
      <p>Email &emsp;<input type="email" name="email"></p>
      <h3>Model information</h3>
      <p>Name &emsp;<input type="text" name="name"></p>
      <p>DOI &emsp;<input type="text" name="doi"></p>
      <p>Version &emsp;<input type="text" name="version"></p>
      <p>Tag &emsp;<input type="text" name="tag"></p>
      <p>Location &emsp;<input type="text" name="location"></p>
      <p> Type of task
      <select id="task" name="task">
        <option value="1">Segmentation</option>
        <option value="2">Classification</option>
        <option value="3">Synthesis</option>
        <option value="4">Regression</option>
      </select>
      </p>
      <p> Input format
      <select id="format" name="format">
        <option value="1">NIFTI</option>
        <option value="2">DICOM</option>
      </select>
      </p>
      <p>Processor type 
      <select id="processor" name="processor">
        <option value="1">CPU</option>
        <option value="2">GPU</option>
      </select>
      </p>
      <h3>Upload files</h3>
      <p>PDF &emsp;<input type="file" name="pdf"></p>
      <p>Input example &emsp;<input type="file" name="inputs"></p>
      <p>Config files &emsp;<input type="file" name="configs"></p>
      <input type="hidden" name=“redirection” value=“http://straiti3.org/blog”>
      <input type=submit value=Upload>
    </form>
    </body>
    '''


email_signature = '''
STRAIT I3 Team
Vanderbilt University
'''

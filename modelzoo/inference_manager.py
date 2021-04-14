import os
import threading
import time


class InferenceEngine():
    def __init__(self,manager,env_outpath):
        self.queue = []
        self.manager = manager
        self.ENV_OUTPATH = env_outpath

    def async_run(self, instance):
        instance.verified = '3'
        self.manager.pushmodel(instance)
        while len(self.queue) > 0:
            time.sleep(10)
        self.queue.append(instance)

        fid = open('log_build.log', 'w')
        try:
            author = instance.author
            author = author.replace(' ', '_')
            name = instance.model_name
            name = name.replace(' ', '_')
            version = instance.version
            proc = instance.processor

            fid.write('Author = {}\nModel = {}\n Version = {}\n Processor type = {}\n'.format(author, name, version,
                                                                                              proc))
            # Create folder structure
            wd = os.path.join(self.ENV_OUTPATH, author)
            fid.write('     {}\n'.format(wd))
            if not os.path.exists(wd):
                os.mkdir(wd)
            wd = os.path.join(wd, name)
            fid.write('     {}\n'.format(wd))
            if not os.path.exists(wd):
                os.mkdir(wd)
            wd = os.path.join(wd, version)
            fid.write('     {}\n'.format(wd))
            if os.path.exists(wd):
                cmd = "rm -r '{}'".format(wd)
                os.system(cmd)
            os.mkdir(wd)
            fid.write('- Folder structure created\n')

            # Download and Unzip Inputs
            inpath = os.path.join(wd, 'INPUTS')
            fid.write('     {}\n'.format(inpath))
            os.mkdir(inpath)
            fid.write('     {}\n'.format(instance.__str__()))
            if len(instance.external_data) == 0:
                input_file = self.manager.download_file(instance, 'inputs', wd)
                fid.write('     {}\n'.format(input_file))
            else:
                input_file = os.path.join(wd, 'inputs.zip')
                cmd = "sudo wget -O {} {}".format(input_file, instance.external_data)
                os.system(cmd)
            cmd = "sudo unzip '{}' -d '{}'".format(input_file, inpath)
            os.system(cmd)
            os.remove(input_file)
            # TODO Seems that there is an error in Riqiang model, this line is made to correct it
            if not os.path.exists(os.path.join(inpath, 'NIfTI')):
                os.mkdir(os.path.join(inpath, 'NIfTI'))
            fid.write('- Input added to folder structure\n')

            # Download and Unzip config
            configpath = os.path.join(wd, 'CONFIGS')
            os.mkdir(configpath)
            fid.write('- Config directory created')
            config_file = self.manager.download_file(instance, 'configs', wd)
            fid.write('     {}\n'.format(config_file))
            cmd = "unzip '{}' -d '{}'".format(config_file, configpath)
            os.system(cmd)
            os.remove(config_file)
            config = os.path.join(configpath)
            fid.write('- Config added to folder structure\n')

            # Set output directory
            outpath = os.path.join(wd, 'OUTPUTS')
            os.mkdir(outpath)
            # TODO Correct problem with Yuhankai docker
            os.mkdir('{}/temp'.format(outpath))
            fid.write('- Outputs created to folder structure\n')
            cmd = "bash '{}/run_docker.sh' '{}' '{}' '{}'".format(configpath, inpath, outpath, config)
            fid.write("{} \n".format(cmd))
            os.system(cmd)

            fid.write('- Model built : DONE\n')
            instance.verified = '5'
            self.manager.pushmodel(instance)
        except:
            fid.write('- Model built : ERROR\n')
            instance.verified = '2'
            self.manager.pushmodel(instance)
        self.queue.remove(instance)
        fid.close()

    def submit_job(self,instance):
        x = threading.Thread(target=self.async_run, args=(instance,), daemon=True)
        x.start()




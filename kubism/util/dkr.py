import os
from os import path
import time
import docker

from kubism.util.decorators import automate


_KUBISM_REGISTRY_ = 'srv.regan.analytics:3290'
_LOCAL_DOCKER_ = docker.from_env()


class Dockerfile:
    
    def __init__(self, parent_image=None, build_path='.', port=None):
        self._parent_image = parent_image
        self.build_path = build_path
        self._instructions = []
        self.update_from()
        if port is not None:
            self.add_port(port)

    
    def write(self, build_path=None):
        writepath = path.join(
            self.build_path if build_path is None else build_path, 
            'Dockerfile')
        with open(writepath, 'w') as f:
            for instr, arg in self._instructions:
                f.write(f'{instr} {arg}\n')
        return writepath


    def update_from(self, parent_image=None):
        if parent_image is not None:
            self.parent_image = parent_image 
        instr = ('FROM', self.parent_image)
        if len(self._instructions) > 0:
            self._instructions[0] = instr
        else:
            self._instructions.append(instr)



    def add_file(self, file, dest=None):
        dest = '/' if dest is None else dest
        #self.add_instr('ADD', f'{file} {dest}\n')
        self.add_instr('COPY', f'{file} {dest}\n')


    def add_cmd(self, args):
        arg_str = '['
        for arg in args:
            arg_str += f'"{arg}", '
        arg_str = arg_str[:-2] + ']'
        self.add_instr('CMD', arg_str)


    def add_run(self, arg):
        self.add_instr('RUN', arg)


    def add_port(self, port, proto='TCP'):
        self.add_instr('EXPOSE', f'{port}/{proto}')


    def add_instr(self, instr, arg):
        self._instructions.append((instr, arg))


    @property
    def parent_image(self):
        return self._parent_image

    @parent_image.setter
    def parent_image(self, parent_image):
        self._parent_image = parent_image
        self.update_from(self.parent_image)




class Image:

    run_delay = 2

    @automate
    def __init__(self, repo=None, tag=None, 
            parent_image=None, port=None,
            dockerfile_build_path='.',
            build_locally=True, host=None
            ):
        self.repo = repo
        self.tag = tag
        self.parent_image = parent_image
        self.port = port
        self.dockerfile_build_path = dockerfile_build_path
        self.container = None
        self.host = host
        self.build_locally = build_locally

        # Automation Steps
        self._created_dockerfile = False
        self._wrote_dockerfile = False
        self._built_dockerfile = False
        self._pushed_dockerfile = False
        self._removed_dockerfile = False

        # Run Controls
        self.volumes = None



    @property
    def docker(self):
        if self.host is not None:
            return docker.DockerClient(base_url=self.host)
        else:
            return docker.from_env()



    def create_dockerfile(self):
        self.dockerfile = Dockerfile(
                parent_image=self.parent_image,
                build_path=self.dockerfile_build_path,
                port=self.port) 
        self._created_dockerfile = True
        return self.dockerfile


    def write_dockerfile(self):
        self._wrote_dockerfile = True
        return self.dockerfile.write()


    def build(self):
        self._built_dockerfile = True
        if self.build_locally:
            host = _LOCAL_DOCKER_
        else:
            host = self.docker
        return host.images.build(
            path=self.dockerfile_build_path, 
            tag=self.full_name)

              
    def push(self):
        self._pushed_dockerfile = True
        self.docker.images.push(self.full_repo, tag=self.tag)


    def remove_dockerfile(self):
        self._removed_dockerfile = True
        os.remove(path.join(self.dockerfile_build_path, 'Dockerfile'))


    def automate(self):
        if not self._created_dockerfile:
            self.create_dockerfile()
        if not self._wrote_dockerfile:
            self.write_dockerfile()
        if not self._built_dockerfile:
            self.build()
        if not self._pushed_dockerfile:
            self.push()
        if not self._removed_dockerfile:
            self.remove_dockerfile()


    def run(self, detach=True, pull=True, volumes=None, **kwargs):
        if pull:
            self.docker.images.pull(self.full_repo, tag=self.tag)
        if volumes is not None:
            vols = {}
            for vol, mode in volumes:
                if isinstance(vol, str):
                    mnt = bnd = vol
                else:
                    mnt, bnd = vol
                vols.update(({mnt:{'bind':bnd, 'mode':mode}}))
            kwargs.update({'volumes':vols})
        self.container = self.docker.containers.run(
            self.full_name, detach=detach, **kwargs)
        if detach:
            message = f'{self.full_name} running detached as {self.container}'
            if self.port is not None:
                message += f' with port {self.port} exposed'
            print(message)
        time.sleep(Image.run_delay)


    def stop(self):
        print(f'{self.full_name} Stopping container: {self.container}')
        if self.container is not None:
            self.container.stop()
        print(f'{self.full_name} {self.container} container Stopped')


    @property
    def full_repo(self):
        if _KUBISM_REGISTRY_ is None:
            return f'{self.repo}'
        else:
            return f'{_KUBISM_REGISTRY_}/{self.repo}'

    @property
    def full_name(self):
        return self.full_repo + f':{self.tag}'



class App_Image(Image):

    @automate
    def __init__(self, app, app_dest='/app/', 
            app_exec=None,
            interpreter=None,
            **kwargs
            ):
        super().__init__(**kwargs)
        self.app = app
        self.app_dest = app_dest
        self.app_exec = app_exec
        if app_exec is not None:
            self.app_exec = app_exec
        else:
            self.app_exec = path.join(app_dest, path.basename(app))            
        self.interpreter = interpreter
        

    def create_dockerfile(self, instructions):
        super().create_dockerfile()
        self.dockerfile.add_run(f'mkdir {self.app_dest}')
        self.dockerfile.add_instr('WORKDIR', self.app_dest)
        self.dockerfile.add_file(self.app, dest=self.app_dest)
        for instr, arg in instructions:
            self.dockerfile.add_instr(instr, arg)
        self.dockerfile.add_cmd([self.interpreter, self.app_exec])
        return self.dockerfile




class PyApp_Image(App_Image):

    @automate
    def __init__(self, app, py_ver='3.8', **kwargs):
        super().__init__(app, **kwargs)
        self.py_ver = py_ver
        self.parent_image = f'python:{self.py_ver}'
        self.interpreter = 'python", "-u'
        if 'parent_image' in kwargs:
            self.parent_image = kwargs['parent_image']



class RPy_Image(PyApp_Image):

    @automate
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.parent_image = 'balenalib/raspberrypi3-python'



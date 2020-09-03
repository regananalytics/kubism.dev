from os import path
import socket
import yaml
import docker
from kubernetes import client, config

testpath = './k8s/test/'

registry = 'localhost:32000'
repo = 'py_echo'
tag = 'test'

high_port = 32121
namespace = 'default'

dep_name = 'py-echo'
srv_name = 'echo-srv'

docker_client = docker.from_env() # Load Docker Client
config.load_kube_config() # Load K8s configuration

def build_image():
    # Build Dockerfile using Docker
    return docker_client.images.build(path=testpath, tag=f'{registry}/{repo}:{tag}')


def push_image():
    # Push image to local registry
    docker_client.images.push(f'{registry}/{repo}', tag=tag)


def apply_deploy(api, body, name=''):
    # "Apply" deployment from yaml
    # Try to create a deployment, and if it already exists, patch it instead
    try:
        return api.create_namespaced_deployment(
            body=body, namespace=namespace)
    except:
        return api.patch_namespaced_deployment( name,
            body=body, namespace=namespace)


def apply_service(api, body, name=''):
    # "Apply" deployment from yaml
    # Try to create a deployment, and if it already exists, patch it instead
    try:
        return api.create_namespaced_service(
            body=body, namespace=namespace)
    except:
        return api.patch_namespaced_service( name,
            body=body, namespace=namespace)


def deploy_echo():
    with open(path.join(testpath, 'echo-dep.yml'), 'r') as f:
        dep = yaml.safe_load(f)
        dep['metadata']['name'] = dep_name # Set name
        v1 = client.AppsV1Api()
        resp = apply_deploy(v1, dep, 'py-echo')
        print(f'Deployment created. Status: {resp.metadata.name}')


def add_srv():
    with open(path.join(testpath, 'echo-srv.yml'), 'r') as f:
        srv = yaml.safe_load(f)
        srv['metadata']['name'] = srv_name # Set name
        api = client.CoreV1Api()
        resp = apply_service(api, srv, 'echo-srv')
        print(f'Service created. Status: {resp.metadata.name}')


def call_echo():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', high_port))
        s.sendall(b'Hello Server!')
        data = s.recv(1024)
    print('Recieved', repr(data))


def cleanup():
    client.CoreV1Api().delete_namespaced_service(srv_name, namespace=namespace)
    client.AppsV1Api().delete_namespaced_deployment(dep_name, namespace=namespace)


if __name__ == '__main__':
    build_image()
    push_image()
    deploy_echo()
    add_srv()
    call_echo()
    cleanup()
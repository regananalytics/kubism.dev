import socket, time
from kubism.util.dkr import PyApp_Image

import docker
import kubism.util.dkr as dkr

SERVER = '172.24.12.161'
CLIENT = '172.24.12.160'

echo_port = 8080

# Echo Test
# Create Echo Server
print('Building and pushing images...')

echo_srv = PyApp_Image('./examples/py/echo_server.py',
    parent_image = 'arm32v6/python:3-alpine',
    repo='echo', tag='server-v6', automate=True)
echo_srv.docker = docker.DockerClient(base_url=f'ssh://pi@{SERVER}')

echo_cli = PyApp_Image('./examples/py/echo_client.py',
    parent_image = 'arm32v7/python:3-buster',
    repo='echo', tag='client-v7', automate=True)
echo_cli.docker = docker.DockerClient(base_url=f'ssh://pi@{CLIENT}')

print(f'Run Server on server {SERVER} ...')
echo_srv.run(ports={f'{echo_port}/tcp':echo_port})

print('Waiting 3 seconds...')
time.sleep(3)

print(f'Run Client on client {CLIENT} ...')
print('Calling Server...')
echo_cli.run(ports={f'{echo_port}/tcp':echo_port})

#echo_srv.stop() # Not necessary
#echo_cli.stop()

print('DONE!')
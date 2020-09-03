import socket, time
from kubism.util.dkr import RPy_Image

import docker
import kubism.util.dkr as dkr

RPI = '172.24.12.160'
PORT = 8080

def get_temp():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((RPI, PORT))
        s.sendall(b'Hello Server!')
        return s.recv(1024)


print('Building and pushing images...')

therm_srv = RPy_Image('./examples/py/therm.py',
    repo='therm', tag='async', host=f'ssh://pi@{RPI}',
    automate=False, build_locally=False)
instructions = [('COPY', './kubism/deploy/kubio.py /app/')]
therm_srv.create_dockerfile(instructions)
therm_srv.automate()

print(f'Run Server on raspberry-pi {RPI} ...')
therm_srv.run(ports={f'{PORT}/tcp':PORT}, 
    volumes=[('/sys/bus/w1/devices/', '/sys/bus/w1/devices/', 'ro')])

for _ in range(10):
    print(get_temp())

therm_srv.stop()
therm_srv.docker.containers.prune()

print('Done')
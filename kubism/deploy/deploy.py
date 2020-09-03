import socket
import asyncio
import time

listen_addr = '0.0.0.0'
listen_port = 8080


class upstream:

    
    def __init__(self):
        self.callback = None
        self.conn = None
        self.reader = None
        self.writer = None


    def set_callback(self, func):
        self.callback = func
        

    def listen_sync(self, host=listen_addr, port=listen_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen()
            self.conn, addr = s.accept()
            with self.conn:
                print('Connected by', addr)
                while True:
                    data = self.conn.recv(1024)
                    return self.callback(data)


    def respond_sync(self, message):
        if self.conn is not None:
            self.conn.sendall(message)



    async def listen_async(self, host=listen_addr, port=listen_port):

        async def callback_wrapper(reader, writer):
            self.reader = reader
            self.writer = writer

            data = await self.reader.read(1024)
            print(f'Recieved {data}')
            await self.callback(data)

            self.reader = None
            self.writer = None

        server = await asyncio.start_server(
            callback_wrapper,
            host, port)

        async with server:
            print('Serve Forever...')
            await server.serve_forever()
        

    async def respond_async(self, message):
        print(f'Writing Message: {message}')
        self.writer.write(message)
        await self.writer.drain()
        self.writer.close()




class upstate:

    def __init__(self):
        pass




class Server(upstream, upstate):


    def __init__(self):
        self._mapped_ = [] # TODO: put mapped attributes here so they can be pushed in update
        self._last_update_ = None
        self.set_callback(self.report_state)


    def map_attr(self, *args):
        for arg in args:
            assert isinstance(arg, str)
            self._mapped_.append(arg)

    def get_state(self):
        pass


    def report_state(self):
        pass #state = self.get_state()


    def update_state(self):
        self._last_update_ = time.time()
        pass
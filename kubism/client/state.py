# Copyright 2020 Regan Analytics

from kubism.util import greek
from kubism.util.psql import DB

DEBUG = False


class State:

    t_idx = 0

    def __init__(self):        
        self.remote = DB()
        self.connect_to_remote()


    def connect_to_remote(self):
        if not self.remote_connected:
            self.remote.connect() # Connect to remote


    # Alias for remote.is_connected
    @property
    def remote_connected(self):
        if self.remote is not None:
            return self.remote.is_connected
        else:
            return False


    def create_table(self, table_name, *args, **kwargs):
        print(self.remote.create_table(table_name, *args, **kwargs))


    def insert_row(self, table_name, row_dict, **kwargs):
        print(self.remote.insert_row(table_name, row_dict, **kwargs))


    def add_column(self, table_name, col_dict, **kwargs):
        print(self.remote.add_column(table_name, col_dict, **kwargs))


    def drop_table(self, table_name, *args, **kwargs):
        print(self.remote.drop_table(table_name, **kwargs))
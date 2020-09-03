import os
import psycopg2
from dotenv import load_dotenv

DRY_RUN = True

def execute(cursor, query, debug=DRY_RUN):
    if not debug:
        cursor.execute(query)
    else:
        pass

load_dotenv()
connection = psycopg2.connect(os.environ['DATABASE_URL'])

class DB:

    is_connected = False

    def __init__(self):
        load_dotenv()
        try:
            self.url = os.environ['DATABASE_URL']
        except:
            print('DATABASE_URL has not been set in .env')
        
    
    def connect(self):
        """
        Connect to remote database. Return true if successful
        """
        if not self.is_connected:
            try:
                self.connection = psycopg2.connect(self.url)
                self.is_connected = True
                return True
            except:
                return False
                

    def create_table(self, table_name, cols=[], index=True, safe=True, **kwargs):
        query = 'CREATE TABLE '
        if safe:
            query += 'IF NOT EXISTS '
        query += f'"{table_name}" '
        query += '( '
        if index:
            if isinstance(index, str):
                query += index + ' SERIAL PRIMARY KEY, '
            else:
                query += 'idx SERIAL PRIMARY KEY, '
        if isinstance(cols, str):
            cols = [cols]
        for col in cols:
            query += f'{col}, '
        #if len(cols) > 1:
        query = query[:-2]
        query += ' );'
        return self.set_query(query, **kwargs), table_name


    def insert_row(self, table_name, row_dict, **kwargs):
        query = f'INSERT INTO "{table_name}" '
        cols = vals = ''
        for col in row_dict:
            cols += f'{col}, '
            vals += f"'{row_dict[col]}', "
        query += f'({cols[:-2]}) VALUES ({vals[:-2]})'
        return self.set_query(query, **kwargs)


    def add_column(self, table_name, col_dict, **kwargs):
        query = f'ALTER TABLE "{table_name}" '
        for col in col_dict:
            query += f'ADD COLUMN {col} '
            query += f'{col_dict[col]}, '
        query = query[:-2] + ';'
        return self.set_query(query, **kwargs)


    def drop_table(self, table_name, **kwargs):
        query = f'DROP TABLE "{table_name}"'
        return self.set_query(query, **kwargs)

            
    def set_query(self, query, verbose=True, debug=False):
        if verbose: print(query)
        if not debug:
            try:
                with self.connection:
                    with self.connection.cursor() as cursor:
                        execute(cursor, query)
                return True
            except:
                return False
        else:
            with self.connection:
                with self.connection.cursor() as cursor:
                    execute(cursor, query)
            return True
            

    def get_query(self, query, verbose=True, debug=False):
        if verbose: print(query)
        try:
            with self.connection:
                with self.connection.cursor() as cursor:
                    execute(cursor, query)
                    return True, cursor.fetchall()
        except:
            return False



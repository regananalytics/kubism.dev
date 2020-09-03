import os
import psycopg2

from dotenv import load_dotenv

load_dotenv()

connection = psycopg2.connect(os.environ['DATABASE_URL'])

CREATE_TEST_TABLE = """CREATE TABLE IF NOT EXISTS test_table (
    id SERIAL PRIMARY KEY,
    test_field TEXT,
    test_number INTEGER
);"""

ADD_TEST_ROW = """INSERT INTO test_table (test_field, test_number) VALUES ('test', %s)"""

def create_test_table():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_TEST_TABLE)
            cursor.execute(ADD_TEST_ROW, (12,))

        
def read_test_table():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM test_table')
            print(cursor.fetchall())


def cleanup():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute('DROP TABLE test_table')


if __name__ == '__main__':
    create_test_table()
    read_test_table()
    cleanup()
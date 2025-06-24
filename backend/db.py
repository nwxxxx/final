import pymysql
from pymysql.cursors import DictCursor
import click
from flask import current_app, g
from flask.cli import with_appcontext
import re

class MySQLConnection:
    def __init__(self, conn):
        self.conn = conn
    
    def execute(self, query, args=()):
        cursor = self.conn.cursor()
        cursor.execute(query, args)
        return cursor
    
    def commit(self):
        self.conn.commit()
    
    def close(self):
        self.conn.close()

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        sql_script = f.read().decode('utf8')
        sql_script = re.sub(r'--.*', '', sql_script)
        sql_commands = sql_script.split(';')
        sql_commands = [cmd.strip() for cmd in sql_commands if cmd.strip()]
        cursor = db.cursor()
        for cmd in sql_commands:
            cursor.execute(cmd)
        db.commit()
        cursor.close()

@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

def get_db():
    if 'db' not in g:
        conn = pymysql.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB'],
            port=current_app.config.get('MYSQL_PORT', 3306),
            cursorclass=DictCursor,
            charset='utf8mb4'
        )
        g.db = MySQLConnection(conn)
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
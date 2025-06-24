import os
import click
from flask import current_app, g
from flask.cli import with_appcontext
import MySQLdb
from dotenv import load_dotenv

load_dotenv()

'''
这里，
g 是一个特殊对象，独立于每一个请求。在处理请求过程中，
它可以用于储存可能多个函数都会用到的数据。把连接储存于其中，
可以多次使用， 而不用在同一个请求中每次调用 get_db 时都创建一个新的连接。

current_app 是另一个特殊对象，该对象指向处理请求的 Flask 应用。 
'''


def init_db():
    '''
    在init_db里，先连接数据库，然后执行'schema.sql'里的SQL语句建库建表
    '''
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        cursor = db.cursor()
        cursor.execute(f.read().decode('utf8'))
        cursor.close()


@click.command('init-db')  # 定义一个名为 init-db 命令行，后面可以命令行中运行它
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def get_db():  # 连接数据库
    if 'db' not in g:  # g.db类似一个全局变量
        g.db = MySQLdb.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', 'nwx2698199'),
            database=os.getenv('MYSQL_DATABASE', 'flask_forum'),
            charset='utf8mb4'
        )
        g.db.autocommit(True)
    return g.db


def close_db(e=None):
    db = g.pop('db', None)  # 取得g中的db

    if db is not None:
        db.close()  # 关闭数据库连接


def init_app(app):
    app.teardown_appcontext(close_db)
    '''
    teardown_appcontext 是 Flask 的一个装饰器，用于注册在请求上下文结束时需要执行的函数
    用于在请求结束后自动关闭数据库连接
    '''
    app.cli.add_command(init_db_command)
    '''
    这行代码向 Flask 的命令行接口（CLI）添加了一个新的命令
    允许你通过命令行来初始化数据库
    '''


def query_db(query, args=(), one=False):
    """执行查询并返回结果"""
    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(query, args)
    rv = cursor.fetchall()
    cursor.close()
    return (rv[0] if rv else None) if one else rv

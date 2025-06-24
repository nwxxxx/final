import os
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import timedelta

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        # 修改为MySQL配置
        MYSQL_HOST='localhost',
        MYSQL_USER='root',
        MYSQL_PASSWORD='nwx2698199',
        MYSQL_DB='UserDatabases',
        MYSQL_PORT=3306,
        JWT_SECRET_KEY='your-secret-key',
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=1))
    
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    from . import db
    db.init_app(app)
    
    from . import auth
    app.register_blueprint(auth.bp)
    
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
        
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden'}), 403

    return app
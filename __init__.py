from flask import Flask
from flask_mysql_connector import MySQL
from config import DB_USERNAME, DB_PASSWORD, DB_NAME, DB_HOST, SECRET_KEY, CLOUD_NAME, CLOUD_API_KEY, CLOUD_API_SECRET, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, MAIL_USE_TLS, MAIL_USE_SSL
from mysql.connector.errors import IntegrityError
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_mail import Mail


import cloudinary
mysql = MySQL()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=SECRET_KEY,
        MYSQL_USER=DB_USERNAME,
        MYSQL_PASSWORD=DB_PASSWORD,
        MYSQL_DATABASE=DB_NAME,
        MYSQL_HOST=DB_HOST
        #BOOTSTRAP_SERVE_LOCAL=BOOTSTRAP_SERVE_LOCAL
    )
    app.config. from_mapping(
        MAIL_SERVER = MAIL_SERVER,
        MAIL_PORT = MAIL_PORT,
        MAIL_USERNAME = MAIL_USERNAME,
        MAIL_PASSWORD = MAIL_PASSWORD,
        MAIL_USE_TLS = MAIL_USE_TLS,
        MAIL_USE_SSL = False
    )
    cloudinary.config(
        cloud_name = CLOUD_NAME,
        api_key = CLOUD_API_KEY,
        api_secret = CLOUD_API_SECRET
    )
    mysql.init_app(app)
    CSRFProtect(app)
    
    mail.init_app(app)

    from .routes import routes
    from .auth import auth

    app.register_blueprint(routes, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')

    # Initialize LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Import your User model
    from .models import Users

    @login_manager.user_loader
    def load_user(id):
        return Users.query.get(int(id))


    return app

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flaskext.markdown import Markdown

db = SQLAlchemy()


def create_app(**config_overrides):
    app = Flask(__name__)
    app.config.from_pyfile('settings.py')
    app.config.update(config_overrides)
    db.init_app(app)
    migrate = Migrate(app, db)
    Markdown(app)

    from blog.views import blog_app
    from author.views import author_app

    app.register_blueprint(blog_app)
    app.register_blueprint(author_app)

    return app

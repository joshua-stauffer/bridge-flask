import os
from flask_migrate import Migrate, upgrade
from app import create_app, db
from app.models import User, Post, PostContents, Quote, Node, Video, Resource

from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    raise Exception('Couldnt load environmental variables')

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor 
def make_shell_context():
    return dict(
        db=db, Node=Node, Post=Post, PostContents=PostContents,
        User=User, Quote=Quote, Video=Video, Resource=Resource
    )


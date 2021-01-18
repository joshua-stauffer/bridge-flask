import os
import logging
logging.basicConfig(filename='flask_base.log', level=logging.DEBUG)
from flask_migrate import Migrate, upgrade
from app import create_app, db
from app.models import User, Post, PostContents, Quote, Node, Video, Resource

from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    raise Exception('Couldnt load environmental variables')
    logging.error('Unable to load environmental variables')

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.logger.info(f'got env variablesL {os.environ}')
app.logger.info('database connection is ', app.config.get('DATABASE_URL'), None) 
migrate = Migrate(app, db)


@app.cli.command()
def test():
    """Run all tests"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.shell_context_processor 
def make_shell_context():
    return dict(
        db=db, Node=Node, Post=Post, PostContents=PostContents,
        User=User, Quote=Quote, Video=Video, Resource=Resource
    )

@app.cli.command()
def deploy():
    """deployment tasks"""
    
    #upgrade database to latest version
    upgrade()

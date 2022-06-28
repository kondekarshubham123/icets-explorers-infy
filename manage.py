import os
import uvicorn
import typer
from app.main.config import Config,basedir
from app import fast_app

manager = typer.Typer()


@manager.command(name='run')
def run():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= os.path.join(basedir,"configs","dev-racer-354316-188df6515822.json")
    port = Config.get_value('port')
    uvicorn.run("manage:fast_app",host="0.0.0.0",port=int(port),use_colors=True)

if __name__ == "__main__":
    manager()
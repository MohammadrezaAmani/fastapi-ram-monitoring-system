from uvicorn import run

from monitor import app

if __name__ == "__main__":
    run(app=app)

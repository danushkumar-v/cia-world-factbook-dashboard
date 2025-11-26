"""
WSGI Entry Point for Production Deployment
"""
from app import app

server = app.server

if __name__ == "__main__":
    server.run()

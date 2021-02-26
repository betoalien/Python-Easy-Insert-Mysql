#!/usr/local/bin/python

from flup.server.fcgi import WSGIServer
import sys
sys.path.insert(0, '/usr/local/lib/python3.8/dist-packages/')

from app import app

if __name__ == '__main__':
    WSGIServer(app).run()
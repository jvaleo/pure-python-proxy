#!/usr/bin/python
"""
Simple proxy server
"""

import logging
import re
import socket
import sys
import threading

HOST = '0.0.0.0'
PORT = 8181

LOG = logging.getLogger(__name__)
LOG_HANDLER = logging.StreamHandler(sys.stdout)
FORMAT = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
LOG_HANDLER.setFormatter(FORMAT)
LOG.addHandler(LOG_HANDLER)
LOG.setLevel(logging.DEBUG)

def multithreading_server(client, addr):
    """
    Threading handle
    """
    data = client.recv(1024)
    lock = threading.Lock()
    while 1:
        lock.acquire()
        lock.release()
    LOG.debug('Client closed: {0}'.format(addr))
    lock.close()


def get_headers(data):
    """
    Get the headers, if it is a GET then pass to check proxy server and pass the request
    """
    headers = {}
    accepted_methods = [ 'POST', 'GET']
    lines = data.splitlines()
    for i in lines:
        if 'GET' in i or 'POST' in i: # Only support GET or POST
            request_path = i.split()[1]
            if re.match(r"\/service_1\/.*", request_path):
                request = request_path.split('/')[2]
                proxy_path = '10.0.0.10:8000'
            elif re.match(r"\/service_2\/.*", request_path):
                request = request_path.split('/')[2]
                proxy_path = '10.0.0.20:8001'
            elif re.match(r"\/service_3\/.*", request_path):
                request = request_path.split('/')[2]
                proxy_path = '10.0.0.30:8002'
            elif re.match(r"\/service_4\/.*", request_path):
                request = request_path.split('/')[2]
                proxy_path = '10.0.0.30:8003'
            return request, proxy_path
            break
    request, proxy_path = None
    return request, proxy_path

def web_server():
    """
    Listen for requests on PORT
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((HOST, PORT))
    except Exception as e:
        LOG.error('Unable to bind to {0}:{1}'.format(HOST,PORT))
        sys.exit()
    sock.listen(5)
    while True:
        conn, addr = sock.accept()
        LOG.debug('Client {0}'.format(addr))
        data = conn.recv(1024)
        try:
            request, proxy_path = get_headers(data)
        except Exception as e:
            LOG.error('Unable to parse request/proxy_path')
        threading.Thread(target = multithreading_server, args = (conn, addr)).start()
        proxy_connection(proxy_path, request)

def proxy_connection(host, data):
    """
    Take in a host:port and data and send it to the destination
    """
    dest_ip = host.split(':')[0]
    dest_port = int(host.split(':')[1])
    forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    forward.settimeout(1)
    try:
        forward.connect((dest_ip, dest_port))
        LOG.debug('{0} {1}'.format(dest_ip, dest_port))
    except Exception as e:
        LOG.error('Unable to connect to {0} on {1} - {2}'.format(dest_ip, dest_port, e))
    try:
        forward.send(data)
        LOG.debug('{0} {1} {2}'.format(dest_ip, dest_port, data))
        forward.close()
    except Exception as e:
        LOG.error('Unable to send data {0} on {1} - {2} {3}'.format(dest_ip, dest_port, data,  e))

if __name__ == '__main__':
    try:
        while True:
            web_server()
    except KeyboardInterrupt:
        LOG.info('Caught KeyboardInterrupt')
        sys.exit()

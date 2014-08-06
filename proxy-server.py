#!/usr/bin/python
import socket
import re
import threading

HOST = '0.0.0.0'
PORT = 8181


def multithreading_server(client, addr):
    """
    Threading handle
    """
    data = client.recv(1024)
    lock = threading.Lock()
    while 1:
        lock.acquire()
        lock.release()
    print 'Client closed:', addr
    lock.close()


def get_headers(data):
    """
    Get the headers, if it is a GET then pass to check proxy server and pass the request
    """
    headers = {}
    lines = data.splitlines()
    for i in lines:
        if 'GET' in i:
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

def web_server():
    """
    Listen for requests on PORT
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)
    while True:
        conn, addr = sock.accept()
        print('Client {0}'.format(addr))
        data = conn.recv(1024)
        request, proxy_path = get_headers(data)
        threading.Thread(target = multithreading_server, args = (conn, addr)).start()
        proxy_connection(proxy_path, request)

def proxy_connection(host, data):
    """
    Take in a host:port and data and send it to the destination
    """
    dest_ip = host.split(':')[0]
    dest_port = int(host.split(':')[1])
    dest_ip = 'localhost' #TODO REMOVE THIS
    forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        forward.connect((dest_ip, dest_port))
    except Exception as e:
        print('Unable to connect to {0} on {1} - {2}'.format(dest_ip, dest_port, e)
    try:
        forward.send(data)

try:
    while True:
        web_server()
except KeyboardInterrupt:
    exit()

#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import socketserver
import socket
import os
from xml.sax import make_parser
from xml.sax import ContentHandler
#import xml.etree.ElementTree as ET
import time

class Server_Constructor(ContentHandler):

    def __init__(self):

        self.tags = []
        self.dicc = {'account': ['username', 'passwd'],
                     'uaserver': ['ip', 'port'],
                     'rtpaudio': ['port'],
                     'regproxy': ['ip', 'port'],
                     'log': ['path'],
                     'audio': ['path']}

    def startElement(self, name, attrs):

        if name in self.dicc:
            dicc_aux = {}
            for atribute in self.dicc[name]:
                dicc_aux[atribute] = attrs.get(atribute, "")
            self.tags.append([name, dicc_aux])

    def get_tags(self):
        return self.tags

#Condiciones de entrada
if len(sys.argv) != 2:
	sys.exit("Usage: python3 uaserver.py config")

#Extracción de lo introducido por la linea de comandos
CONFIG = sys.argv[1]#Fichero de configuración del UA

#Inicio del manejador
#Manejo del fichero de configuración
parser = make_parser()
server_handler = Server_Constructor()
parser.setContentHandler(server_handler)
parser.parse(open(CONFIG))
info = server_handler.get_tags()

#Extracción de la información de configuración
username = info[0][1]['username']
password = info[0][1]['passwd']
server_ip = info[1][1]['ip']
server_port = info[1][1]['port']
rtp_port = info[2][1]['port']
proxy_ip = info[3][1]['ip']
proxy_port = info[3][1]['port']
log_path = info[4][1]['path']
audio_path = info[5][1]['path']

#Procedimiento que genera una nueva entrada de log
def do_log(entry):

    log = open(log_path, 'a+')
    log.write('\r\n' + time.strftime('%Y%m%d%H%M%S ', time.gmtime(time.time())) + entry)
    log.close()

#Procedimiento que borra el fichero de log
def delete_log():
    log= open(log_path, 'w')
    log.close()

class SIP_UA_Handler(socketserver.DatagramRequestHandler):
    """
    SIP User Agent server class
    """
    def handle(self):
        while 1:
            line = self.rfile.read()
            if not line:
                break
            request = line.decode('utf-8')
            log_entry ="Received from "+proxy_ip+':'+str(proxy_port) +' '+request.replace('\r\n',' ')
            do_log(log_entry)
            print("\r\nReceived from proxy-- " + request)
            METHOD = request.split(' ')[0]
            if METHOD == 'INVITE':
                self.wfile.write(b'SIP/2.0 100 Trying\r\n')
                self.wfile.write(b"SIP/2.0 180 Ring\r\n")
                reply = "SIP/2.0 200 OK\r\n"
                reply += 'Content-Type: application/sdp\r\n\r\n'
                reply += 'v=0\r\n'
                reply += 'o=' + username + ' ' + server_ip + '\r\n'
                reply += 's=mysession\r\n'
                reply += 't=0\r\n'
                reply += 'm=audio ' + rtp_port + ' RTP\r\n'
                self.wfile.write(bytes(reply,'utf-8'))
                log_entry ="Sending to "+proxy_ip+':'+str(proxy_port) +' '+reply.replace('\r\n',' ')
                do_log(log_entry)
                print("Sending-- SIP/2.0 100 Trying\r\nSIP/2.0 180 Ring\r\n" + reply)
            elif METHOD == 'ACK':
                aEjecutar = "./mp32rtp -i " + server_ip
                aEjecutar += " -p " + rtp_port + " < " + audio_path
                os.system(aEjecutar)
                log_entry ="Running " + aEjecutar
                do_log(log_entry)
                print("Vamos a ejecutar", aEjecutar)
            elif METHOD == 'BYE':
                reply = "SIP/2.0 200 OK\r\n"
                self.wfile.write(bytes(reply,'utf-8'))
                log_entry ="Sending to "+proxy_ip+':'+str(proxy_port) +' '+reply.replace('\r\n',' ')
                do_log(log_entry)
                print("Sending-- " + reply)
            else:
                reply = "SIP/2.0 405 Method Not Allowed\r\n"
                self.wfile.write(bytes(reply,'utf-8'))
                log_entry ="Sending to "+proxy_ip+':'+str(proxy_port) +' '+reply.replace('\r\n',' ')
                do_log(log_entry)
                print("Sending-- " + reply)

if __name__ == "__main__":
    #delete_log()
    serv = socketserver.UDPServer(('', int(server_port)), SIP_UA_Handler)
    log_entry = "Starting server..."
    log_entry = log_entry.replace('\n',' ')
    do_log(log_entry)
    print("\r\nServer " + username + " listening at port: " + server_port + "...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        log_entry = "Finishing server..."
        log_entry = log_entry.replace('\r\n',' ')
        do_log(log_entry)
        print("Finishing server.")

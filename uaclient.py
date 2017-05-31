#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa cliente que abre un socket a un servidor
"""

import socket
import sys
import os
from xml.sax import make_parser
from xml.sax import ContentHandler
import hashlib
import time

class UA_Constructor(ContentHandler):

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

#
#Condiciones de entrada
#
if len(sys.argv) != 4:
	sys.exit("Usage: python uaclient.py config method option")
#
#Extracción de lo introducido por la linea de comandos
#
#Fichero de configuración del UA
CONFIG = sys.argv[1]
#Metodo que quiere enviar el cliente
METHOD = sys.argv[2]
#Opción elegida de inicio
OPTION = sys.argv[3]

#
#Inicio del manejador
#
#Manejo del fichero de configuración
parser = make_parser()
client_handler = UA_Constructor()
parser.setContentHandler(client_handler)
parser.parse(open(CONFIG))
info = client_handler.get_tags()

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

#Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((proxy_ip, int(proxy_port)))

try:
    #Actuaciones en función del método especificado por el cliente
    if METHOD == "REGISTER":
	    #Estructura de mensaje REGISTER
	    request = 'REGISTER sip:' +username + ':' + server_port + ' SIP/2.0\r\n'
	    request += 'Expires:' + OPTION + '\r\n'

    elif METHOD == "INVITE":
	    #Estructura de mensaje INVITE
	    request = 'INVITE sip:' + OPTION + ' SIP/2.0\r\n'
	    request += 'Content-Type: application/sdp\r\n\r\n'
	    request += 'v=0\r\n'
	    request += 'o=' + username + ' ' + server_ip + '\r\n'
	    request += 's=mysession\r\n'
	    request += 't=0\r\n'
	    request += 'm=audio ' + rtp_port + ' RTP\r\n'

    elif METHOD == "BYE":
	    #Estructura de mensaje BYE
	    request = 'BYE sip:'+ OPTION + ' SIP/2.0\r\n'
    else:
	    request = METHOD + ' sip:'+ OPTION + ' SIP/2.0\r\n'

    delete_log()
    entry = "Starting client: "+username
    do_log(entry)
    entry = "Socket connected to Proxy "+proxy_ip+":"+str(proxy_port)
    do_log(entry)
    #Envio Request al Proxy
    my_socket.send(bytes(request, 'utf-8') + b'\r\n')
    log_entry ="Sending to "+proxy_ip+':'+str(proxy_port) +' '+request.replace('\r\n',' ')
    do_log(log_entry)
    print("Sendin to proxy-- " , request)
    #Recibo contestacion
    data = my_socket.recv(1024)
    reply = data.decode('utf-8')
    log_entry ="Received from "+proxy_ip+':'+str(proxy_port) +' '+reply.replace('\r\n',' ')
    do_log(log_entry)
    print('Received -- ', reply)
    code = reply.split(' ')[1].split(' ')[0]
    #print('Code--> ' + code)
    #if reply.startswith('SIP/2.0 401 Unauthorized'):
    if code == "401":
        aux = hashlib.md5()
        nonce = reply.split('=')[1]
        aux.update(bytes(password,'utf-8') + bytes(nonce,'utf-8'))
        response = aux.hexdigest()
	    #Estructura de REGISTER con autorizacion
        Request = 'REGISTER sip:'+username+':'+server_port+' SIP/2.0\r\n'
        Request += 'Expires:'+OPTION+'\r\n'+ 'Authorization: Digest response='
        Request += response + '\r\n'
	    ####PASAR PRINT AL LOG
        print("Sending REGISTER (+login): " , Request)
	    ####PASAR PRINT AL LOG
        #Envio REGISTER con Autorización al Proxy
        my_socket.send(bytes(Request, 'utf-8'))
        #Recibo contestacion
        data = my_socket.recv(1024)
        reply = data.decode('utf-8')
    #elif reply.startswith("SIP/2.0 100 Trying\r\n"):
    elif code == "100":
        answer = reply.split()
        if answer[7] == "200":
            receiver = answer[12].split('=')[1]
            request = "ACK sip:" + receiver + " SIP/2.0"
            print("Sending ACK")
            my_socket.send(bytes(request, 'utf-8'))
            aEjecutarVLC = 'cvlc trp://@127.0.0.1:' + rtp_port +'> /dev/null &'
            print("Vamos a ejecutar " + aEjecutarVLC)
            os.system(aEjecutarVLC)
            aEjecutar = "./mp32rtp -i " + server_ip
            aEjecutar += " -p " + rtp_port + " < " + audio_path
            print("Vamos a ejecutar", aEjecutar)
            os.system(aEjecutar)
    entry = "Finishing socket."
    do_log(entry)
    print("Finishing socket...")

except ConnectionRefusedError:
    print("ERROR - Connection refused")
    print("Finishing socket")

#Cerramos todo
my_socket.close()

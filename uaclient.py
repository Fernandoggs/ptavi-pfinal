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
#######TRAZA#######
##print(info)
#######TRAZA#######

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

#Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((proxy_ip, int(proxy_port)))

######
# FALTA AÑADIR EL 'Starting...' AL FICHERO LOG
######

#Actuaciones en función del método especificado por el cliente
if METHOD == "REGISTER":
	#Estructura de mensaje REGISTER
	Request = 'REGISTER sip:'
	Request += username + ':' + server_port
	Request += ' SIP/2.0\r\n'
	Request += 'Expires:' + OPTION + '\r\n'

elif METHOD == "INVITE":
	#Estructura de mensaje INVITE
	Request = 'INVITE sip:' + OPTION + ' SIP/2.0\r\n'
	Request += 'Content-Type: application/sdp\r\n'
	Request += 'v=0\r\n'
	Request += 'o=' + username + ' ' + server_ip + '\r\n'
	Request += 's=mysession\r\n'
	Request += 't=0\r\n'
	Request += 'm=audio ' + rtp_port + ' RTP\r\n'

    ####FALTA SDP
elif METHOD == "BYE":
	#Estructura de mensaje BYE
	Request = 'BYE sip:'+ OPTION + ' SIP/2.0\r\n'
else:
    print("The method entered is wrong, it must be REGISTER, INVITE or BYE")
    sys.exit("(Mind the capital letters)")


####PASAR PRINT AL LOG
print("Enviando: " , Request)
####PASAR PRINT AL LOG
#Envio Request al Proxy
my_socket.send(bytes(Request, 'utf-8') + b'\r\n')
#Recibo contestacion
data = my_socket.recv(1024)
Reply = data.decode('utf-8')
####PASAR PRINT AL LOG
print('Recibido -- ', Reply)
####PASAR PRINT AL LOG
code = Reply.split(' ')[1]
print("Code = " + code)
if code == '401':
    aux = hashlib.md5()
    nonce = Reply.split('=')[1]
    aux.update(bytes(password,'utf-8') + bytes(nonce,'utf-8'))
    response = aux.hexdigest()
	#Estructura de REGISTER con autorizacion
    Request = 'REGISTER sip:'
    Request += username + ':' + server_port
    Request += ' SIP/2.0\r\n'
    Request += 'Expires:' + OPTION + '\r\n'
    Request += 'Authorization: Digest response= ' + response
	####PASAR PRINT AL LOG
    print("Enviando REGISTER con Autorización: " , Request)
	####PASAR PRINT AL LOG
    #Envio REGISTER con Autorización al Proxy
    my_socket.send(bytes(Request, 'utf-8') + b'\r\n')
    #Recibo contestacion
    data = my_socket.recv(1024)
    Reply = data.decode('utf-8')
    ####PASAR PRINT AL LOG
    print('Recibido -- ', Reply)
    ####PASAR PRINT AL LOG
"""
elif Reply[1] == '100' and Reply[4] == '180' and Reply[7] == '200':
	#Estructura de mensaje ACK
    ACK = 'ACK sip:'+ OPTION + ' SIP/2.0\r\n'
	####PASAR PRINT AL LOG
    print("Enviando: " + ACK)
	####PASAR PRINT AL LOG
    my_socket.send(bytes(ACK, 'utf-8') + b'\r\n')
    data = my_socket.recv(1024)
"""

print("Terminando socket...")

#Cerramos todo
my_socket.close()
print("Fin.")

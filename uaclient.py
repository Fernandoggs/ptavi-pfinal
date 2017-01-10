#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa cliente que abre un socket a un servidor
"""

import socket
import sys

#Condiciones de entrada
if not len(sys.argv) != 4:
	sys.exit("Usage: python uaclient.py config method opcion")

"""
Extracción de lo introducido por la linea de comandos
"""
#Fichero de configuración del UA
CONFIG = sys.argv[1]
#Metodo que quiere enviar el cliente
METHOD = sys.argv[2]
#Opción elegida de inicio
OPTION = sys.argv[3]


server_aux = log_str.split('@')[1]
SERVER = server_aux.split(':')[0]

#Nick de la persona a la que va dirigido el mensaje
NICK = log_str.split(':')[0]

#Puerto SIP
PORT = int(server_aux.split(':')[1])

#Contenido que vamos a enviar
REQUEST = METHOD + ' sip:' + NICK + ' SIP/2.0\r\n'
ACK = 'ACK sip:'+ NICK + ' SIP/2.0\r\n'
BYE = 'BYE sip:'+ NICK + ' SIP/2.0\r\n'

#Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect(('127.0.0.1', PORT))

if METHOD == "INVITE":
    print("Enviando: " , REQUEST)
    my_socket.send(bytes(REQUEST, 'utf-8') + b'\r\n')
    data = my_socket.recv(1024)
    Reply = data.decode('utf-8')

print('Recibido -- ', Reply)
if Reply == "SIP/2.0 100 Trying\r\nSIP/2.0 180 Ring\r\nSIP/2.0 200 OK\r\n\r\n":
    print("Enviando: " + ACK)
    my_socket.send(bytes(ACK, 'utf-8') + b'\r\n')
    data = my_socket.recv(1024)
    print("Enviando: " + BYE)
    my_socket.send(bytes(BYE, 'utf-8') + b'\r\n')
    data = my_socket.recv(1024)

print("Terminando socket...")

#Cerramos todo
my_socket.close()
print("Fin.")

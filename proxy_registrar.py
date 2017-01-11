#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor SIP Register simple
"""

import socketserver
import sys
import json
import time
import uaclient

#
#Condiciones de entrada
#
if not len(sys.argv) != 2:
	sys.exit("Usage: python uaserver.py config")
#
#Extracción de lo introducido por la linea de comandos
#
#Fichero de configuración del UA
CONFIG = sys.argv
#
#Inicio del manejador
#
#Manejo del fichero de configuración
parser = make_parser()
server_handler = uaclient.UA_Constructor()
parser.setContentHandler(server_handler)
parser.parse(open(CONFIG))
info = server_handler.get_tags()
#######TRAZA#######
print(info)
#######TRAZA#######

server_ip = info[0][1]['ip']
server_port = info[0][1]['port']
clients_fich = info[1][1]['path']
passwd_fich = info[1][1]['passwdpath']
log_fich = info[2][1]['path']
nonce = '4815162342'

#Usuarios registrados
class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """
    SIP REGISTER server class
    """
    users_dicc: {}
    #Abro el fichero de registro de clientes en modo escritura
    def register2json(self):
        json.dump(self.users_dicc, open(clients_fich,'w'))

    #Compruebo si existe el fichero y lo leo
    def json2register(self):


if __name__ == "__main__":
	#Crea un servidor UDP.Hay q pasar 2 parametros: ip y puerto donde voy a escuchar /
	# y la clase
    serv = socketserver.UDPServer(('', int(sys.argv[1])), SIPRegisterHandler)
    print("Lanzando servidor UDP de eco...")
    #Se crea esta excepción para q al salir del servidor con crtl+c salga el mensaje de Finalizado
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")

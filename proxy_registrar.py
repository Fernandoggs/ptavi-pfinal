#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor SIP Register simple
"""

import socketserver
import sys
import json
import time

#Manejador de datagramas
#Un servidor echo es un servidor que envia lo mismo que recibe
class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """
    SIP REGISTER server class
    """
    users_dicc: {}
    client_ip: ''
    lists = []
    def handle(self):
        """ Método principal """
        if self.lists == []:
            self.json2registered()

        print(self.client_address)

        print("El cliente nos manda ", line.decode('utf-8'))

        if line.decode('utf-8').startswith('REGISTER'):
            self.client_ip = deco[deco.find(':')]


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

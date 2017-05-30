#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor SIP Register simple
"""

import socketserver
import sys
import json
import time
import random
import hashlib
from xml.sax import make_parser
from xml.sax import ContentHandler

class Proxy_Constructor(ContentHandler):

    def __init__(self):

        self.tags = []
        self.dicc = {'server': ['name', 'ip', 'port'],
                     'database': ['path', 'passwdpath'],
                     'log': ['path']}

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
if not len(sys.argv) != 1:
	sys.exit("Usage: python uaserver.py config")
#
#Extracción de lo introducido por la linea de comandos
#
#Fichero de configuración del UA
CONFIG = sys.argv[1]
#
#Inicio del manejador
#
#Manejo del fichero de configuración
parser = make_parser()
proxy_handler = Proxy_Constructor()
parser.setContentHandler(proxy_handler)
parser.parse(open(CONFIG))
info = proxy_handler.get_tags()

#Extrae la informacion del fichero de configuración
server_name = info[0][1]['name']
server_ip = info[0][1]['ip']
server_port = info[0][1]['port']
registered_fich = info[1][1]['path']
passwd_fich = open(info[1][1]['passwdpath'],'r')
log_fich = info[2][1]['path']


passwords = passwd_fich.readlines()#Extrae la informacion del archivo de contraseñas
nonce = random.randint(0,99999999999999999)#Genera el nonce como num aleatorio

#Usuarios registrados
class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """
    SIP REGISTER server class
    """
    users_dicc = {}

    #Abro el fichero de registro de clientes en modo escritura
    def register2json(self):
        json.dump(self.users_dicc,open(registered_fich,'w'))

    #Compruebo si existe el fichero y lo leo
    def json2registered(self):
        try:
            with open(registered_fich) as registered_file:
                self.users_dicc = json.load(registered_file)
        except:
            self.register2json()

    #Borra usuarios del registro de usuarios registrados
    def delete(self):
        aux_list = []
        for user in self.users_dicc:
            expires = int(self.users_dicc[user][-1])
            if expires < time.time():
                aux_list.append(user)
        for client in aux_list:
            del self.users_dicc[client]
            print('Deleting: ',client)


    #Registro de nuevos Usuarios
    def register(self,client_expire,register_user,client_address,client_port):
        self.json2registered()
        self.time = float(time.time())
        self.time_expire = float(time.time()) + float(client_expire)
        self.client_info=[client_address,client_port,self.time,self.time_expire]
        self.users_dicc[register_user] = self.client_info
        if int(client_expire) == 0:
                del self.users_dicc[register_user]
        self.wfile.write(b"SIP/2.0 200 0K\r\n")
        self.delete()
        self.register2json()



    def handle(self):
        #Registra ip y puerto del cliente (client_address)
        self.json2registered()
        client_ip = self.client_address[0]
        client_port = self.client_address[1]

        while 1:
            line = self.rfile.read()
            if not line:
                break
            request = line.decode('utf-8')
            print("\r\nReceiving-- " + request)
            ###HACER LOG
            METHOD = request.split(' ')[0]
            if METHOD == 'REGISTER':
                if 'Authorization:' in request:
                    response = request.split('=')[1].split('\r')[0]
                    user = request.split(':')[1]
                    user_port = request.split('.com:')[1].split(' S')[0]
                    user_exp = request.split('s:')[1].split('Au')[0]
                    # Genero el response q tengo q comprobar con el response recibido del UA
                    for line in passwords:
                        if line.split()[0] == user:
                            aux = hashlib.md5()
                            u_pass = line.split()[-1]
                            aux.update(bytes(u_pass,'utf-8') + bytes(str(nonce),'utf-8'))
                            my_response = aux.hexdigest()
                            if my_response == response:
                                self.register(user_exp,user,client_ip,user_port)
                                reply = "SIP/2.0 200 OK\r\n"
                            else:
                                reply = "SIP/2.0 404 User Not Found\r\n"
                            ####PASAR PRINT AL LOG
                            print("Sending-- " + reply)
                            self.wfile.write(bytes(reply, "utf-8"))

                else:
                    reply = "SIP/2.0 401 Unauthorized\r\n"
                    reply += "WWW Authenticate: nonce=" + str(nonce)
                    user = request.split(':')[1]
                    ####PASAR PRINT AL LOG
                    print("Sending-- " + reply)
                    ####PASAR PRINT AL LOG
                    self.wfile.write(bytes(reply, "utf-8"))

            elif METHOD == 'INVITE':
                self.json2registered()
                user_to = request.split(':')[1].split(' ')[0]
                print("user_to--" + user_to + "--")
                if user_to in self.users_dicc.keys():
                    print("Usuario encontrado")
                else:
                    print(user_to + " is offline ")

            else:
                reply = "SIP/2.0 405 Method Not Allowed\r\n"
                print("Sending-- " + reply)
                self.wfile.write(bytes(reply, "utf-8"))

if __name__ == "__main__":
    serv = socketserver.UDPServer(('', int(server_port)), SIPRegisterHandler)
    print("\r\nServer " + server_name + " listening at port: " + server_port + "...")
    #Se crea esta excepción para q al salir del servidor con crtl+c salga el mensaje de Finalizado
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("----SERVER FINISHED----")

#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import socketserver
import sys
import os
import xml.etree.ElementTree as ET


class SIPHandler(socketserver.DatagramRequestHandler):
    """
    SIP server class
    """
    IP = sys.argv[1]
    PORT = sys.argv[2]

    def handle(self):
        # Leyendo línea a línea lo que nos envía el cliente
        line = self.rfile.read()
        Request = line.decode('utf-8')
        print("El proxy nos manda: " + Request)

        if Request.startswith('INVITE'):
            self.wfile.write(b"SIP/2.0 100 Trying\r\n")
            self.wfile.write(b"SIP/2.0 180 Ring\r\n")
            self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")

        elif Request.startswith('ACK'):
            AUDIO = sys.argv[3]
            aEjecutar = "./mp32rtp -i 127.0.0.1 -p 23032 < " + AUDIO
            print("Vamos a ejecutar: ", aEjecutar)
            os.system(aEjecutar)

        elif Request.startswith('BYE'):
            self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
            print("Despidiendo al cliente...")

        else:
            self.wfile.write(b"SIP/2.0 405 Method Not Allowed\r\n\r\n")

if __name__ == "__main__":
    # Creamos servidor
    try:
        config = sys.argv[1]
        info = ET.parse(str(config))
        root = info.getroot()
        server_port = root.find("uaserver").attrib["port"]
        ip = root.find("uaserver").attrib["ip"]
        rtp_port = root.find("rtpaudio").attrib["port"]

        if len(sys.argv) != 2:
            sys.exit("Usage: python3 uaserver.py Config")


        serv = socketserver.UDPServer(('', PORT), SIPHandler)
        print("Listening...")
        serv.serve_forever()

    except:
        sys.exit("Usage: python3 uaserver.py Config")

import socket
import argparse
import threading
import re
import pickle
from colorama import Fore, Style
from argparse import RawTextHelpFormatter

styleKeeper = Fore.CYAN + Style.BRIGHT

class Keeper():
    def __init__(self, ip, port):        
        '''
        Construtor da classe do servidor centralizado.

        :param ip: 
        '''
        
        self.ip = ip
        self.port = port
        self.listClients = []

    @property
    def ip(self):
        return self._ip
    
    @property
    def port(self):
        return self._port

    @ip.setter
    def ip(self, ip):
        self._ip = ip

    @port.setter
    def port(self, port):
        self._port = port

    def notify_ip(self, address):
        global styleKeeper

        for ip in self.listClients:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(ip)

            sock.send(b'NewClient')
            msg = sock.recv(1024)

            if re.search('Ok', msg.decode('utf-8')):
                sock.send(pickle.dumps(address))
                msg = sock.recv(1024)

                if re.search('Ok', msg.decode('utf-8')):
                    print(styleKeeper + 'New client sent to {}'.format(ip[0]))
            
            sock.close()

    def connected(self, conn, addr):
        while True:
            try:
                msg = conn.recv(1024)
                if re.search('EnterBlockChain', msg.decode('utf-8')):
                    self.listClients.append((addr[0], addr[1]))
                    conn.send(addr[1])
                    self.notify_ip((addr[0], addr[1]))
                    msg = conn.recv(1024)

                    if re.search('Ok', msg.decode('utf-8')):
                        conn.send(pickle.dumps(self.listClients))

    def start_server(self):
        global styleKeeper

        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                server.bind((self.ip, self.port))
                server.listen(10)
            except:
                print(styleKeeper + "Error on start server - Bind port!")
        
            print(styleKeeper + "Server Running on port {}".format(self.port))

            try:
                while True:
                    conn, addr = server.accept()
                    print(styleKeeper + "New connection from {} with port {}".format(addr[0], addr[1]))
                    threading.Thread(target=self.connected, args=(conn,addr))
            except:
                server.close()
                print(styleKeeper + "Ending the execution of server - No messages!")

        except (KeyboardInterrupt, SystemExit):
            print(styleKeeper + "Finishing the execution of server...")





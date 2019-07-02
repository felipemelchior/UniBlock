import socket
import argparse
import threading
import re
import pickle
import time
from colorama import Fore, Style
from argparse import RawTextHelpFormatter

styleKeeper = Fore.CYAN + Style.BRIGHT
styleHeartbeat = Fore.RED + Style.BRIGHT

class Keeper():
    def __init__(self, ip, port):        
        '''
        Construtor da classe do servidor centralizado.

        :param ip: 
        '''
        
        self.ip = ip
        self.port = port
        self.listClients = []
        self.threads = []

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

    def heartbeat(self):
        global styleHeartbeat

        while True:
            time.sleep(20)

            print(styleHeartbeat + 'Initializing Heartbeat on clients')

            for ip in self.listClients:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect(ip)

                    sock.send(b'UAlive?')
                    msg = sock.recv(1024)
                    if msg:
                        print(styleHeartbeat + '{} still alive :)'.format(ip[0]))
                    else:
                        print(styleHeartbeat + '{} is dead :X'.format(ip[0]))
                        self.listClients.remove(ip)
                        self.notify_ip(ip, 'DEAD')
                except (ConnectionRefusedError, ConnectionResetError):
                    print(styleHeartbeat + '{} is dead :X'.format(ip[0]))
                    self.listClients.remove(ip)
                    self.notify_ip(ip, 'DEAD')

    def notify_ip(self, address, case):
        global styleKeeper

        for ip in self.listClients:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(ip)

            if re.search('DEAD', case):
                sock.send(b'DeadClient')
                msg = sock.recv(1024)

                if re.search('Ok', msg.decode('utf-8')):
                    sock.send(pickle.dumps(ip))
                    msg = sock.recv(1024)
                    if re.search('Ok', msg.decode('utf-8')):
                        print(styleKeeper + 'Client {} notified for dead client'.format(ip[0]))
            
            if re.search('NEW', case):
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
                    conn.send(pickle.dumps(addr))
                    self.notify_ip((addr[0], addr[1]), 'NEW')
                if re.search('GiveMeUsers', msg.decode('utf-8')):
                    conn.send(pickle.dumps(self.listClients))
            except:
                pass

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
                    thread = threading.Thread(target=self.connected, args=(conn,addr))
                    thread.start()
                    self.threads.append(thread)
            except:
                server.close()
                print(styleKeeper + "Ending the execution of server - No messages!")

        except (KeyboardInterrupt, SystemExit):
            print(styleKeeper + "Finishing the execution of server...")




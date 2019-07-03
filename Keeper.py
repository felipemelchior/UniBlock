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
        self.clients = ([], [])

    def show_clients(self):
        global styleKeeper
        print(styleKeeper + '\nUsers:')
        print(styleKeeper + '\tMiners:')
        for miner in self.clients[0]:
            print(styleKeeper + '\t\t{}'.format(miner))
        print(styleKeeper + '\tTraders:')
        for trader in self.clients[1]:
            print(styleKeeper + '\t\t{}'.format(trader))

    @property
    def listClients(self):
        return self.clients[0] + self.clients[1]

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
            flag_dead = False
            deads = []
            time.sleep(20)

            print(styleHeartbeat + '\nInitializing Heartbeat on clients:')

            for ip in self.listClients:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    sock.connect(ip)

                    sock.send(b'UAlive?')
                    msg = sock.recv(1024)
                    if msg:
                        print(styleHeartbeat + '\t{} still alive :)'.format(ip))
                    else:
                        print(styleHeartbeat + '\t{} is dead :X'.format(ip))
                        deads.append(ip)
                        self.remove_client(ip)
                        flag_dead = True
                        # print(self.clients)
                        # self.notify_ip(ip, 'DEAD')
                except (ConnectionRefusedError, ConnectionResetError):
                    print(styleHeartbeat + '\t{} is dead :X'.format(ip))
                    deads.append(ip)
                    self.remove_client(ip)
                    flag_dead = True
                    # print(self.clients)
                    # self.notify_ip(ip, 'DEAD')
            for dead in deads:
                self.notify_ip(dead, 'DEAD')
            if flag_dead:
                self.show_clients()

    def remove_client(self, client):
        if client in self.clients[0]:
            self.clients[0].remove(client)
        if client in self.clients[1]:
            self.clients[1].remove(client)

    def notify_ip(self, address, case):
        global styleKeeper

        for ip in self.listClients:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(ip)
            
            if re.search('DEAD', case):
                sock.send(b'DEAD')
                msg = sock.recv(1024)

                if re.search('Ok', msg.decode('utf-8')):
                    sock.send(pickle.dumps(address))
                    msg = sock.recv(1024)
                    if re.search('Ok', msg.decode('utf-8')):
                        print(styleKeeper + '\tClient {} notified for dead client'.format(ip))
            
            if re.search('NEWMiner', case):
                sock.send(b'NEWMiner')
                msg = sock.recv(1024)

                if re.search('Ok', msg.decode('utf-8')):
                    sock.send(pickle.dumps(address))
                    msg = sock.recv(1024)

                    if re.search('Ok', msg.decode('utf-8')):
                        print(styleKeeper + '\t\tsent to {}'.format(ip))

            if re.search('NEWTrader', case):
                sock.send(b'NEWTrader')
                msg = sock.recv(1024)

                if re.search('Ok', msg.decode('utf-8')):
                    sock.send(pickle.dumps(address))
                    msg = sock.recv(1024)

                    if re.search('Ok', msg.decode('utf-8')):
                        print(styleKeeper + '\t\tsent to {}'.format(ip))
            
            sock.close()

    def connected(self, conn, addr):
        global styleKeeper
        port = addr[1] + 1
        ip = addr[0]
        while True:
            try:
                msg = conn.recv(1024)
                if re.search('NEWMiner', msg.decode('utf-8')):
                    print(styleKeeper + '\tNew Miner {}'.format((ip, port)))
                    self.notify_ip((ip, port), 'NEWMiner')
                    self.clients[0].append((ip, port))
                    conn.send(pickle.dumps((ip, port)))
                elif re.search('NEWTrader', msg.decode('utf-8')):
                    print(styleKeeper + '\tNew Trader {}'.format((ip, port)))
                    self.notify_ip((ip, port), 'NEWTrader')
                    self.clients[1].append((ip, port))
                    conn.send(pickle.dumps((ip, port)))
                if re.search('GiveMeUsers', msg.decode('utf-8')):
                    conn.send(pickle.dumps(self.clients))
                    break
            except:
                pass
            self.show_clients()

    def start_server(self):
        global styleKeeper
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                server.bind((self.ip, self.port))
                server.listen(10)
            except:
                print(styleKeeper + "\nError on start server - Bind port!\n")
        
            print(styleKeeper + "\nServer Running on port {}\n".format(self.port))

            thread_heartbeat = threading.Thread(target=self.heartbeat, args=())
            thread_heartbeat.start()

            try:
                while True:
                    conn, addr = server.accept()
                    print(styleKeeper + "\nNew connection from {} with port {}:".format(addr[0], addr[1]))
                    thread = threading.Thread(target=self.connected, args=(conn,addr))
                    thread.start()
                    # self.threads.append(thread)
            except:
                server.close()
                print(styleKeeper + "\nEnding the execution of server - No messages!\n")

        except (KeyboardInterrupt, SystemExit):
            print(styleKeeper + "\nFinishing the execution of server...\n")




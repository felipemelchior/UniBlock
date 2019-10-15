import socket
import threading
import re
import pickle
import time
from BlockChain import MinerChain, TraderChain
from random import randint
from colorama import Fore, Style
import traceback

# Variaveis globais, apenas para a concatenação da string e colorir a mesma (Biblioteca Colorama)
styleCommunication = Fore.MAGENTA + Style.BRIGHT
styleClient = Fore.GREEN + Style.BRIGHT
styleChain = Fore.YELLOW + Style.BRIGHT

class Connection:
    '''
    Classe base para conexoes
    '''
    def __init__(self, my_address, clients):
        self.my_address = my_address
        self.clients = clients
        self.mine = True
        self.connMiners = list()
        self.connTraders = list()

    def show_clients(self):
        global styleClient
        print(styleClient + '\nUsers:')
        print(styleClient + '\tMiners:')
        for miner in self.listMiners:
            print(styleClient + '\t\t{}'.format(miner))
        print(styleClient + '\tTraders:')
        for trader in self.listTraders:
            print(styleClient + '\t\t{}'.format(trader))

    @property
    def listClients(self):
        return self.clients[0] + self.clients[1]

    @property
    def listTraders(self):
        return self.clients[1]
    
    @property
    def listMiners(self):
        return self.clients[0]

    @property
    def my_port(self):
        return int(self.my_address[1])

    @property
    def my_ip(self):
        return str(self.my_address[0])

    @property
    def my_address(self):
        '''
        Metodo getter do my_address.

        :returns: str -- ip.
        '''
        return self._my_ip_port
    
    @my_address.setter
    def my_address(self, ip_port):
        '''
        :param ip_port: tupla ip e port
        '''
        self._my_ip_port=ip_port

    def getBlockChain(self):
        clients = self.listClients
        if self.my_address in clients:
            clients.remove(self.my_address)
        while True:
            client = self.clients[randint(0, len(self.clients)-1)]
            try:
                socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socketClient.connect(client[0])
                socketClient.send(b'GetBlock')
                msg = socketClient.recv(1024)
                if re.search('Ok', msg.decode('utf-8')):
                    socketClient.send(bytes(str(len(self.blockChain.chain)+1),('utf-8')))
                    block = socketClient.recv(4096)
                    block = pickle.loads(block)
                    if block['index'] == '':
                        break

                    newChain=self.blockChain.chain.copy()
                    newChain.append(block)
                    if self.blockChain.last_block['previous_hash'] != block['previous_hash']:
                        self.blockChain.chain = newChain
            except:
                continue
                
    def remove_client(self, client):
        if client in self.clients[0]:
            self.clients[0].remove(client)
        if client in self.clients[1]:
            self.clients[1].remove(client)

    
    def removeConnection(self, client):
        i = 0
        isMiner = False

        for connMiner in self.connMiners:
            if(connMiner[1] == client):
                isMiner = True
                connMiner[0].close()
                break
            i = i + 1
        
        if(isMiner):
            self.connMiners.pop(i)
        else:
            i = 0
            for connTrader in self.connTraders:
                if(connTrader[1] == client):
                    connTrader[0].close()
                    break
                i = i + 1

            self.connMiners.pop(i)

    def printClients(self):
        '''
        Imprime na tela a lista de clientes mineradores e a lista de clientes negociadores.
        '''    

        global styleClient

        print(styleClient + 'Miners => {}'.format(self.listMiners))
        print(styleClient + 'Traders => {}'.format(self.listTraders))

    def listenConnection(self):
        '''
        Coloca o servidor para rodar de fato.
        Após, fica escutando a porta e quando chegar alguma conexão, cria um thread para o cliente.
        Trata envia para a função que irá tratar a requisição.

        :param Ip: Endereço Ip que o servidor irá rodar
        :param Port: Porta em que o servidor irá rodar
        '''

        global styleCommunication
        try:
            try:
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server.bind(self._my_ip_port) # FIXME
                server.listen(10)
                print(styleCommunication + "Server running on port {}".format(self.my_port))
            except:
                traceback.print_exception()
                print("Error on start server")

            try:
                while True: #Loop que mantem conexão.
                    conn, addr = server.accept()
                    # print(styleCommunication + "New Connection from {} with port {}".format(addr[0],addr[1]))
                    
                    aux = threading.Thread(target=self.filterCommunication, args=(conn,addr))			
                    aux.start()
            except:
                print(styleCommunication + "Ending the server execution")

            server.close()

        except (KeyboardInterrupt, SystemExit):
            print(styleCommunication + "Finishing execution of Server...")
            exit()
import socket
import threading
import re
import json
import pickle
from BlockChain import MinerChain, TraderChain
from colorama import Fore, Style


# Variaveis globais, apenas para a concatenação da string e colorir a mesma (Biblioteca Colorama)
styleCommunication = Fore.MAGENTA + Style.BRIGHT
styleClient = Fore.GREEN + Style.BRIGHT

class Connection:
    def __init__(self, myIp, listClients):
        self.myIp=myIp
        self.listClients = listClients
        self.listMiners = []
        self.listTraders = []
        self.miner = False

    @property
    def myIp(self):
        return self._myIp
    
    @myIp.setter
    def myIp(self, value):
        self._myIp=value

    def printClients(self):
        global styleClient

        print(styleClient + 'Miners => {}'.format(self.listMiners))
        print(styleClient + 'Traders => {}'.format(self.listTraders))

    def getMinersAndTraders(self):
        '''
        Adiciona nas respectivas listas os ips que são mineradores e ips que são traders 
        '''
        
        global styleCommunication
        active = []

        while (len(active) != len(self.listClients)):
            for ip in self.listClients:
                if ip == self.myIp:
                    if ip not in active:
                        active.append(ip)
                    continue

                if ip not in active:
                    socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        socketClient.connect((ip, 5055))
                    except:
                        print(styleCommunication + 'Conexão recusada para o cliente {}! Provável que este ainda esteja iniciando'.format(ip))
                        continue

                    active.append(ip)

                    socketClient.send(b'TypeOfClient')
                    
                    msg = socketClient.recv(1024)
                    
                    if re.search('Miner', msg.decode("utf-8")):
                        self.listMiners.append(ip)
                    elif re.search('Trader', msg.decode("utf-8")):
                        self.listTraders.append(ip)

                    socketClient.close()
        
        self.printClients()

    def communicationConnection(self, conn, addr):
        '''
        Trata as conexões dos clients... Recebe uma mensagem, filtra e envia uma resposta
        :param conn: Socket de conexão com o cliente
        :param addr: Endereço da conexão deste cliente
        '''

        while True:
            msg = conn.recv(1024)

            if re.search('TypeOfClient', msg.decode("utf-8")):
                if self.miner:
                    conn.send(b'Miner')
                else:
                    conn.send(b'Trader')

            if not msg: break

        conn.close()



    def listenConnection(self, port=5055):
        '''
        Coloca o servidor para rodar de fato
        Após, fica escutando a porta e quando chegar alguma conexão, cria um thread para o cliente
        e trata envia para a função que irá tratar a requisição
        :param Ip: Endereço Ip que o servidor irá rodar
        :param Port: Porta em que o servidor irá rodar
        '''
        global styleCommunication

        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                server.bind((self._myIp, int(port)))
                server.listen(10)
            except:
                print("Error on start server")
    
            print(styleCommunication + "Server running on port {}".format(port))

            threads = []

            try:
                while True:
                    conn, addr = server.accept()
                    print(styleCommunication + "New Connection from {} with port {}".format(addr[0],addr[1]))
                    
                    aux = threading.Thread(target=self.communicationConnection, args=(conn,addr))			
                    aux.start()
                    threads.append(aux)
            except:
                print(styleCommunication + "Ending the server execution")

            server.close()

        except (KeyboardInterrupt, SystemExit):
            print(styleCommunication + "Finishing execution of Server...")
            exit()

class Miner(Connection):
    def __init__(self, myIp, listClients):
        super().__init__(myIp, listClients)
        self.miner = True
        self.flagRich=False
        self.listMiners.append(self.myIp)
        self.blockChain = MinerChain()

    def communicationConnection(self, conn, addr):
        '''
        Trata as conexões dos clients... Recebe uma mensagem, filtra e envia uma resposta
        :param conn: Socket de conexão com o cliente
        :param addr: Endereço da conexão deste cliente
        '''

        while True:
            msg = conn.recv(1024)

            if re.search('TypeOfClient', msg.decode("utf-8")):
                if self.miner:
                    conn.send(b'Miner')
                else:
                    conn.send(b'Trader')
            
            if re.search('Rich', msg.decode("utf-8")):
                if self.flagRich:
                    conn.send(b'True')
                else: 
                    conn.send(b'False')

            if re.search('NewTransaction', msg.decode("utf-8")):
                conn.send(b'Ok')
                transaction = conn.recv(4096)
                self.blockChain.new_transaction(pickle.loads(transaction))
                conn.send(b'Ok')
            
            if re.search('NewBlock', msg.decode("utf-8")):
                conn.send(b'Ok')
                block=conn.recv(4096)
                newChain=self.blockChain.chain.copy()
                newChain.last_block=block
                if self.blockChain.valid_chain(newChain):
                    self.blockChain.chain=newChain
                    conn.send(b'Ok')
                else:
                    conn.send(b'NOk')


            if not msg: break

        conn.close()

class Trader(Connection):
    def __init__(self, myIp, listClients):
        super().__init__(myIp, listClients)
        self.listTraders.append(self.myIp)
        self.blockChain = TraderChain()

    def runMethods(self):
        while True:
            self.userInput()

    def userInput(self):
        transaction = self.blockChain.new_transaction(self.myIp)
        transaction['minerIp'] = self.discoverMiner()
        self.sendToMiner(transaction)

    def discoverMiner(self):
        global styleCommunication
        ipMiner = ''
        miner = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        for ip in self.listMiners:
            try: 
                miner.connect((ip, 5055))
            except:
                print(styleCommunication + '{} not connected in Blockchain!'.format(ip))
                continue

            miner.send(b'Rich')
            msg = miner.recv(1024)

            if re.search('True', msg.decode("utf-8")):
                ipMiner = ip
                print(styleCommunication + 'Miner Found! IP = {}'.format(ip))
                break

            if not msg: 
                miner.close()
                break
        
        return ipMiner

    def sendToMiner(self, transaction):
        connectionMiner = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connectionMiner.connect((transaction['ipMiner'], 5055))

        connectionMiner.send(b'NewTransaction')
        msg = connectionMiner.recv(1024)

        if re.search('Ok', msg.decode("utf-8")):
            print(styleCommunication + 'Sending the transaction to the Miner...')

            connectionMiner.send(pickle.dumps(transaction))
            msg = connectionMiner.recv(1024)

            if re.search('Ok', msg.decode("utf-8")):
                print(styleCommunication + 'Transaction Sent to the Miner!')
        connectionMiner.close()
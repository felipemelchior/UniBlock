import os
import socket
import threading
import re
import pickle
import time
from BlockChain import TraderChain
from colorama import Fore, Style
from communication import Connection

# Variaveis globais, apenas para a concatenação da string e colorir a mesma (Biblioteca Colorama)
styleCommunication = Fore.MAGENTA + Style.BRIGHT
styleClient = Fore.GREEN + Style.BRIGHT
styleChain = Fore.YELLOW + Style.BRIGHT

class Trader(Connection):
    '''
    Classe do usuario comum.
    '''
    def __init__(self, my_address, clients):
        '''
        Construtor da classe do usuario comum.

        :param my_address: ip.
        :param listClients: lista de clientes.
        '''
        super().__init__(my_address, clients)
        self.blockChain = TraderChain('blocks/{}'.format(self.my_port))
        # self.blockChain = TraderChain(str(self.my_port))

    def runMethods(self):
        '''
        Metodo em loop que fica pedindo ao usuário o texto que deve ser adicionado na chain.
        Esta função acaba criando uma cadeia de chamadas de funções.
        '''

        if len(self.listClients) != 1:
            self.getBlockChain()
        
        while True:
            time.sleep(1) 
            self.userInput() #Inicia as transações.

    def userInput(self):
        '''
        Inicia a transação.
        Descobre o ip do minerador que está com a flag rich.
        Envia esta transação para o minerador com a flag rich.
        '''

        case = input(styleClient + '\nEnter your command (type help to list commands) => ')

        if re.search('exit', case):
            del self.blockChain._chain
            os._exit(0)
        elif re.search('help', case):
            print(styleClient + 'help:')
            print(styleClient + '\tlu - list users')
            print(styleClient + '\tst - send transaction')
            print(styleClient + '\tsc - show chain')
            print(styleClient + '\texit - quit trader')
        elif re.search('lu', case):
            self.show_clients()
        
        if len(self.listMiners) != 0:
            if re.search('st', case):
                transaction = self.blockChain.new_transaction(self.my_address)
                self.sendToMiner(transaction)
            elif re.search('sc', case):
                print(styleChain + '\nActual chain {}\n'.format(self.blockChain.chain))
        else:
            print(styleClient + 'Attention! No miners available! Please, try again later.')

    def sendToMiner(self, transaction):
        '''
        Envia a transação para o minerador.
        Utiliza pickle para serializar o dado e enviar.

        :param transaction: Transaction.
        '''

        print(styleCommunication + '\tSending the transaction to {} Miner...'.format(len(self.listMiners)))

        for connMiner in self.connMiners:
            connection = connMiner[0]

            try:
                connection.send(b'NewTransaction') #Faz requisição para nova transação.
            except:
                miner = connMiner[1]
                connection.connect(miner)
                connection.send(b'NewTransaction') #Faz requisição para nova transação.

            msg = connection.recv(1024)

            if re.search('Ok', msg.decode("utf-8")):

                connection.send(pickle.dumps(transaction)) #Empacota transação.
                msg = connection.recv(1024)

                if re.search('Ok', msg.decode("utf-8")): #Testa se foi possível enviar a transação.
                    pass

    def createConnection(self, client, tipo):
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        listConnection = list()
        listConnection.append(connection)
        listConnection.append(client)

        if(tipo == "Miner"):
            self.connMiners.append(listConnection)
        else:
            self.connTraders.append(listConnection)
    

    def filterCommunication(self, conn, addr):
        '''
        Trata as conexões dos clients... Recebe uma mensagem, filtra e envia uma resposta.

        :param conn: Socket de conexão com o cliente.
        :param addr: Endereço da conexão deste cliente.
        '''
        global styleChain

        while True:
            try:
                msg = conn.recv(1024)

                if re.search('DEAD', msg.decode("utf-8")):
                    # Dead's actions
                    conn.send(b'Ok')
                    msg = conn.recv(4096)
                    client = pickle.loads(msg)
                    self.remove_client(client)
                    self.removeConnection(client)
                    conn.send(b'Ok')

                elif re.search('NEWMiner', msg.decode("utf-8")):
                    # New's actions
                    conn.send(b'Ok')
                    msg = conn.recv(4096)
                    client = pickle.loads(msg)
                    self.clients[0].append(client)
                    self.createConnection(client,"Miner")
                    conn.send(b'Ok')

                elif re.search('NEWTrader', msg.decode("utf-8")):
                    # New's actions
                    conn.send(b'Ok')
                    msg = conn.recv(4096)
                    client = pickle.loads(msg)
                    self.clients[1].append(client)
                    self.createConnection(client,"Trader")
                    conn.send(b'Ok')

                elif re.search('UAlive?', msg.decode("utf-8")):
                    # Aliver's actions
                    conn.send(b'Ok')
                  
                elif re.search('NewBlock', msg.decode("utf-8")):
                    conn.send(b'Ok')
                    block=conn.recv(4096)
                    self.con_block = block
                    block=pickle.loads(block) #Desempacota o bloco
                    newChain=self.blockChain.chain.copy()
                    newChain.append(block)
                    if self.blockChain.last_block['previous_hash'] != block['previous_hash']:
                        # self.blockChain.chain = newChain
                        self.blockChain.last_block = block
                        print(styleChain + '\n\tNew block added to BlockChain!')
                        print(styleClient + 'Enter your command (type help to list commands) =>' , end='')
                    self.mine = True

                elif re.search('valid', msg.decode('utf-8')):
                    conn.send(b'Ok')
                    block = conn.recv(4096)
                    block = pickle.loads(block)
                    newChain=self.blockChain.chain.copy()
                    newChain.append(block)
                    if self.blockChain.valid_chain(newChain) and self.mine:#Testa se a nova cadeia é vaĺida.
                        self.mine = False
                        conn.send(b'Ok')
                    else:
                        conn.send(b'Nok')
        
                elif re.search('GetBlock', msg.decode('utf-8')):
                    conn.send(b'Ok')
                    index = conn.recv(1024)
                    block = self.blockChain._chain.block(int(index))
                    conn.send(pickle.dumps(block))

            except Exception as e: pass



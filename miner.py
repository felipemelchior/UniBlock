import socket
import os
import threading
import re
import pickle
import time
from BlockChain import TraderChain
from colorama import Fore, Style
from communication import *

# Variaveis globais, apenas para a concatenação da string e colorir a mesma (Biblioteca Colorama)
styleCommunication = Fore.MAGENTA + Style.BRIGHT
styleClient = Fore.GREEN + Style.BRIGHT
styleChain = Fore.YELLOW + Style.BRIGHT

class Miner(Connection):
    '''
    Classe do minerador.
    '''
    def __init__(self, my_address, clients):
        '''
        Construtor da classe do minerador.

        :param my_address: ip.
        :param listClients: lista de clientes.
        :param rich: flag do minerador que utiliza a carteira.
        '''
        super().__init__(my_address, clients)
        self.blockChain = MinerChain('blocks/{}'.format(self.my_port))
        # self.blockChain = MinerChain(str(self.my_port))


    def runMethods(self):
        '''
        Metodo em loop que fica pedindo ao usuário o texto que deve ser adicionado na chain.
        Esta função acaba criando uma cadeia de chamadas de funções.
        '''

        if len(self.listClients) != 1:
            self.getBlockChain()

        while True:
            time.sleep(1) #Sleep para sincronizar as threads.
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
            print(styleClient + '\tsc - show chain')
            print(styleClient + '\tsw - show wallet')
            print(styleClient + '\texit - quit miner')

        elif re.search('lu', case):
            self.show_clients()
        elif re.search('sw', case):
            print(styleChain + '\nActual wallet {}\n'.format(self.blockChain.transactions))
        elif re.search('sc', case):
            print(styleChain + '\nActual chain {}\n'.format(self.blockChain.chain))
            

    def sendTransactionsToMiners(self):
        '''
        Envia as transacoes para os mineradores.
        '''
        global styleCommunication
        wallet=self.blockChain.transactions.pop(0)
        for miner in self.listMiners: #Percorre lista de mineradores.
            socketMiner = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socketMiner.connect(miner)

            socketMiner.send(b'MineThis') #Envia mensagem para que os mesmos minerem.
            msg = socketMiner.recv(1024)

            if re.search('Ok', msg.decode("utf-8")):
                socketMiner.send(pickle.dumps(wallet)) #Empacota carteira.
                msg = socketMiner.recv(1024)

                if re.search('Ok', msg.decode("utf-8")):
                    pass


    def sendBlock(self, block):
        '''
        Envia o ultimo bloco minerado para todos na rede.

        :param block: ultimo bloco minerado.
        '''
        global styleCommunication
        yes = 0
        no = 0
        dead = 0
        for client in self.listClients: #Percorre a lista de clientes.
            socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                socketClient.connect(client)

                socketClient.send(b'valid') #Envia requisição para adicionar novo bloco.
                msg = socketClient.recv(1024)
                if re.search('Ok', msg.decode("utf-8")):
                    socketClient.send(pickle.dumps(block)) #Empacota bloco.
                    if re.search('Ok', msg.decode("utf-8")): #Caso o bloco seja aceito, o novo minerador se torna o rich.
                        # print(styleCommunication+'Block added to blockChain')
                        yes += 1
                    elif re.search('Nok', msg.decode("utf-8")): #Em caso negativo, o bloco é descartado.
                        # print(styleCommunication+'Block discarted')
                        no += 1
            except:
                dead += 1
        if yes > int((len(self.listClients)-dead)/2):
            for client in self.listClients: #Percorre a lista de clientes.
                socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    socketClient.connect(client)

                    socketClient.send(b'NewBlock') #Envia requisição para adicionar novo bloco.
                    msg = socketClient.recv(1024)
                    if re.search('Ok', msg.decode("utf-8")):
                        socketClient.send(pickle.dumps(block)) #Empacota bloco.
                except:
                    pass

    def filterCommunication(self, conn, addr):
        '''
        Trata as conexões dos clients... Recebe uma mensagem, filtra e envia uma resposta de acordo ou executa ações.

        :param conn: Socket de conexão com o cliente
        :param addr: Endereço da conexão deste cliente
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
                    conn.send(b'Ok')

                elif re.search('NEWMiner', msg.decode("utf-8")):
                    # New's actions
                    conn.send(b'Ok')
                    msg = conn.recv(4096)
                    client = pickle.loads(msg)
                    self.clients[0].append(client)
                    conn.send(b'Ok')
                    
                elif re.search('NEWTrader', msg.decode("utf-8")):
                    # New's actions
                    conn.send(b'Ok')
                    msg = conn.recv(4096)
                    client = pickle.loads(msg)
                    self.clients[1].append(client)
                    conn.send(b'Ok')
                    
                elif re.search('UAlive?', msg.decode("utf-8")):
                    # Aliver's actions
                    conn.send(b'Ok')
                    
                elif re.search('NewTransaction', msg.decode("utf-8")): #Adiciona uma nova transação.
                    conn.send(b'Ok')
                    transaction = conn.recv(4096)
                    self.blockChain.new_transaction(pickle.loads(transaction)) #Envia a transação para o método que adiciona à lista de transações.
                    conn.send(b'Ok')

                    if len(self.blockChain.finish_transactions) != 0: #Testa se há transações finalizadas.
                        self.sendTransactionsToMiners() 

                elif re.search('MineThis', msg.decode("utf-8")): #Executa mineração.
                    conn.send(b'Ok')
                    wallet = conn.recv(4096)
                    conn.send(b'Ok')
                    self.blockChain.finish_transactions = pickle.loads(wallet) #Atribui a carteira às transações finalizadas.
                    # threading.Thread(target=self.blockChain.mine).start()
                    self.blockChain.start_miner=True 
                    self.blockChain.mine() #Inicia mineração.
                    if self.blockChain.block!=None: #Testa se o bloco está vazio.
                        self.sendBlock(self.blockChain.block) #Envia o bloco para os mineradores.

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
                        print(styleClient + 'Enter your command (type help to list commands) =>', end='')
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
                    # if self.blockChain.valid_chain(newChain):#Testa se a nova cadeia é vaĺida.
                    #     conn.send(b'Ok')
                    # else:
                    #     conn.send(b'Nok')


                else: break
            except:
                pass

        conn.close()

    
    def selectTransactions(self, numberTrasactions):
        '''
        Seleciona as transações que irão formar o bloco para ser minerado.

        :param numberTrasactions: número máximo de trasações em bloco para ser minerado
        '''
        wallet = []
        
        for i in range(0, len(self.blockChain.current_transactions)):
            transaction = self.blockChain.current_transactions[i]

            if(i < numberTrasactions):
                wallet.append(transaction)
            else:
                wallet = self.replaceTransaction(wallet,transaction)

        #self.raiseReward()

        return wallet

    def replaceTransaction(self, wallet, selectedTransaction):
        '''
        Substitui uma trasação de recompensa mais alta dentro de uma lista.

        :param numberTrasactions: lista de trasações para se substituir uma transação
        :param selectedTransaction: trasação que irá substituir outra de menor recompensa
        '''
        newWallet = []
        minValue = 100

        for transaction in wallet:
            if(transaction['reward'] < minValue):
                minValue = transaction['reward']


        for transaction in wallet:
            if(transaction['reward'] == minValue and
             transaction['reward'] < selectedTransaction['reward']):
                newWallet.append(selectedTransaction)
            else:
                newWallet.append(transaction)
        
        return newWallet

    
    def raiseReward(self):
        '''
        Aumenta a prioridade das trasações que as recompensas estavam muito baixas para serem
        selecionadas.
        '''
        for transaction in self.blockChain.current_transactions:
            transaction['reward'] = transaction['reward'] + 1

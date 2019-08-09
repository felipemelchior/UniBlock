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
        clients.remove(self.my_address)
        while True:
            client = self.clients[randint(0, len(self.clients)-1)]
            try:
                socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socketClient.connect(client[0])
            except:
                pass

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
              
    def remove_client(self, client):
        if client in self.clients[0]:
            self.clients[0].remove(client)
        if client in self.clients[1]:
            self.clients[1].remove(client)

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
                print ("ip: ", self._my_ip_port)
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
        self.blockChain = MinerChain(str(self.my_port))

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
            exit(0)
        elif re.search('help', case):
            print(styleClient + 'help:')
            print(styleClient + '\tlu - list users')
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

        TypeOfClient => retorna se o cliente é um minerador ou um negociador.
        Rich => retorna se o cliente é um minerador que está armazenando transações na carteira.
        NewTransaction => recebe uma nova transação a ser adicionada na carteira.
        NewBlock => recebe a noticia que a chain foi atualizada, entao o cliente deve validar a sua chain.

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
                    pass

                if re.search('NEWMiner', msg.decode("utf-8")):
                    # New's actions
                    conn.send(b'Ok')
                    msg = conn.recv(4096)
                    client = pickle.loads(msg)
                    self.clients[0].append(client)
                    conn.send(b'Ok')
                    pass

                if re.search('NEWTrader', msg.decode("utf-8")):
                    # New's actions
                    conn.send(b'Ok')
                    msg = conn.recv(4096)
                    client = pickle.loads(msg)
                    self.clients[1].append(client)
                    conn.send(b'Ok')
                    pass


                if re.search('UAlive?', msg.decode("utf-8")):
                    # Aliver's actions
                    conn.send(b'Ok')
                    pass

                if re.search('NewTransaction', msg.decode("utf-8")): #Adiciona uma nova transação.
                    conn.send(b'Ok')
                    transaction = conn.recv(4096)
                    self.blockChain.new_transaction(pickle.loads(transaction)) #Envia a transação para o método que adiciona à lista de transações.
                    conn.send(b'Ok')

                    if len(self.blockChain.finish_transactions) != 0: #Testa se há transações finalizadas.
                        self.sendTransactionsToMiners() 

                if re.search('MineThis', msg.decode("utf-8")): #Executa mineração.
                    conn.send(b'Ok')
                    wallet = conn.recv(4096)
                    conn.send(b'Ok')
                    self.blockChain.finish_transactions = pickle.loads(wallet) #Atribui a carteira às transações finalizadas.
                    # threading.Thread(target=self.blockChain.mine).start()
                    self.blockChain.start_miner=True 
                    self.blockChain.mine() #Inicia mineração.
                    if self.blockChain.block!=None: #Testa se o bloco está vazio.
                        self.sendBlock(self.blockChain.block) #Envia o bloco para os mineradores.

                if re.search('NewBlock', msg.decode("utf-8")):
                    conn.send(b'Ok')
                    block=conn.recv(4096)
                    self.con_block = block
                    block=pickle.loads(block) #Desempacota o bloco
                    newChain=self.blockChain.chain.copy()
                    newChain.append(block)
                    if self.blockChain.last_block['previous_hash'] != block['previous_hash']:
                        self.blockChain.chain = newChain
                        print(styleChain + '\n\tNew block added to BlockChain!')
                        print(styleClient + 'Enter your command (type help to list commands) =>', end='')
                    self.mine = True

                if re.search('valid', msg.decode('utf-8')):
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
                
                if re.search('GetBlock', msg.decode('utf-8')):
                    conn.send(b'Ok')
                    index = conn.recv(1024)
                    block = self.blockChain._chain.block(int(index))
                    conn.send(pickle.dumps(block))
                    # if self.blockChain.valid_chain(newChain):#Testa se a nova cadeia é vaĺida.
                    #     conn.send(b'Ok')
                    # else:
                    #     conn.send(b'Nok')


                if not msg: break
            except:
                pass

        conn.close()

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
        self.blockChain = TraderChain(str(self.my_port))

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
            exit(0)
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

        for miner in self.listMiners:
            connectionMiner = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connectionMiner.connect(miner)

            connectionMiner.send(b'NewTransaction') #Faz requisição para nova transação.
            msg = connectionMiner.recv(1024)

            if re.search('Ok', msg.decode("utf-8")):

                connectionMiner.send(pickle.dumps(transaction)) #Empacota transação.
                msg = connectionMiner.recv(1024)

                if re.search('Ok', msg.decode("utf-8")): #Testa se foi possível enviar a transação.
                    pass
            connectionMiner.close()

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
                    conn.send(b'Ok')
                    pass

                if re.search('NEWMiner', msg.decode("utf-8")):
                    # New's actions
                    conn.send(b'Ok')
                    msg = conn.recv(4096)
                    client = pickle.loads(msg)
                    self.clients[0].append(client)
                    conn.send(b'Ok')
                    pass

                if re.search('NEWTrader', msg.decode("utf-8")):
                    # New's actions
                    conn.send(b'Ok')
                    msg = conn.recv(4096)
                    client = pickle.loads(msg)
                    self.clients[1].append(client)
                    conn.send(b'Ok')
                    pass

                if re.search('UAlive?', msg.decode("utf-8")):
                    # Aliver's actions
                    conn.send(b'Ok')
                    pass

                if re.search('NewBlock', msg.decode("utf-8")):
                    conn.send(b'Ok')
                    block=conn.recv(4096)
                    self.con_block = block
                    block=pickle.loads(block) #Desempacota o bloco
                    newChain=self.blockChain.chain.copy()
                    newChain.append(block)
                    if self.blockChain.last_block['previous_hash'] != block['previous_hash']:
                        self.blockChain.chain = newChain
                        print(styleChain + '\n\tNew block added to BlockChain!')
                        print(styleClient + 'Enter your command (type help to list commands) =>' , end='')
                    self.mine = True

                if re.search('valid', msg.decode('utf-8')):
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
        
                if re.search('GetBlock', msg.decode('utf-8')):
                    conn.send(b'Ok')
                    index = conn.recv(1024)
                    block = self.blockChain._chain.block(int(index))
                    conn.send(pickle.dumps(block))

                if not msg: break
            except:
                pass

        conn.close()

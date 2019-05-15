import socket
import threading
import re
import pickle
import time
from BlockChain import MinerChain, TraderChain
from colorama import Fore, Style

# Variaveis globais, apenas para a concatenação da string e colorir a mesma (Biblioteca Colorama)
styleCommunication = Fore.MAGENTA + Style.BRIGHT
styleClient = Fore.GREEN + Style.BRIGHT
styleChain = Fore.YELLOW + Style.BRIGHT

class Connection:
    '''
    Classe base para conexoes
    '''
    def __init__(self, myIp, listClients):
        self.myIp=myIp
        self.listClients = listClients
        self.listMiners = []
        self.listTraders = []
        self.miner = False

    @property
    def myIp(self):
        '''
        Metodo getter do myIp.

        :returns: str -- ip.
        '''
        return self._myIp
    
    @myIp.setter
    def myIp(self, value):
        '''
        Metodo setter do myIp.

        :param value: valor do ip.
        '''
        self._myIp=value

    def printClients(self):
        '''
        Imprime na tela a lista de clientes mineradores e a lista de clientes negociadores.
        '''    

        global styleClient

        print(styleClient + 'Miners => {}'.format(self.listMiners))
        print(styleClient + 'Traders => {}'.format(self.listTraders))

    def getMinersAndTraders(self):
        '''
        Adiciona nas respectivas listas os ips que são mineradores e ips que são traders.
        '''
        
        global styleCommunication
        active = []
        visited = []

        while (len(active) != len(self.listClients)): #Loop que adiciona os clientes ao seus respectivos tipos.
            for ip in self.listClients:
                if ip == self.myIp:
                    if ip not in active: #Adiciona à lista de clientes ativos
                        active.append(ip)
                    continue

                if ip not in active: #Tenta conexão com cliente.
                    socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        socketClient.connect((ip, 5055))
                    except:
                        if ip not in visited: 
                            visited.append(ip)
                            print(styleCommunication + 'Conection refused by {}! Likely to be still starting'.format(ip))
                        else:
                            pass
                        continue

                    active.append(ip) #Adiciona à lista de ativos.

                    socketClient.send(b'TypeOfClient') #Envia requisição sobre qual é o tipo do cliente.
                    
                    msg = socketClient.recv(1024)
                    
                    if re.search('Miner', msg.decode("utf-8")): #Adiciona à lista de acordo com a mensagem e o tipo.
                        print(styleCommunication + 'Miner discovery => {}'.format(ip))
                        self.listMiners.append(ip)
                    elif re.search('Trader', msg.decode("utf-8")):
                        print(styleCommunication + 'Trader discovery => {}'.format(ip))
                        self.listTraders.append(ip)

                    socketClient.close()
        
        self.printClients()


    def listenConnection(self, port=5055):
        '''
        Coloca o servidor para rodar de fato.
        Após, fica escutando a porta e quando chegar alguma conexão, cria um thread para o cliente.
        Trata envia para a função que irá tratar a requisição.

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
                while True: #Loop que mantem conexão.
                    conn, addr = server.accept()
                    print(styleCommunication + "New Connection from {} with port {}".format(addr[0],addr[1]))
                    
                    aux = threading.Thread(target=self.filterCommunication, args=(conn,addr))			
                    aux.start()
                    threads.append(aux)
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
    def __init__(self, myIp, listClients, rich):
        '''
        Construtor da classe do minerador.

        :param myIp: ip.
        :param listClients: lista de clientes.
        :param rich: flag do minerador que utiliza a carteira.
        '''
        super().__init__(myIp, listClients)
        self.miner = True
        self.flagRich = rich
        self.listMiners.append(self.myIp)
        self.blockChain = MinerChain()


    def sendTransactionsToMiners(self):
        '''
        Envia as transacoes para os mineradores.
        '''
        global styleCommunication
        wallet=self.blockChain.transactions.pop(0)
        if len(self.listMiners)>1: #Testa se há mais de um minerador.
            for ip in range(1, len(self.listMiners)): #Percorre lista de mineradores.
                socketMiner = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socketMiner.connect((self.listMiners[ip], 5055))

                socketMiner.send(b'MineThis') #Envia mensagem para que os mesmos minerem.
                msg = socketMiner.recv(1024)

                if re.search('Ok', msg.decode("utf-8")):
                    socketMiner.send(pickle.dumps(wallet)) #Empacota carteira.
                    msg = socketMiner.recv(1024)

                    if re.search('Ok', msg.decode("utf-8")):
                        print(styleCommunication + 'Miner' + Fore.RED + '{}'.format(self.listMiners[ip]) + styleCommunication + 'receive the wallet with transactions sucessfully!')
        else: #Faz com que o minerador inicie a mineração.
            socketMiner = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socketMiner.connect((self.listMiners[ip], 5055))

            socketMiner.send(b'MineThis') #Envia requisição de mineração.
            msg = socketMiner.recv(1024)

            if re.search('Ok', msg.decode("utf-8")):
                socketMiner.send(pickle.dumps(wallet)) #Empacota carteira.
                msg = socketMiner.recv(1024)

                if re.search('Ok', msg.decode("utf-8")):
                    print(styleCommunication + 'Miner' + Fore.RED + '{}'.format(self.listMiners[ip]) + styleCommunication + 'receive the wallet with transactions sucessfully!')

        # socketMiner = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # socketMiner.connect((self.listMiners[0], 5055))

        # socketMiner.send(b'MineThis')
        # msg = socketMiner.recv(1024)

        # if re.search('Ok', msg.decode("utf-8")):
        #     socketMiner.send(pickle.dumps(wallet))
        #     msg = socketMiner.recv(1024)

        #     if re.search('Ok', msg.decode("utf-8")):
        #         print(styleCommunication + 'Miner' + Fore.RED + '{}'.format(self.listMiners[0]) + styleCommunication + 'receive the wallet with transactions sucessfully!')
        
        


    def sendBlock(self, block):
        '''
        Envia o ultimo bloco minerado para todos na rede.

        :param block: ultimo bloco minerado.
        '''
        global styleCommunication
        for ip in self.listClients: #Percorre a lista de clientes.
            socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socketClient.connect((ip, 5055))

            socketClient.send(b'NewBlock') #Envia requisição para adicionar novo bloco.
            msg = socketClient.recv(1024)
            if re.search('Ok', msg.decode("utf-8")):
                socketClient.send(pickle.dumps(block)) #Empacota bloco.
                if re.search('Ok', msg.decode("utf-8")): #Caso o bloco seja aceito, o novo minerador se torna o rich.
                    print(styleCommunication+'Block added to blockChain')
                    self.flagRich=True
                elif re.search('Nok', msg.decode("utf-8")): #Em caso negativo, o bloco é descartado.
                    print(styleCommunication+'Block discarted')

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

                if re.search('TypeOfClient', msg.decode("utf-8")): #Envia resposta sobre qual é o tipo de cliente.
                    if self.miner:
                        conn.send(b'Miner')
                    else:
                        conn.send(b'Trader')
                
                if re.search('Rich', msg.decode("utf-8")):
                    if self.flagRich:
                        conn.send(b'True')
                    else: 
                        conn.send(b'False')

                if re.search('NewTransaction', msg.decode("utf-8")): #Adiciona uma nova transação.
                    conn.send(b'Ok')
                    transaction = conn.recv(4096)
                    self.blockChain.new_transaction(pickle.loads(transaction)) #Envia a transação para o método que adiciona à lista de transações.
                    conn.send(b'Ok')
                    print(styleCommunication + 'New Transaction added to wallet')

                    if len(self.blockChain.finish_transactions) != 0: #Testa se há transações finalizadas.
                        self.sendTransactionsToMiners() 
                        self.flagRich=False #Após enviar transações para mineradores, deixa de ser rich e outro deve ser eleito.

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
                    block=pickle.loads(block) #Desempacota o bloco
                    print(styleCommunication + 'Attention! New block added to chain!')

                    newChain=self.blockChain.chain.copy()
                    newChain.append(block) #Adiciona o bloco à nova cadeia.
                    if self.blockChain.valid_chain(newChain):#Testa se a nova cadeia é vaĺida.
                        self.blockChain.chain=newChain
                        conn.send(b'Ok')
                    else:
                        conn.send(b'Nok')
                    print(styleChain + 'Actual chain {}'.format(self.blockChain.chain))


                if not msg: break
            except:
                pass

        conn.close()

class Trader(Connection):
    '''
    Classe do usuario comum.
    '''
    def __init__(self, myIp, listClients):
        '''
        Construtor da classe do usuario comum.

        :param myIp: ip.
        :param listClients: lista de clientes.
        '''
        super().__init__(myIp, listClients)
        self.listTraders.append(self.myIp)
        self.blockChain = TraderChain()

    def runMethods(self):
        '''
        Metodo em loop que fica pedindo ao usuário o texto que deve ser adicionado na chain.
        Esta função acaba criando uma cadeia de chamadas de funções.
        '''

        while True:
            time.sleep(1) #Sleep para sincronizar as threads.
            self.userInput() #Inicia as transações.

    def userInput(self):
        '''
        Inicia a transação.
        Descobre o ip do minerador que está com a flag rich.
        Envia esta transação para o minerador com a flag rich.
        '''

        transaction = self.blockChain.new_transaction(self.myIp)
        transaction['minerRichIp'] = self.discoverMiner()
        self.sendToMiner(transaction)

    def discoverMiner(self):
        '''
        Método que descobre qual o minerador que está aceitando transações para adicionar na carteira.
        '''

        global styleCommunication
        ipMiner = ''

        for ip in self.listMiners: #Percorre a lista de mineradores prourando qual possui a flag de rich.
            miner = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            try: 
                miner.connect((ip, 5055))
            except:
                print(styleCommunication + '{} not connected in Blockchain!'.format(ip))
                continue

            miner.send(b'Rich')
            msg = miner.recv(1024)

            if re.search('True', msg.decode("utf-8")): #Se recebeu True, achou o minerador.
                ipMiner = ip
                print(styleCommunication + 'Miner Found! IP = {}'.format(ip))
                # miner.close()
                # break

            # if not msg: 
                # miner.close()
            #     break
            # miner.close()
            # time.sleep(1)
            miner.close()
        
        return ipMiner

    def sendToMiner(self, transaction):
        '''
        Envia a transação para o minerador.
        Utiliza pickle para serializar o dado e enviar.

        :param transaction: Transaction.
        '''

        connectionMiner = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connectionMiner.connect((transaction['minerRichIp'], 5055))

        connectionMiner.send(b'NewTransaction') #Faz requisição para nova transação.
        msg = connectionMiner.recv(1024)

        if re.search('Ok', msg.decode("utf-8")):
            print(styleCommunication + 'Sending the transaction to the Miner...')

            connectionMiner.send(pickle.dumps(transaction)) #Empacota transação.
            msg = connectionMiner.recv(1024)

            if re.search('Ok', msg.decode("utf-8")): #Testa se foi possível enviar a transação.
                print(styleCommunication + 'Transaction Sent to the Miner!')
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

                if re.search('TypeOfClient', msg.decode("utf-8")): #Retorna qual é o tipo de cliente.
                    if self.miner:
                        conn.send(b'Miner')
                    else:
                        conn.send(b'Trader')


                if re.search('NewBlock', msg.decode("utf-8")): #Adiciona um novo bloco.
                    conn.send(b'Ok')
                    block=conn.recv(4096)
                    block=pickle.loads(block) #Desempaacota o bloco.
                    print(styleCommunication + 'Attention! New block added to chain!')

                    newChain=self.blockChain.chain.copy()
                    newChain.append(block)
                    if self.blockChain.valid_chain(newChain):#Testa se a nova cadeia é válida.
                        self.blockChain.chain=newChain
                        conn.send(b'Ok')
                    else:
                        conn.send(b'Nok')

                    print(styleChain + 'Actual chain {}'.format(self.blockChain.chain))

                if not msg: break
            except:
                pass

        conn.close()


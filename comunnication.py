import socket
import threading
import re

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
        print('Miners => {}'.format(self.listMiners))
        print('Traders => {}'.format(self.listTraders))

    def getMinersAndTraders(self):
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
                        print('Conexão recusada para o cliente {}! Provável que este ainda esteja iniciando'.format(ip))
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

        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                server.bind((self._myIp, int(port)))
                server.listen(10)
            except:
                print("Error on start server")
    
            print("Server running on port {}".format(port))

            threads = []

            try:
                while True:
                conn, addr = server.accept()
                print("New Connection from {} with port {}".format(addr[0],addr[1]))
                
                aux = threading.Thread(target=self.communicationConnection, args=(conn,addr))			
                aux.start()
                threads.append(aux)
            except:
                print("Ending the server execution")

            server.close()

        except (KeyboardInterrupt, SystemExit):
            print("Finishing execution of Server...")
            exit()

class Miner(Connection):
    def __init__(self, myIp, listClients):
        super().__init__(myIp, listClients)
        self.miner = True
        self.flag_rich=False
        self.listMiners.append(self.myIp)

class Trader(Connection):
    def __init__(self, myIp, listClients):
        super().__init__(myIp, listClients)
        self.listTraders.append(self.myIp)
import socket
import threading
import re

class Connection:
    def __init__(self, myIp, listClients):
        self.myIp=myIp
        self.listClients = listClients
        self.listMiners = []

    @property
    def myIp(self):
        return self._myIp
    
    @myIp.setter
    def myIp(self, value):
        self._myIp=value

    def getMiners(self, listClients):
        active = []

        while (len(active) != len(self.listClients)):
            for ip in self.listClients:
                if ip == self.myIp:
                    active.append(ip)
                    continue

                socketMiner = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    socketMiner.connect((ip, 5055))
                except:
                    print('Conexão recusada para o cliente {}! Provavel que este ainda esteja iniciando'.format(ip))
                    continue
                active.append(ip)
                
                msg = socketMiner.recv(1024)
                
                if re.search('Miner', msg.decode("utf-8") ):
                    self.listMiners.append(ip)

                socketMiner.close()

    def connected(self, conn, addr):
        pass

    def listenConnection(self, port=5055):
        print(self.listMiners)
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
                print(self._myIp, port)

                server.bind((self._myIp, int(port)))
                server.listen(10)
            except:
                print("Error on start server")
    
            print("Server running on port {0}".format(port))

            threads = []

            try:
                while True:
                    conn, addr = server.accept()
                    print(" New Connection from " + str(addr[0]) + " with port " + str(addr[1]))
                    
                    aux = threading.Thread(target=connected, args=(conn,addr))
                    aux.setDaemon(True)				
                    aux.start()
                    threads.append(aux)
            except:
                print("Ending the server execution")

            server.close()

        except (KeyboardInterrupt, SystemExit):
            print("Finishing execution of Server...")
            exit()

class Minner(Connection):
    def __init__(self, myIp):
        super().__init__(myIp)
        self.flag_rich=False

class Trader(Connection):
    def __init__(self, myIp):
        super().__init__(myIp)
import socket
import threading

class Connection:
    def __init__(self, myIp):
        self.myIp=myIp

    @property
    def myIp(self):
        return self._myIp
    
    @myIp.setter
    def myIp(self, value):
        self._myIp=value

    def connected(self, conn, addr):
        pass

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
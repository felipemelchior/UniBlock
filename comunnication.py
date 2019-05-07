import os, sys, getopt
import socket
import threading
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(threadName)s:%(message)s')

class Connection:
    def __init__(self, myIp):
        self.myIp=myIp
    @property
    def myIp(self):
        return self._myIp
    @myIp.setter
    def myIp(self, value):
        self._myIp=value
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
                server.bind((self._myIp, port))
                server.listen(10)
            except:
                logging.info(" Error on start server")
    
            logging.info(" WebServer running on port {0}".format(port))

            threads = []

            try:
                while True:
                    conn, addr = server.accept()
                    logging.info(" New Connection from " + str(addr[0]) + " with port " + str(addr[1]))
                    
                    aux = threading.Thread(target=connected, args=(conn,addr))
                    aux.setDaemon(True)				
                    aux.start()
                    threads.append(aux)
            except:
                logging.info(" Ending the server execution")

            server.close()

        except (KeyboardInterrupt, SystemExit):
            logging.info(" Finishing execution of WebServer...")
            exit()

class Minner(Connection):
    def __init__(self, myIp):
        super().__init__(myIp)
        self.flag_rich=False

class Trader(Connection):
    def __init__(self, myIp):
        super().__init__(myIp)
import argparse
import threading
import socket
import pickle
from argparse import RawTextHelpFormatter
from Keeper import Keeper
from communication import *
from trader import Trader
from miner import Miner
from colorama import Fore, Back, Style, init
init(autoreset=True) # autoreset de estilos do colorama

def connectKeeper(keeperIp, keeperPort, client_type):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((keeperIp, keeperPort))
    client_type = bytes('NEW{}'.format(client_type), 'utf-8')
    sock.send(client_type)
    myAddress = sock.recv(4096)
    myAddress = pickle.loads(myAddress)
    sock.send(b'GiveMeUsers')
    users = sock.recv(4096)
    users = pickle.loads(users)
    sock.close()
    return myAddress, users
def parseArguments():
    '''
    Função que identifica os argumentos passados.

    :returns: parser -- objetos contendo os argumentos.
    '''

    parser = argparse.ArgumentParser(description='Didactic implementation of a blockchain v2.0', formatter_class=RawTextHelpFormatter)
    parser.add_argument("-v", "--version", action='version', version='Uniblock v2.0 \nRepository Link => https://github.com/homdreen/UniBlock')
    parser.add_argument("--miner", action="store_const",const=True, help="Define user as miner")
    parser.add_argument("--trader", action="store_const", const=True, help="Define user as trader")
    parser.add_argument("--keeper", action="store_const", const=True, help="Define keeper")
    parser.add_argument("-ki","--keeperip", required=True, help="Define keeper ip")
    parser.add_argument("-kp","--keeperport", type=int, required=True, help="Define keeper port")

    return parser.parse_args()

def main():
    '''
    Função principal do programa.
    '''
    this = None
    listUsers = []
    style = Fore.GREEN + Style.BRIGHT
    args = parseArguments()

    if args.keeper == True: #Testa se é o keeper
        print(style + 'User detected as ' + Fore.RED + 'keeper')

        this = Keeper(args.keeperip, args.keeperport)
        this.start_server()
    else: #Se nao é o keeper, é necessário saber quem é
        if args.miner == True:
            myAddress, listUsers = connectKeeper(args.keeperip, args.keeperport, 'Miner')
            print(style + 'User detected as ' + Fore.RED + 'miner')
            this = Miner(myAddress, listUsers)
            serverCommunication = threading.Thread(target=this.listenConnection, args=()) #Inicia comunicação.
            serverCommunication.start()
            inputThread = threading.Thread(target=this.runMethods)
            inputThread.start()


        elif args.trader == True:
            myAddress, listUsers = connectKeeper(args.keeperip, args.keeperport, 'Trader')
            print(style + 'User detected as ' + Fore.RED + 'trader')
            this = Trader(myAddress, listUsers)
            serverCommunication = threading.Thread(target=this.listenConnection, args=()) #Inicia comunicação.
            serverCommunication.start()
            clientThread = threading.Thread(target=this.runMethods) #Chama cadeia de funções que inicia o blockchain.
            clientThread.start()  

if __name__ == '__main__':
    main()

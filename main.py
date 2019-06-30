import argparse
import threading
import socket
import pickle
from argparse import RawTextHelpFormatter
from Keeper import Keeper
from comunnication import Connection, Miner, Trader
from colorama import Fore, Back, Style, init
init(autoreset=True) # autoreset de estilos do colorama

def connectKeeper(keeperIp, keeperPort):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((keeperIp, keeperPort))
    sock.send(b'EnterBlockChain')
    myAddress = sock.recv(4096)
    myAddress = pickle.loads(myAddress)
    sock.send(b'GiveMeUsers')
    users = sock.recv(4096)
    users = pickle.loads(users)

    return myAddress, users
def parseArguments():
    '''
    Função que identifica os argumentos passados.

    :returns: parser -- objetos contendo os argumentos.
    '''

    parser = argparse.ArgumentParser(description='Didactic implementation of a blockchain v1.0', formatter_class=RawTextHelpFormatter)
    parser.add_argument("-u", "--users", default=1, type=int, help="Number of users of blockchain")
    parser.add_argument("-v", "--version", action='version', version='Uniblock v1.0 \nRepository Link => https://github.com/homdreen/UniBlock')
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
        myAddress, listUsers = connectKeeper(args.keeperip, args.keeperport)
        if args.miner == True:
            print(style + 'User detected as ' + Fore.RED + 'miner')
            this = Miner(str(myAddress[1]), listUsers)
            serverCommunication = threading.Thread(target=this.listenConnection, args=()) #Inicia comunicação.
            serverCommunication.start()
            # TODO

        elif args.trader == True:
            print(style + 'User detected as ' + Fore.RED + 'trader')
            this = Trader(str(myAddress[1]), listUsers)
            serverCommunication = threading.Thread(target=this.listenConnection, args=()) #Inicia comunicação.
            serverCommunication.start()
            # clientThread = threading.Thread(target=this.getMinersAndTraders, args=()) #Adiciona os clientes.
            # clientThread.start()
            while clientThread.is_alive():
                pass
            clientThread = threading.Thread(target=this.runMethods) #Chama cadeia de funções que inicia o blockchain.
            clientThread.start()
            # TODO  

    # for i in range(args.users): #Pega inputs de IP's dos usuários e adiciona à lista.
    #     if i == 0:
    #         user = str(input(style + 'Enter ' + Fore.RED + 'your IP ' + style + ' => '))
    #     else:
    #         user = str(input(style + 'Enter the IP for user ' + Fore.RED + str(i) + style + ' => '))
    #     users.append(user)
    #     print(style + 'User ' + Fore.RED + user + style + ' added to users list!')

    # if args.miner: #Testa se é minerador e se o mesmo é o que possui a carteira.
    #     if args.rich:
    #         client=Miner(users[0], listClients=users, rich=True)
    #     else:
    #         client=Miner(users[0], listClients=users, rich=False)

    # else: #Se não entrar no teste anterior, é trader.
    #     client=Trader(users[0], listClients=users)

    # serverCommunication = threading.Thread(target=this.listenConnection, args=()) #Inicia comunicação.
    # serverCommunication.start()


    # clientThread = threading.Thread(target=this.getMinersAndTraders, args=()) #Adiciona os clientes.
    # clientThread.start()

    # if args.miner == None:
    #     while clientThread.is_alive():
    #         pass
    #     clientThread = threading.Thread(target=client.runMethods) #Chama cadeia de funções que inicia o blockchain.
    #     clientThread.start()

if __name__ == '__main__':
    main()
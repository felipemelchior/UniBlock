import argparse
from colorama import Fore, Back, Style
from argparse import RawTextHelpFormatter
from comunnication import Connection

def parseArguments():
    parser = argparse.ArgumentParser(description='Didactic implementation of a blockchain v1.0', formatter_class=RawTextHelpFormatter)
    parser.add_argument("-u", "--users", default=1, type=int, help="Number of users of blockchain")
    parser.add_argument("-v", "--version", action='version', version='Uniblock v1.0 \nRepository Link => https://github.com/homdreen/UniBlock')
    parser.add_argument("--miner", action="store_const", const=True, help="Define user as miner")

    return parser.parse_args()

if __name__ == '__main__':
    users = []
    style = Fore.GREEN + Style.BRIGHT
    args = parseArguments()

    print(style + 'Connecting/Initialyzing with ' + Fore.RED + str(args.users) + style + ' users')

    if args.miner == True: 
        print(style + 'User detected as ' + Fore.RED + 'miner')

    for i in range(args.users):
        if i == 0: 
            user = str(input(style + 'Enter ' + Fore.RED + 'your IP ' + style + ' => '))
        else: 
            user = str(input(style + 'Enter the IP for user ' + Fore.RED + str(i) + style + ' => '))
        users.append(user)
        print(style + 'User ' + Fore.RED + user + style + ' added to users list!')

    print(users)
    connect=Connection(users[0])
    connect.listenConnection(port=9091)

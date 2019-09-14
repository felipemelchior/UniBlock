import json
import os
import shutil

'''
Funções e classes que implementam as ferramentas necessárias para o funcionamento da blockchain.
'''

def read_block(index, path_blocks='.'):
    '''
    Função que lê as informações do bloco de um arquivo

    :param index: index do bloco.
    :param path_blocks: caminho para os blocos.
    :returns: dic -- informações do bloco lido.
    '''
    if not os.path.isdir(path_blocks):
        exit(0)
    file=open('{}/{}.json'.format(path_blocks, index))
    info=json.load(file)
    file.close()
    return info

def write_block(index, info, path_blocks='.'):
    '''
    Função de persistência do bloco

    :param index: index do bloco.
    :param info: informações do bloco.
    :param path_blocks: caminho para os blocos.
    '''
    if not os.path.isdir(path_blocks):
        os.mkdir(path_blocks)
    file=open('{}/{}.json'.format(path_blocks, index), 'w')
    file.write(info)
    file.close()

class Block(object):
    '''
    Classe que implementa o bloco da chain
    '''
    def __init__(self, info):
        '''
        Construtor do bloco da chain

        :param info: informações do bloco
        '''
        self.index=info['index']
        self.timestamp=info['timestamp']
        self.transactions=info['transactions']
        self.proof=info['proof']
        self.previous_hash=info['previous_hash']
        self.hash_proof=info['hash_proof']

    def __str__(self):
        '''
        Método que retorna a representação em string do bloco

        :returns: str -- string que representa o bloco com suas informações
        '''
        return '{'+'\n\t"index":"{0}",\n\t"timestamp":"{1}",\n\t"transactions":"{2}",\n\t"proof":"{3}",\n\t"previous_hash":"{4}",\n\t"hash_proof":"{5}"\n'.format(self.index, self.timestamp, self.transactions, self.proof, self.previous_hash, self.hash_proof)+'}'

    def to_dic(self):
        '''
        Método que retorna um dicionário com as informações do bloco

        :returns: dic -- informações do bloco
        '''
        info={
            'index':self.index,
            'timestamp':self.timestamp,
            'transactions':self.transactions,
            'proof':self.proof,
            'previous_hash':self.previous_hash,
            'hash_proof':self.hash_proof
        }
        return info

class Chain(object):
    '''
    Classe que implementa a chain da blockchain
    '''
    def __init__(self, path_blocks):
        '''
        Construtor da classe chain
        '''
        self.path_blocks=path_blocks# port
        if os.path.isdir(self.path_blocks):#remove a pasta, se existir
            shutil.rmtree(self.path_blocks)
        os.mkdir(self.path_blocks)#cria a pasta sem blocos
        self._list_blocks = []
        self.list_blocks=[]
        self.last_block={
            'index':0,
            'timestamp':'',
            'transactions':'',
            'proof':'',
            'previous_hash':'',
            'hash_proof':''
        }

    def __str__(self):
        '''
        Método que retorna uma string que representa a chain

        :returns: str -- string que representa a chain com seus blocos
        '''
        string='{\n'
        for block in self._list_blocks[:-1]:
            string=''.join([string, str(block), ',\n'])
        string=''.join([string, str(self._list_blocks[-1]), '\n'])
        string=''.join([string, '}'])
        return string

    def __del__(self):
        '''
        Destrutor da classe
        '''
        for i in range(len(self._list_blocks)):#limpa da memória os blocos da lista
            temp=self._list_blocks.pop()
            del temp
        if input('Do you want delete existing blocks? [y/n]')=='y':#apaga a pasta com os blocos se o usuário digitar s
            if os.path.isdir(self.path_blocks):
                shutil.rmtree('./{}'.format(self.path_blocks))

    def block(self, index):
        '''
        Método que retorna as informações de um bloco da chain

        :param index: index do bloco desejado
        :returns: dic -- informações do bloco
        '''
        info=None
        return_block=None
        for block in self._list_blocks:
            if block.index==index:
                return_block=block
        if return_block!=None:#se o bloco estiver em memória, retorna o bloco em memória
            info={
                'index':return_block.index,
                'timestamp':return_block.timestamp,
                'transactions':return_block.transactions,
                'proof':return_block.proof,
                'previous_hash':return_block.previous_hash,
                'hash_proof':return_block.hash_proof
            }
        elif os.path.isfile('{}/{}.json'.format(self.path_blocks, index)):#se o bloco existir no disco, retorna o bloco do disco
            info=read_block(index, self.path_blocks)
        else:#se o bloco não estiver nem na memória e nem no disco, retorna um bloco vazio
            info={
                'index':'',
                'timestamp':'',
                'transactions':'',
                'proof':'',
                'previous_hash':'',
                'hash_proof':''
            }
        return info

    def to_list_blocks(self, list_info):
        '''
        Método que converte uma lista de informações de blocos em uma lista de blocos

        :param list_info: lista de informações de blocos
        :returns: list -- lista de blocos
        '''
        list_blocks=[]
        for info in list_info:
            list_blocks.append(Block(info))
        return list_blocks

    @property
    def path_blocks(self):
        '''
        Método getter que retorna o caminho do blocos

        :returns: str -- caminho/pasta dos blocos
        '''
        return self._path_blocks

    @path_blocks.setter
    def path_blocks(self, path_blocks):
        '''
        Método setter que sobrescreve o caminho dos blocos

        :param path_blocks: caminho/pasta dos blocos
        '''
        self._path_blocks=path_blocks

    @property
    def list_blocks(self):
        '''
        Método que retorna uma lista com as informações dos blocos em memória

        :returns: list -- lista que contém as informações dos blocos em memória
        '''
        list_blocks=[]
        for block in self._list_blocks:
            list_blocks.append(block.to_dic())
        return list_blocks

    @list_blocks.setter
    def list_blocks(self, list_info):
        '''
        Método setter para a lista de blocos em memória da chain

        :param list_info: lista de informações
        '''
        if os.path.isdir(self.path_blocks):#remove a pasta, se existir
            shutil.rmtree(self.path_blocks)
        os.mkdir(self.path_blocks)#cria a pasta sem blocos
        list_blocks=self.to_list_blocks(list_info)#cria uma nova lista de blocos
        for block in list_blocks:#sobrescreve a lista de blocos no disco
            write_block(block.index, str(block), self.path_blocks)
        self._list_blocks=list_blocks[-10:]

    @property
    def last_block(self):
        '''
        Método getter que retorna a informação do último bloco

        :returns: dic -- informações do último bloco
        '''
        return self._list_blocks[-1].to_dic()

    @last_block.setter
    def last_block(self, info):
        '''
        Método setter que adiciona o último bloco na chain

        :param info: informações do bloco que será adicionado na chain
        '''
        if len(self._list_blocks)>9:#se a lista de blocos já tiver 10 blocos, remove o primeiro
            temp=self._list_blocks.pop(0)
            del temp
        new_block=Block(info)
        self._list_blocks.append(new_block)
        write_block(new_block.index, str(new_block), self.path_blocks)#grava o bloco em disco

    def range_blocks(self, range_index):
        '''
        Método que retorna um range de informações dos blocos desejados

        :param range_index: range de indexs dos blocos desejados
        :returns: list -- lista de informações dos blocos
        '''
        list_blocks=[]
        for index in range_index:
            try:#testa se o bloco existe em disco, se não existir contínua para a próxima iteração
                list_blocks.append(Block(read_block(index, self.path_blocks)).to_dic())
            except:
                continue
        return list_blocks

if __name__ == "__main__":
    pass
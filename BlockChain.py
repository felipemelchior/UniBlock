import hashlib
import json
import re
from time import time
from colorama import Fore, Style
import tools as tls
import random

styleCommunication = Fore.MAGENTA + Style.BRIGHT
styleClient = Fore.GREEN + Style.BRIGHT

class BlockChain(object):

	'''
	Classe pai da blockchain.
	Implementa os metodos essenciais para a blockchain.
	'''

	def __init__(self, path_blocks):
		'''
		Construtor da classe BlockChain.
		Inicia a lista chain da classe e a regra da prova de trabalho.
		'''
		self._chain=tls.Chain(path_blocks)#chain da blockchain
		self.rule='0000'#a regra inicialmente comeca com quatro zeros
    
	@property
	def rule(self):
		'''
		Metodo getter para a regra da prova de trabalho.

		:returns: int -- regra da prova de trabalho.
		'''
		return self._rule
	
	@rule.setter
	def rule(self, rule):
		'''
		Metodo setter para a regra da prova de trabalho.
		
		:param rule: regra da prova de trabalho.
		'''
		self._rule=rule

	@staticmethod
	def hash(block):
		'''
		Metodo estatico que gera a hash do bloco.

		:param block: bloco da cadeia de blocos.
		:returns: str -- hash do bloco.
		'''
		block_string=json.dumps(block, sort_keys=True).encode()
		return hashlib.sha256(block_string).hexdigest()

	@staticmethod
	def valid_proof(last_proof, proof, rule):
		'''
		Metodo estatico que valida a proof gerada.

		:param last_proof: ultima prova.
		:param proof: prova atual.
		:param rule: regra da prova de trabalho.
		:returns: bool -- flag da prova de trabalho gerada.
		'''
		guess='{0}{1}'.format(last_proof, proof).encode()
		guess_hash=hashlib.sha256(guess).hexdigest()
		return (guess_hash[:len(rule)]==rule, guess_hash)

	@property
	def last_proof(self):
		'''
		Metodo getter para a ultima prova de trabalho adicionada na chain.

		:returns: int -- ultima prova de trabalho.
		'''
		return self.last_block['proof']

	@property
	def chain(self):
		'''
		Metodo getter para a cadeia de blocos.

		:returns: list -- cadeia de blocos.
		'''
		return self._chain.list_blocks

	@chain.setter
	def chain(self, chain):
		'''
		Metodo setter para a cadeia de blocos.

		:param chain: cadeia de blocos.
		'''
		self._chain.list_blocks=chain

	@property
	def last_block(self):
		'''
		Metodo getter para o ultimo bloco da chain.

		:returns: list -- ultimo bloco da cadeia de blocos.
		'''
		return self._chain.last_block

	@last_block.setter
	def last_block(self, block):
		'''
		Metodo setter para adicionar um novo block para a chain como se fosse uma atribuicao qualquer.
		
		:param block: bloco que sera inserido na cadeia de blocos.
		'''
		self._chain.last_block=block

	def valid_chain(self, chain):
		'''
		Confere se a chain eh valida atraves das hashs da chain.

		:param chain: cadeia de blocos.
		:returns: bool -- flag da validade do ultimo bloco da cadeia de blocos.
		'''
		for index in range(1, int(self.last_block['index'])):
			if chain[index]['previous_hash']!=self.hash(chain[index-1]):
				return False
			if not self.valid_proof(chain[index-1]['proof'], chain[index]['proof'], self.rule)[0]:
				return False
		return True

	@property
	def full_chain(self):
		return self._chain.range_blocks(range(int(self.chain[len(self.chain)-1]['index'])+1))

class MinerChain(BlockChain):

	max_transactions=2

	'''
	Classe que extende a classe BlockChain
	Classe que implementa os metodos da chain utilizada pelos mineradores da blockchain
	'''

	def __init__(self, path_blocks):
		'''
		Construtor da classe 
		Cria a lista de transacoes
		Inicia a flag que diz quando um block pode comecar a ser minerado
		'''
		super().__init__(path_blocks)
		self.transactions=[[]]
		self.start_miner=False
		self.block=None

	@property
	def block(self):
		'''
		Metodo getter do block.

		:returns: list -- bloco da cadeia de blocos.
		'''
		return self._block
	
	@block.setter
	def block(self, block):
		'''
		Metodo setter do block.

		:param block: novo bloco da cadeia de blocos.
		'''
		self._block=block

	@property
	def transactions(self):
		'''
		Metodo getter para as transacoes.

		:returns: list -- lista de transacoes.
		'''
		return self._transactions

	@transactions.setter
	def transactions(self, transactions):
		'''
		Metodo setter das transacoes.
		Vai servir para que sejam passadas as transacoes entre o antigo e o novo dono da carteira.

		:param transactions: lista de transacoes.
		'''
		self._transactions=transactions

	@property
	def current_transactions(self):
		'''
		Metodo getter para as transacoes atuais.

		:returns: dict -- transacao atual.
		'''
		return self.transactions[-1]

	@property
	def finish_transactions(self):
		'''
		Metodo getter para as transacoes fechadas.

		:returns: dict -- transacao.
		'''
		return self.transactions[0] if len(self.transactions[0])==self.max_transactions else []

	@finish_transactions.setter
	def finish_transactions(self, f_t):
		'''
		Metodo setter para adicionar carteiras que ja foram terminadas e estao prontas para serem mineradas.
		Vai servir para passar as carteiras para os mineradores comecarem a minerar.

		:param f_t: carteira pronta para ser mineirada.
		'''
		self._transactions.insert(0, f_t)

	def new_transaction(self, transaction):
		'''
		Metodo que recebe uma nova transacao e adiciona nas transacoes atuais.
		Se o numero maximo de transacoes da carteira for atingido.
		Uma nova carteira e adicionada na lista de transacoes.

		:param transaction: nova transacao.
		:returns: int -- indice do proximo bloco.
		'''
		#if len(self.current_transactions) >=self.max_transactions:
			#self.transactions.append([])
		self.current_transactions.append(transaction)
		return self.last_block['index']+1

	@property
	def start_miner(self):
		'''
		Metodo getter para retornar o valor da flag _start_miner.
		Responsavel por dizer (return True) quando uma carteira esta pronta para ser minerada.

		:returns: bool -- flag de inicio da mineracao.
		'''
		return self._start_miner

	@start_miner.setter
	def start_miner(self, value):
		'''
		Metodo setter para mudar o valor da flag start_miner.

		:param value: novo valor da flag de inicio da mineracao.
		'''
		self._start_miner=value

	def new_block(self, proof, previous_hash=None):
		'''
		Cria um novo bloco com as informacoes.

		:param proof: prova de trabalho.
		:param previous_hash: hash do bloco anterior.
		:returns: dict -- novo bloco.
		'''
		block={
			# 'index':len(self.chain)+1,
			'index': int(self.last_block['index'])+1,
			'timestamp':time(),
			'transactions':self.finish_transactions.copy(),
			'proof':proof,
			'previous_hash':self.hash(self.last_block),
		}
		if len(self.transactions) == 1:
			self.finish_transactions.clear()
		else:
			self._transactions.pop(0)
		
		return block

	def proof_of_work(self, last_proof):
		'''
		Metodo de prova de trabalho.
		Determina a dificuldade de minerar um block.

		:param last_proof: ultima prova de trabalho.
		:returns: int -- prova de trabalho.
		'''
		proof=0
		while self.valid_proof(last_proof, proof, self.rule)[0] is False and self.start_miner==True:
			proof+=1
		return (proof, self.valid_proof(last_proof, proof, self.rule)[1])
	
	def mine(self):
		'''
		Minera a carteira se ja estiver pronto para minerar.
		Muda a flag para false e retorna o block minerado.
		'''
		if self.start_miner:
			proof, hash_proof=self.proof_of_work(self.last_proof)
			previous_hash=self.hash(self.last_block)
			block=self.new_block(proof, previous_hash)
			block['hash_proof']=hash_proof
			if self.start_miner:
				self.block=block
			else:
				self.block=None
			self.start_miner=False
		else:
			self.block=None
		

class TraderChain(BlockChain):
	'''
	Classe que implementa a chain dos traders
	'''

	def __init__(self, path_blocks):
		'''
		Construtor da classe
		'''
		super().__init__(path_blocks)

	def new_transaction(self, myIp):
		'''
		Cria uma nova transacao que sera enviada para a carteira ativa

		:param myIp: ip da maquina.
		:returns: dict -- lista de transacoes.
		'''
		global styleClient
		transaction = {}

		userInput = input(styleClient + 'Enter your message => ' + Fore.RED)

		if re.search('exit', userInput):
			print(styleClient + 'Ending the execution of program... ')
			exit()

		transaction['userInput'] = userInput
		transaction['address'] = myIp
		transaction['reward'] = random.randint(1, 10)

		return transaction

if __name__=='__main__':
	pass
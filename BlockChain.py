import hashlib
import json
import re
from time import time
from colorama import Fore, Style

styleCommunication = Fore.MAGENTA + Style.BRIGHT
styleClient = Fore.GREEN + Style.BRIGHT

max_transactions=2

class BlockChain(object):

	'''
	classe pai da blockchain
	implementa os metodos essenciais para a blockchain
	'''

	def __init__(self):
		'''
		construtor da classe BlockChain
		inicia a lista chain da classe e a regra da prova de trabalho
		'''
		self.chain=[]#chain da blockchain
		self.chain.append({
			'index':len(self.chain)+1,
			'timestamp':time(),
			'transactions':[],
			'proof':0,
			'previous_hash':0,
		})
		self.rule='0000'#a regra inicialmente comeca com quatro zeros
    
	@property
	def rule(self):
		'''
		metodo que retorna a regra da prova de trabalho
		'''
		return self._rule
	
	@rule.setter
	def rule(self, rule):
		'''
		metodo para mudar a regra da prova de trabalho
		'''
		self._rule=rule

	@staticmethod
	def hash(block):
		'''
		metodo estatico que gera a hash do bloco
		'''
		block_string=json.dumps(block, sort_keys=True).encode()
		return hashlib.sha256(block_string).hexdigest()

	@staticmethod
	def valid_proof(last_proof, proof, rule):
		'''
		metodo estatico que valida a proof gerada
		'''
		guess='{0}{1}'.format(last_proof, proof).encode()
		guess_hash=hashlib.sha256(guess).hexdigest()
		return guess_hash[:len(rule)]==rule

	@property
	def last_proof(self):
		'''
		retorna a ultima prova de trabalho adicionada na chain
		'''
		return self.last_block['proof']

	@property
	def chain(self):
		'''
		getter da chain
		'''
		return self._chain

	@chain.setter
	def chain(self, chain):
		'''
		setter da chain
		'''
		self._chain=chain

	@property
	def last_block(self):
		'''
		metodo para retornar o ultimo bloco da chain
		'''
		return self.chain[-1]

	@last_block.setter
	def last_block(self, block):
		'''
		um metodo setter para adicionar um novo block para a chain como se fosse uma atribuicao qualquer
		'''
		self._chain.append(block)

	def valid_chain(self, chain):
		'''
		confere se a chain eh valida atraves das hashs da chain
		'''
		for index in range(1, len(self.chain)):
			if chain[index]['previous_hash']!=self.hash(chain[index-1]):
				return False
			if not self.valid_proof(chain[index-1]['proof'], chain[index]['proof'], self.rule):
				return False
		return True

class MinerChain(BlockChain):

	'''
	classe que extende a classe BlockChain
	classe que implementa os metodos da chain utilizada pelos mineradores da blockchain
	'''

	def __init__(self):
		'''
		construtor da classe 
		cria a lista de transacoes
		inicia a flag que diz quando um block pode comecar a ser minerado
		'''
		super().__init__()
		self.transactions=[[]]
		self.start_miner=False
		self.block=None

	@property
	def block(self):
		return self._block
	
	@block.setter
	def block(self, block):
		self._block=block

	@property
	def transactions(self):
		'''
		metodo getter para retornar as transacoes
		'''
		return self._transactions

	@transactions.setter
	def transactions(self, transactions):
		'''
		metodo setter das transacoes
		vai servir para que sejam passadas as transacoes entre o antigo e o novo dono da carteira
		'''
		self._transactions=transactions

	@property
	def current_transactions(self):
		'''
		metodo getter para retornar as transacoes atuais
		'''
		return self.transactions[-1]

	@property
	def finish_transactions(self):
		'''
		metodo getter para retornar as transacoes fechadas
		'''
		return self.transactions[0] if len(self.transactions[0])==max_transactions else []

	@finish_transactions.setter
	def finish_transactions(self, f_t):
		'''
		metodo setter para adicionar carteiras que ja foram terminadas e estao prontas para serem mineradas
		vai servir para passar as carteiras para os mineradores comecarem a minerar
		'''
		self._transactions.insert(0, f_t)

	def new_transaction(self, transaction):
		'''
		metodo que recebe uma nova transacao e adiciona nas transacoes atuais
		se o numero maximo de transacoes da carteira for atingido
		uma nova carteira eh adionada na lista de transacoes
		'''
		if len(self.current_transactions) >=max_transactions:
			self.transactions.append([])
		self.current_transactions.append(transaction)
		return self.last_block['index']+1

	@property
	def start_miner(self):
		'''
		metodo getter para retornar o valor da flag _start_miner
		responsavel por dizer (return True) quando uma carteira esta pronta para ser minerada
		'''
		return self._start_miner

	@start_miner.setter
	def start_miner(self, value):
		'''
		metodo setter para mudar o valor da flag start_miner
		'''
		self._start_miner=value

	def new_block(self, proof, previous_hash=None):
		'''
		Cria um novo bloco com as informacoes
		'''
		block={
			'index':len(self.chain)+1,
			'timestamp':time(),
			'transactions':self.finish_transactions,
			'proof':proof,
			'previous_hash':previous_hash or self.hash(self.last_block),
		}
		self._transactions.pop(0)
		return block

	def proof_of_work(self, last_proof):
		'''
		metodo de prova de trabalho
		determina a dificuldade de minerar um block
		'''
		proof=0
		while self.valid_proof(last_proof, proof, self.rule) is False and self.start_miner==True:
			proof+=1
		return proof
	
	def mine(self):
		'''
		minera a carteira se ja estiver pronto para minerar
		muda a flag para false e retorna o block minerado
		'''
		if self.start_miner:
			proof=self.proof_of_work(self.last_proof)
			previous_hash=self.hash(self.last_block)
			block=self.new_block(proof, previous_hash)
			if self.start_miner:
				self.block=block
			else:
				self.block=None
			self.start_miner=False
		else:
			self.block=None
		

class TraderChain(BlockChain):
	'''
	classe que implementa a chain dos traders
	'''

	def __init__(self):
		'''
		construtor da classe
		'''
		super().__init__()

	def new_transaction(self, myIp):
		'''
		cria uma nova transacao que sera enviada para a carteira ativa
		'''
		global styleClient
		transaction = {}

		userInput = input(styleClient + 'Enter your message => ' + Fore.RED)

		if re.search('exit', userInput):
			print(styleClient + 'Ending the execution of program... ')
			exit()

		transaction['userInput'] = userInput
		transaction['address'] = myIp

		return transaction

def main():
	pass

if __name__=='__main__':
	main()

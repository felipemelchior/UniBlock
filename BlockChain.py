import hashlib
import json
from time import time
from uuid import uuid4

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
		self.rule='0000'#a regra inicialmente comeca com quatro zeros

	def add_block(self, block):
		'''
		adiciona o novo block na chain
		'''
		self.chain.append(block)

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
		return guess_hash[:4]==rule

	@property
	def last_proof(self):
		'''
		retorna a ultima prova de trabalho adicionada na chain
		'''
		return self.last_block['proof']

	@property
	def last_block(self):
		'''
		metodo para retornar o ultimo bloco da chain
		'''
		return self.chain[-1]

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

	def resolve_conflicts(self):
		'''
		funcao que decide a prioridade para adicionar na chain caso dois mineradores passarem pela prova de trabalho juntos
		'''
		# neighbours = self.nodes
		# new_chain = None
		# for node in neighbours:
		# 	response = requests.get(f'http://{node}/chain')
		# 	if response.status_code == 200:
		# 		length = response.json()['length']
		# 		chain = response.json()['chain']
		# 		if length > max_length and self.valid_chain(chain):
		# 			max_length = length
		# 			new_chain = chain
		# if new_chain:
		# 	self.chain = new_chain
		# 	return True
		# return False
		return True# TODO -> criar um metodo para resolver conflitos de forma eficiente

	def consensus(self):
		'''
		testa se a chain usada pelo cliente esta correta ou n
		caso esteja, retorna true e avisa os outros clientes
		caso nao esteja, retorna false e pede uma chain valida
		'''
		replace=self.resolve_conflicts()
		if replace:
			return False
		else:
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
		self._transactions=[[]]
		self.start_miner=False

	@property
	def transactions(self):
		'''
		metodo getter para retornar as transacoes
		'''
		return self._transactions

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
		return self.transactions[0]

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
		block={
			'index':len(self.chain)+1,
			'timestamp':time(),
			'transactions':self.finish_transactions,
			'proof':proof,
			'previous_hash':previous_hash or self.hash(self.last_block),
		}
		self.transactions.pop(0)
		return block

	def proof_of_work(self, last_proof):
		'''
		metodo de prova de trabalho
		determina a dificuldade de minerar um block
		'''
		proof=0
		while self.valid_proof(last_proof, proof, self.rule) is False:
			proof+=1
		return proof
	
	def mine(self):
		proof=self.proof_of_work(self.last_proof)
		previous_hash=self.hash(self.last_block)
		block=self.new_block(proof, previous_hash)
		response={}# TODO -> qual vai ser a resposta?
		return response

class TraderChain(BlockChain):
	'''
	classe que implementa a chain dos traders
	'''

	def __init__(self):
		'''
		construtor da classe
		'''
		super().__init__()

	def new_transaction(self):
		'''
		cria uma nova transacao que sera enviada para a carteira ativa
		'''
		transaction=None# TODO -> definir como e o que vamos encapsular em uma transacao
		return transaction

def main():
	pass

if __name__=='__main__':
	main()

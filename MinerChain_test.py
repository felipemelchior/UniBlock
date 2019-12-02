import unittest
from BlockChain import MinerChain


class Test_MinerChain(unittest.TestCase):

    
    def test_removeMinedTrasactions1(self):
        minerChain = MinerChain('blocks/{}'.format(10000))
        remainList = []
        
        transaction1 = {}
        transaction2 = {}
        transaction3 = {}
        transaction4 = {}
        transaction5 = {}
        transaction6 = {}
        transaction7 = {}
        transaction8 = {}

        transaction1['priority'] = 1
        transaction2['priority'] = 2
        transaction3['priority'] = 3
        transaction4['priority'] = 4

        transaction5['priority'] = 1
        transaction6['priority'] = 2
        transaction7['priority'] = 6
        transaction8['priority'] = 7

        remainList.append(transaction7)
        remainList.append(transaction8)

        minerChain.new_transaction(transaction5)
        minerChain.new_transaction(transaction6)
        minerChain.new_transaction(transaction7)
        minerChain.new_transaction(transaction8)

        bloco={
                'index':'',
                'timestamp':'',
                'transactions':[transaction1,transaction2,transaction3, transaction4],
                'proof':'',
                'previous_hash':'',
                'hash_proof':''
            }
        

        minerChain.removeMinedTrasactions(bloco)

        self.assertEqual(remainList, minerChain.current_transactions)

    
    def test_removeMinedTrasactions2(self):
        minerChain = MinerChain('blocks/{}'.format(10000))
        remainList = []
        
        transaction1 = {}
        transaction2 = {}
        transaction3 = {}
        transaction4 = {}
        transaction5 = {}
        transaction6 = {}
        transaction7 = {}
        transaction8 = {}

        transaction1['priority'] = 1
        transaction2['priority'] = 2
        transaction3['priority'] = 3
        transaction4['priority'] = 4

        transaction5['priority'] = 1
        transaction6['priority'] = 2
        transaction7['priority'] = 3
        transaction8['priority'] = 4

        minerChain.new_transaction(transaction5)
        minerChain.new_transaction(transaction6)
        minerChain.new_transaction(transaction7)
        minerChain.new_transaction(transaction8)

        bloco={
                'index':'',
                'timestamp':'',
                'transactions':[transaction1,transaction2,transaction3, transaction4],
                'proof':'',
                'previous_hash':'',
                'hash_proof':''
            }
        

        minerChain.removeMinedTrasactions(bloco)

        self.assertEqual(remainList, minerChain.current_transactions)

    
    
    def test_removeMinedTrasactions3(self):
        minerChain = MinerChain('blocks/{}'.format(10000))
        remainList = []
        
        transaction1 = {}
        transaction2 = {}
        transaction3 = {}
        transaction4 = {}
        transaction5 = {}
        transaction6 = {}
        transaction7 = {}
        transaction8 = {}

        transaction1['priority'] = 1
        transaction2['priority'] = 2
        transaction3['priority'] = 3
        transaction4['priority'] = 4

        transaction5['priority'] = 5
        transaction6['priority'] = 6
        transaction7['priority'] = 7
        transaction8['priority'] = 8

        remainList.append(transaction5)
        remainList.append(transaction6)
        remainList.append(transaction7)
        remainList.append(transaction8)

        minerChain.new_transaction(transaction5)
        minerChain.new_transaction(transaction6)
        minerChain.new_transaction(transaction7)
        minerChain.new_transaction(transaction8)

        bloco={
                'index':'',
                'timestamp':'',
                'transactions':[transaction1,transaction2,transaction3, transaction4],
                'proof':'',
                'previous_hash':'',
                'hash_proof':''
            }
        

        minerChain.removeMinedTrasactions(bloco)

        self.assertEqual(remainList, minerChain.current_transactions)

    

    def test_validateHash(self):
        minerChain = MinerChain('blocks/{}'.format(10000))
        transaction1 = {}
        transaction2 = {}
        transaction1['priority'] = 1
        transaction2['priority'] = 2
        transactions = [transaction1,transaction2]

        block={
			# 'index':len(self.chain)+1,
			'index': 0,
			'timestamp':23232,
			'transactions':transactions.copy(),
			'previous_hash':"123123",
			'nounce':0
		}

        self.assertEqual(None, minerChain.validateHash(block))


    
    def test_generateHash(self):
        minerChain = MinerChain('blocks/{}'.format(10000))

        self.assertEqual(None, minerChain.generateBlock("12345"))

if __name__ == '__main__':
    unittest.main()
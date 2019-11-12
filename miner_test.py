import miner
import unittest
import random

class Test_Miner(unittest.TestCase):

    def test_selectTransactions1(self):
        wallet = []
        testMiner = miner.Miner("127.0.0.1", [])
        transaction1 = {}
        transaction2 = {}
        transaction3 = {}
        maxTrasactions = 2
        testMiner.blockChain.max_transactions = maxTrasactions

        #Variável de controle
        wallet.append({'priority':3})
        wallet.append({'priority':2})

        transaction1['priority'] = 1
        transaction2['priority'] = 2
        transaction3['priority'] = 3
        testMiner.blockChain.new_transaction(transaction1)
        testMiner.blockChain.new_transaction(transaction2)
        testMiner.blockChain.new_transaction(transaction3)
        newWallet = testMiner.selectTransactions(maxTrasactions)

        self.assertEqual(newWallet, wallet)

    
    def test_selectTransactions2(self):
        wallet = []
        testMiner = miner.Miner("127.0.0.1", [])
        transaction1 = {}
        transaction2 = {}
        transaction3 = {}
        maxTrasactions = 2
        testMiner.blockChain.max_transactions = maxTrasactions

        #Variável de controle
        wallet.append({'priority':3})
        wallet.append({'priority':2})

        transaction1['priority'] = 3
        transaction2['priority'] = 2
        transaction3['priority'] = 1
        testMiner.blockChain.new_transaction(transaction1)
        testMiner.blockChain.new_transaction(transaction2)
        testMiner.blockChain.new_transaction(transaction3)
        newWallet = testMiner.selectTransactions(maxTrasactions)

        self.assertEqual(newWallet, wallet)


    def test_selectTransactions3(self):
        wallet = []
        testMiner = miner.Miner("127.0.0.1", [])
        transaction1 = {}
        transaction2 = {}
        transaction3 = {}
        transaction4 = {}
        maxTrasactions = 2
        testMiner.blockChain.max_transactions = maxTrasactions

        #Variável de controle
        wallet.append({'priority':3})
        wallet.append({'priority':4})

        transaction1['priority'] = 1
        transaction2['priority'] = 2
        transaction3['priority'] = 3
        transaction4['priority'] = 4
        testMiner.blockChain.new_transaction(transaction1)
        testMiner.blockChain.new_transaction(transaction2)
        testMiner.blockChain.new_transaction(transaction3)
        testMiner.blockChain.new_transaction(transaction4)
        newWallet = testMiner.selectTransactions(maxTrasactions)

        self.assertEqual(newWallet, wallet)


    
    def test_selectTransactions4(self):
        wallet = []
        testMiner = miner.Miner("127.0.0.1", [])
        transaction1 = {}
        transaction2 = {}
        transaction3 = {}
        transaction4 = {}
        maxTrasactions = 2
        testMiner.blockChain.max_transactions = maxTrasactions

        #Variável de controle
        wallet.append({'priority':4})
        wallet.append({'priority':5})

        transaction1['priority'] = 2
        transaction2['priority'] = 5
        transaction3['priority'] = 4
        transaction4['priority'] = 3
        testMiner.blockChain.new_transaction(transaction1)
        testMiner.blockChain.new_transaction(transaction2)
        testMiner.blockChain.new_transaction(transaction3)
        testMiner.blockChain.new_transaction(transaction4)
        newWallet = testMiner.selectTransactions(maxTrasactions)

        self.assertEqual(newWallet, wallet)


if __name__ == '__main__':
    unittest.main()
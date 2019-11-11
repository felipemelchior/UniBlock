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
        wallet.append({'reward':3})
        wallet.append({'reward':2})

        transaction1['reward'] = 1
        transaction2['reward'] = 2
        transaction3['reward'] = 3
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
        wallet.append({'reward':3})
        wallet.append({'reward':2})

        transaction1['reward'] = 3
        transaction2['reward'] = 2
        transaction3['reward'] = 1
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
        wallet.append({'reward':3})
        wallet.append({'reward':4})

        transaction1['reward'] = 1
        transaction2['reward'] = 2
        transaction3['reward'] = 3
        transaction4['reward'] = 4
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
        wallet.append({'reward':4})
        wallet.append({'reward':5})

        transaction1['reward'] = 2
        transaction2['reward'] = 5
        transaction3['reward'] = 4
        transaction4['reward'] = 3
        testMiner.blockChain.new_transaction(transaction1)
        testMiner.blockChain.new_transaction(transaction2)
        testMiner.blockChain.new_transaction(transaction3)
        testMiner.blockChain.new_transaction(transaction4)
        newWallet = testMiner.selectTransactions(maxTrasactions)

        self.assertEqual(newWallet, wallet)


if __name__ == '__main__':
    unittest.main()
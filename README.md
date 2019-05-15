# UniBlock - BlockChain Implementation

![blockchain](images/blockchain.jpg)

UniBlock é uma implementação de uma estrutura de BlockChain realizada na disciplina de Sistemas Distribuídos do Sétimo Semestre da Universidade Federal do Pampa - Brasil.

## O que é um BlockChain

O blockchain (também conhecido como “o protocolo da confiança”) é uma tecnologia de registro distribuído que visa a descentralização como medida de segurança. São bases de registros e dados distribuídos e compartilhados que têm a função de criar um índice global para todas as transações que ocorrem em um determinado mercado. Funciona como um livro-razão, só que de forma pública, compartilhada e universal, que cria consenso e confiança na comunicação direta entre duas partes, ou seja, sem o intermédio de terceiros. Está constantemente crescendo à medida que novos blocos completos são adicionados a ela por um novo conjunto de registros. Os blocos são adicionados à blockchain de modo linear e cronológico. Cada nó - qualquer computador que conectado a essa rede tem a tarefa de validar e repassar transações - obtém uma cópia da blockchain após o ingresso na rede. A blockchain possui informação completa sobre endereços e saldos diretamente do bloco gênese até o bloco mais recentemente concluído. 

Fonte: [Wikipédia](https://pt.wikipedia.org/wiki/Blockchain), [BlockChain](https://www.blockchain.com/)

---
## Instalação

Foi utilizado apenas pacotes nativos do Python3.
Entretanto, em algumas distribuições os pacotes podem variar, neste caso instale as dependências utilizando:

```bash
$ pip3 install -r requirements.txt
```


---
## Uso

O código possui 3 tipos de usuários:

| Tipo de Usuário       | Como Funciona           | Como iniciar  |
| ------------- |:-------------:| -----:|
| Trader      | Usuário que adicionará dados no BlockChain | ```$ python3 main.py -u <usuarios> ``` |
| Miner Rich      | Minerador que começará guardando transações na carteira      |   ```$ python3 main.py -u <usuarios> --miner --rich``` |
| Miner | Usuário que minera o Bloco      |    ```$ python3 main.py -u <usuarios> --miner``` |

**Nota:** Quando o sistema for iniciado, somente um Miner Rich pode ser iniciado!

Maiores Informações sobre a implementação, consulte a página de [documentação do projeto](https://github.com/homdreen/UniBlock/tree/master/docs). 

---
## Desenvolvedores

![Felipe](images/homdreen.png)
![Guilherme](images/guilherme.png)
![Lucas](images/gordo.png)
![Rafael](images/rafa.png)

* Felipe Homrich Melchior - <fehmel@gmail.com> - [Perfil GitHub](https://github.com/homdreen) <br>
* Guilherme Neri Bustamante Sá - <guinbsa@gmail.com> - [Perfil GitHub](https://github.com/161150744) <br>
* Lucas Antunes de Almeida - <lucasalmeida053@gmail.com> - [Perfil GitHub](https://github.com/LucasAntunesdeAlmeida) <br>
* Rafael Fernandes Silva - <faelsfernandes@gmail.com> - [Perfil GitHub](https://github.com/faelsfernandes) <br>

Pull-Requests são bem-vindos e encorajados!

---
## License

Copyright (C) Felipe Homrich Melchior (2019-), Guilherme Neri Bustamante Sá (2019-), Lucas Antunes de Almeida (2019-) and Rafael Fernandes da Silva (2019-)

Licensed under the Apache License, Version 2.0
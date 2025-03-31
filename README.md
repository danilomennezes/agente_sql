Instruções para Rodar a Aplicação

Passo 1: Criação das Tabelas no Banco de Dados.

•	Crie o banco de dados vendas_db no PostgreSQL.

•	Em seguida, crie as tabelas necessárias utilizando os seguintes comandos SQL:



CREATE TABLE clientes (
    id_cliente SERIAL PRIMARY KEY,
    nome VARCHAR(100),
    saldo DECIMAL(10, 2)
);

CREATE TABLE produtos (
    id_produto SERIAL PRIMARY KEY,
    nome VARCHAR(100),
    preco DECIMAL(10, 2),
    estoque INT
);

CREATE TABLE transacoes (
    id_transacao SERIAL PRIMARY KEY,
    id_cliente INT REFERENCES clientes(id_cliente),
    id_produto INT REFERENCES produtos(id_produto),
    data_transacao TIMESTAMP,
    quantidade INT,
    valor_transacao DECIMAL(10, 2)
);

Passo 2: Inserção de Dados nas Tabelas.

•	Após a criação das tabelas, insira os dados de exemplo utilizando os seguintes comandos SQL:

INSERT INTO clientes (nome, saldo) VALUES
('Maria Oliveira', 1200.00),
('Carlos Silva', 750.50),
('Ana Souza', 980.00),
('Ricardo Lima', 550.75),
('Juliana Pereira', 1300.00);

INSERT INTO produtos (nome, preco, estoque) VALUES
('Notebook', 5000.00, 20),
('Smartphone', 7000.00, 15),
('Teclado', 450.00, 50),
('Monitor', 2200.00, 30),
('Fone de Ouvido', 1500.00, 25);

INSERT INTO transacoes (id_cliente, id_produto, data_transacao, quantidade, valor_transacao) VALUES
(1, 1, '2025-03-01 10:15:00', 1, 5000.00),
(2, 2, '2025-03-02 14:30:00', 2, 14000.00),
(3, 3, '2025-03-03 16:00:00', 1, 450.00),
(4, 4, '2025-03-04 11:45:00', 1, 2200.00),
(5, 5, '2025-03-05 09:30:00', 1, 1500.00),
(1, 2, '2025-03-06 13:20:00', 1, 7000.00),
(2, 3, '2025-03-07 12:10:00', 3, 1350.00),
(3, 4, '2025-03-08 15:55:00', 1, 2200.00),
(4, 5, '2025-03-09 10:25:00', 2, 3000.00),
(5, 1, '2025-03-10 17:40:00', 1, 5000.00);


Passo 3: Instalação das Dependências.

pip install langchain, langchain.openai, psycopg, psycopg2, langchain_community, langgraph


Passo 4: Configuração das Variáveis de Ambiente.

•	Para instalar as dependências necessárias, abra o terminal e execute o seguinte comando:

$env:token_openai = "insira seu token aqui"

$env:senha_pgadmin = "insira a senha do banco aqui"

$env:usuario_pgadmin = "insira o login do banco aqui"


Passo 5: Execução do Código.

•	Abra o PyCharm ou sua IDE preferida.

•	Abra o arquivo agent_sql.py no seu projeto.

•	Abra o terminal e execute o seguinte comando: python agent_sql.py

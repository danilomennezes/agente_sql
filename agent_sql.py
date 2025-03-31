import os

from langchain_openai import ChatOpenAI
from langchain.agents import AgentType, initialize_agent
from langchain.agents import Tool

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.llms import OpenAI

import psycopg2
from typing import TypedDict


openai_api_key = os.getenv("token_openai")
senha_db = os.getenv("senha_pgadmin")
usuario_db = os.getenv("usuario_pgadmin")

llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=openai_api_key)


class State(TypedDict):
    sql: str
    parametros: dict
    resultados: str
    pergunta: str
    resposta: str

def conexao_db():
    try:
        conn = psycopg2.connect(
            dbname="vendas_db",
            user=usuario_db,
            password=senha_db,
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None


prompt_template = """
                    Você é um assistente de geração de SQL.
                    Essa é a estrutura do banco de dados:
                    -- Tabela de clientes
                    CREATE TABLE clientes (
                        id_cliente SERIAL PRIMARY KEY,
                        nome VARCHAR(100),
                        saldo DECIMAL(10, 2)
                    );

                    -- Tabela de produtos
                    CREATE TABLE produtos (
                        id_produto SERIAL PRIMARY KEY,
                        nome VARCHAR(100),
                        preco DECIMAL(10, 2),
                        estoque INT
                    );

                    -- Tabela de transações
                    CREATE TABLE transacoes (
                        id_transacao SERIAL PRIMARY KEY,
                        id_cliente INT REFERENCES clientes(id_cliente),
                        id_produto INT REFERENCES produtos(id_produto),
                        data_transacao TIMESTAMP,
                        quantidade INT,
                        valor_transacao DECIMAL(10, 2)
                    );

                    A seguinte é uma pergunta do usuário, e você deve gerar a consulta SQL correspondente.

                    Pergunta: {pergunta}
                    Consulta SQL:
                    """

prompt_transformar = """
                    Você é um assistente especializado na conversão de comandos SQL.

                    Sua tarefa é receber um comando SQL e transformá-lo utilizando parâmetros (%s) e também gerar uma lista de parâmetros que devem ser usados para substituir esses placeholders.
                    Nunca altere o SQL, somente insira os placeholders.

                    Exemplo de resposta:

                        Consulta SQL: select * from clientes where cliente.nome = %s
                        Parâmetros: [xxxxxxxx]

                    A seguinte é o SQL:
                    {resposta}

                    Consulta SQL:
                    Parâmetros:
                    """

prompt = PromptTemplate(input_variables=["pergunta"], template=prompt_template)
prompt_transformar = PromptTemplate(input_variables=["resposta"], template=prompt_transformar)

chain = LLMChain(llm=llm, prompt=prompt)
# chain = prompt | llm
chain_transformar = LLMChain(llm=llm, prompt=prompt_transformar)
# chain_transformar = prompt | llm


# Função para gerar SQL
def gerar_sql(state: State) -> State:
    pergunta = state["pergunta"]

    resposta = chain.run(pergunta)
    respostasql = chain_transformar.run(resposta)

    partes = respostasql.split("Parâmetros:")
    sql = partes[0].strip().replace("Consulta SQL:", "").strip()

    parametros = eval(partes[1].strip())

    # print(f"Resposta:  {resposta}")
    # print(f"Resposta sql:  {respostasql}")
    # print(f"parametro:  {parametros}")

    return {**state, "sql": sql, "parametros": parametros}


# Função para executar consultas SQL no banco de dados
def executar_consulta_sql(state: State) -> State:
    sql = state["sql"]
    params = state["parametros"]

    conn = conexao_db()

    if conn is None:
        return {**state, "resultados": "Desculpe, não conseguimos conexão ao banco de dados."}

    try:

        db = conn.cursor()
        db.execute(sql, params)

        # verificando se a primeira palavra é 'select", para permitir somente fazer consulta ao db
        if "select" in sql.strip().split()[0].lower():
            resultados = db.fetchall()
            resultados_str = resultados
        else:
            resultados_str = "Comando não executado."

        db.close()
        conn.close()

        return {**state, "resultados": resultados_str}

    except Exception as e:
        print(f"Erro ao conectar ou executar a consulta: {e}")
        return {**state, "resultados": "Desculpe, não conseguimos consultar o banco de dados."}


# Função para gerar resposta
def gerar_resposta_fluida(state: State) -> str:
    resultados = state["resultados"]
    pergunta = state["pergunta"]

    if not resultados:
        return {**state, "resposta": "Desculpe, não encontramos dados para responder à sua pergunta."}

    resposta_prompt_template = """
        Você é um assistente de geração de SQL.

        Comece a resposta com "Olá, você solicitou por..." e logo após um resumo da pergunta do usuário.

        A seguinte é uma pergunta do usuário:
        Pergunta: {pergunta}
        A seguinte é o resultado para resposta da pergunta obtido via consulta ao banco de dados:
        resultado: {resultados}

        Com base nas seguintes informações de respostas e resultados, forneça uma resposta fluida, resumida e informativa:
        Resposta:
    """
    resposta_prompt = PromptTemplate(input_variables=["resultados", "pergunta"], template=resposta_prompt_template)
    resposta_chain = LLMChain(llm=llm, prompt=resposta_prompt)
    resposta = resposta_chain.run({"resultados": resultados, "pergunta": pergunta})

    return {**state, "resposta": resposta}


from langgraph.graph import END, StateGraph

graph_builder = StateGraph(State)

def configurar_fluxo():
    workflow = StateGraph(State)
    workflow.add_node("agentsql", gerar_sql)
    workflow.add_node("agentdb", executar_consulta_sql)
    workflow.add_node("action", gerar_resposta_fluida)
    workflow.set_entry_point("agentsql")
    workflow.add_edge('agentsql', 'agentdb')
    workflow.add_edge('agentdb', 'action')
    return workflow.compile()


def main():
    while True:
        pergunta_usuario = input("Faça uma pergunta ou digite sair? ")
        if pergunta_usuario.lower() in ['sair']:
            print("Saindo... Até logo!")
            break
        app = configurar_fluxo()
        resposta = app.invoke({"pergunta": pergunta_usuario})
        print(resposta["resposta"])


if __name__ == "__main__":
    main()


# Quais clientes compraram um Notebook?
# Quanto cada cliente gastou no total?
# Quem tem saldo suficiente para comprar um Smartphone?




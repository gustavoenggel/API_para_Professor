import requests
import os
from dotenv import load_dotenv

load_dotenv()

def consultar_despesa_por_orgao(ano, codigo_orgao):
    url ="https://api.portaldatransparencia.gov.br/api-de-dados/despesas/por-orgao"

    headers = {
        "chave-api-dados": os.getenv("API_KEY")
    }

    params = {
        "ano": ano,
        "orgaoSuperior": codigo_orgao,
        "pagina": 1
    }

    resposta = requests.get(url,headers=headers, params=params)

    dados = resposta.json()

    if not dados:
        return "Nenhum registro encontrado para o ano informado."
    elif isinstance(dados, dict) and "Erro na API" in dados:
        return f"Erro na consulta: {dados['Erro na API']}"
    
    return dados


try:
    ano = input("Digite o ANO que deseja consultar (ex: 2024): ")

    # 1. Validação do formato do Ano
    if len(ano) != 4 or not ano.isdigit():
        print("ANO INVÁLIDO! O ano deve conter exatamente 4 números.")
    else:
        # 2. Exibição do Menu no Terminal
        print("\n--- Selecione o Órgão ---")
        print("[1] - Ministério da Saúde")
        print("[2] - Ministério da Educação (MEC)")
        print("[3] - Ministério da Defesa")
        print("[4] - Ministério da Justiça")

        opcao = input("\nDigite a opção desejada: ")

        # 3. Estrutura de Decisão por IF / ELIF / ELSE
        if opcao == "1":
            codigo_orgao = "36000"
            nome_orgao = "Ministério da Saúde"
        elif opcao == "2":
            codigo_orgao = "26000"
            nome_orgao = "Ministério da Educação (MEC)"
        elif opcao == "3":
            codigo_orgao = "52000"
            nome_orgao = "Ministério da Defesa"
        elif opcao == "4":
            codigo_orgao = "30000"
            nome_orgao = "Ministério da Justiça"
        else:
            codigo_orgao = None
            print("Opção inválida! Escolha um número válido do menu.")

        # 4. Chamada da Função caso o órgão seja válido
        if codigo_orgao:
            print(f"\nA procurar despesas de {ano} para {nome_orgao}...")
            resultado = consultar_despesa_por_orgao(ano, codigo_orgao)
            print(resultado)

except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")
    
if isinstance(resultado, list):
            print("\n" + "="*60)
            print(f"RESUMO DE DESPESAS ({len(resultado)} unidades/entidades encontradas)")
            print("="*60)
            
            for item in resultado:
                orgao_nome = item.get("orgao", "Não informado")
                empenhado = item.get("empenhado", "0,00")
                pago = item.get("pago", "0,00")
                
                print(f"• Entidade:  {orgao_nome}")
                print(f"  Empenhado: R$ {empenhado}")
                print(f"  Pago:      R$ {pago}")
                print("-" * 60)
else:
    print(resultado)
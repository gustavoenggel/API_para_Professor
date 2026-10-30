# 🏛️ Consulta de Despesas Públicas - Portal da Transparência

Este projeto é uma aplicação desenvolvida em Python para consumir a API de dados do **Portal da Transparência do Governo Federal**, permitindo consultar despesas públicas consolidadas por ministérios e órgãos federais.

O repositório conta com duas abordagens de uso:
1. **CLI (Terminal):** Execução via linha de comando interativa.
2. **Interface Web (Streamlit):** Painel gráfico web amigável com métricas detalhadas.

---

## 🚀 Funcionalidades

- **Autenticação Segura:** Leitura da chave de API via arquivo `.env` para proteção de credenciais.
- **Validação de Entrada:** Validação de anos com 4 dígitos numéricos e restrição de opções do menu.
- **Filtro por Órgão Superior:** Mapeamento dinâmico para códigos SIAFI de Ministérios (Saúde, Educação, Defesa, Justiça).
- **Tratamento de Erros:** Captura e exibição clara de falhas de conexão ou retornos vazios da API.
- **Visualização Amigável:** Formatação de valores empenhados e pagos em componentes visuais no Streamlit.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+**
- **[Requests](https://requests.readthedocs.io/):** Requisições HTTP para a API.
- **[Streamlit](https://streamlit.io/):** Construção da interface gráfica web.
- **[python-dotenv](https://github.com/theskumar/python-dotenv):** Gerenciamento de variáveis de ambiente.

---

## 📁 Estrutura do Projeto

```text
API_para_Professor/
├── .env                 # Arquivo com a chave privada da API (não versionado)
├── .gitignore           # Arquivos ignorados pelo Git
├── app.py               # Lógica principal e execução via Terminal (CLI)
├── frontend.py          # Interface gráfica web desenvolvida em Streamlit
├── README.md            # Documentação completa do projeto
└── requirements.txt     # Lista de dependências do Python
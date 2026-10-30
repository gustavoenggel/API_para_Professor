import base64
import os
from pathlib import Path

import altair as alt
import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

# 1. Carrega as variáveis do ficheiro .env
load_dotenv()

# URL do endpoint de despesas por órgão
API_URL = "https://api.portaldatransparencia.gov.br/api-de-dados/despesas/por-orgao"


def consultar_despesa_por_orgao(ano, codigo_orgao):
    headers = {"chave-api-dados": os.getenv("API_KEY")}
    params = {"ano": ano, "orgaoSuperior": codigo_orgao, "pagina": 1}
    resposta = requests.get(API_URL, headers=headers, params=params)
    return resposta.json()


# ======================================================================
# IMAGENS
# Dica: para usar imagens suas, crie uma pasta "assets" ao lado deste
# arquivo e salve com os nomes abaixo (ex.: assets/saude.jpg). Se o
# arquivo local existir, ele tem prioridade sobre o link da internet.
# ======================================================================
IMAGENS = {
    "hero": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1600&q=80",
    "saude": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800&q=80",
    "educacao": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800&q=80",
    "defesa": "https://images.unsplash.com/photo-1579912437766-7896df6d3cd3?w=800&q=80",
    "justica": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=800&q=80",
    "consulta": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1600&q=80",
    "sobre": "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1000&q=80",
}


def img(chave):
    """Retorna a imagem local (assets/<chave>.jpg|jpeg|png) ou o link da internet."""
    base = Path(__file__).parent / "assets"
    for ext in ("jpg", "jpeg", "png", "webp"):
        arq = base / f"{chave}.{ext}"
        if arq.exists():
            mime = "jpeg" if ext in ("jpg", "jpeg") else ext
            dados = base64.b64encode(arq.read_bytes()).decode()
            return f"data:image/{mime};base64,{dados}"
    return IMAGENS[chave]


# Mapeamento dos Órgãos (Nome -> Código SIAFI)
ORGAOS = {
    "Ministério da Saúde": "36000",
    "Ministério da Educação (MEC)": "26000",
    "Ministério da Defesa": "52000",
    "Ministério da Justiça": "30000",
}

ORGAOS_INFO = {
    "Ministério da Saúde": (
        "saude",
        "Recursos do SUS, hospitais federais, vacinação e programas de saúde pública.",
    ),
    "Ministério da Educação (MEC)": (
        "educacao",
        "Universidades e institutos federais, merenda, livros didáticos e bolsas.",
    ),
    "Ministério da Defesa": (
        "defesa",
        "Forças Armadas, operações, equipamentos e infraestrutura de defesa nacional.",
    ),
    "Ministério da Justiça": (
        "justica",
        "Segurança pública, Polícia Federal, sistema penitenciário e direitos do cidadão.",
    ),
}


# ======================================================================
# FUNÇÕES AUXILIARES
# ======================================================================
def para_float(valor):
    """Converte '1.234.567,89' (formato brasileiro) em float."""
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = str(valor).replace("R$", "").strip().replace(".", "").replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return 0.0


def brl(valor):
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def brl_curto(valor):
    for limite, sufixo in ((1e12, "tri"), (1e9, "bi"), (1e6, "mi"), (1e3, "mil")):
        if abs(valor) >= limite:
            n = f"{valor / limite:.2f}".replace(".", ",")
            return f"R$ {n} {sufixo}"
    return brl(valor)


def html(bloco):
    """Remove a indentação para o Streamlit não tratar o HTML como bloco de código."""
    st.markdown("\n".join(l.strip() for l in bloco.splitlines() if l.strip()), unsafe_allow_html=True)


# ======================================================================
# CONFIGURAÇÃO DA PÁGINA
# ======================================================================
st.set_page_config(
    page_title="Painel de Despesas Públicas",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

AZUL = "#0B3C5D"
AZUL_ESCURO = "#072A42"
VERDE = "#1B998B"
VERDE_ESCURO = "#147A6F"
FUNDO = "#F3F7FA"
TEXTO = "#1E2D3B"

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@700;900&family=Public+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {{ font-family: 'Public Sans', sans-serif; color: {TEXTO}; }}
.stApp {{ background: #FFFFFF; }}
#MainMenu, footer, header[data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
.block-container {{ max-width: 1180px; padding-top: 0 !important; padding-bottom: 0 !important; }}
html {{ scroll-behavior: smooth; }}

h1, h2, h3 {{ font-family: 'Merriweather', serif; color: {AZUL}; }}

/* ---------- Barra de navegação ---------- */
.nav {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 18px 4px; border-bottom: 1px solid #E3EAF0; background: #fff;
    position: sticky; top: 0; z-index: 99;
}}
.nav .logo {{ display: flex; align-items: center; gap: 12px; font-family: 'Merriweather', serif;
    font-weight: 900; font-size: 1.25rem; color: {AZUL}; line-height: 1.1; }}
.nav .logo small {{ display: block; font-family: 'Public Sans', sans-serif; font-weight: 500;
    font-size: .72rem; color: #6B7C8C; letter-spacing: .2px; }}
.nav .brasao {{ width: 44px; height: 44px; border-radius: 10px; background: {AZUL};
    display: flex; align-items: center; justify-content: center; font-size: 1.4rem; }}
.nav .links a {{ color: {AZUL}; text-decoration: none; font-weight: 600; font-size: .92rem;
    margin-left: 26px; padding: 6px 0; border-bottom: 2px solid transparent; }}
.nav .links a:hover {{ border-bottom-color: {VERDE}; color: {VERDE_ESCURO}; }}

/* ---------- Hero ---------- */
.hero {{
    position: relative; min-height: 400px; border-radius: 0 0 18px 18px; overflow: hidden;
    background-color: {AZUL}; background-size: cover; background-position: center;
    display: flex; align-items: center;
}}
.hero::before {{ content: ""; position: absolute; inset: 0;
    background: linear-gradient(100deg, rgba(7,42,66,.93) 0%, rgba(7,42,66,.78) 45%, rgba(7,42,66,.25) 100%); }}
.hero .conteudo {{ position: relative; padding: 56px 52px; max-width: 700px; }}
.hero h1 {{ color: #fff; font-size: 2.5rem; line-height: 1.2; margin: 0 0 16px 0; }}
.hero p {{ color: #D5E3EE; font-size: 1.1rem; line-height: 1.6; margin: 0 0 28px 0; }}
.hero a.botao {{ display: inline-block; background: {VERDE}; color: #fff; text-decoration: none;
    font-weight: 700; padding: 14px 28px; border-radius: 8px; }}
.hero a.botao:hover {{ background: {VERDE_ESCURO}; }}
.hero a.sec {{ display: inline-block; color: #fff; text-decoration: none; font-weight: 600;
    padding: 14px 20px; margin-left: 8px; border: 1px solid rgba(255,255,255,.5); border-radius: 8px; }}

/* ---------- Seções ---------- */
.secao {{ padding: 64px 0 8px 0; }}
.secao h2 {{ font-size: 1.7rem; margin: 0 0 8px 0; }}
.secao .sub {{ color: #5B6B7A; font-size: 1.02rem; max-width: 640px; margin-bottom: 30px; line-height: 1.6; }}
.barra {{ width: 56px; height: 4px; background: {VERDE}; border-radius: 2px; margin-bottom: 18px; }}

/* ---------- Cards de órgãos ---------- */
.card {{ background: #fff; border: 1px solid #E3EAF0; border-radius: 12px; overflow: hidden; height: 100%;
    box-shadow: 0 2px 10px rgba(11,60,93,.06); }}
.card .foto {{ height: 170px; background-size: cover; background-position: center;
    background-color: {AZUL}; background-image: linear-gradient(135deg, {AZUL}, {VERDE}); }}
.card .corpo {{ padding: 18px 20px 22px 20px; }}
.card h3 {{ font-size: 1.05rem; margin: 0 0 8px 0; }}
.card p {{ font-size: .92rem; color: #5B6B7A; line-height: 1.55; margin: 0; }}
.card .codigo {{ display: inline-block; margin-top: 12px; font-size: .78rem; font-weight: 600;
    color: {VERDE_ESCURO}; background: #E6F5F3; padding: 4px 10px; border-radius: 20px; }}
.grid4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }}
.grid3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }}

/* ---------- Passos ---------- */
.passo {{ background: {FUNDO}; border-radius: 12px; padding: 26px 24px; height: 100%; }}
.passo .num {{ width: 38px; height: 38px; border-radius: 50%; background: {AZUL}; color: #fff;
    display: flex; align-items: center; justify-content: center; font-weight: 700; margin-bottom: 14px; }}
.passo h3 {{ font-size: 1rem; margin: 0 0 6px 0; }}
.passo p {{ margin: 0; font-size: .92rem; color: #5B6B7A; line-height: 1.55; }}

/* ---------- Banner da consulta ---------- */
.banner {{ position: relative; border-radius: 14px 14px 0 0; overflow: hidden; min-height: 170px;
    background-color: {AZUL}; background-size: cover; background-position: center; display: flex; align-items: center; }}
.banner::before {{ content: ""; position: absolute; inset: 0;
    background: linear-gradient(90deg, rgba(7,42,66,.92), rgba(7,42,66,.55)); }}
.banner .conteudo {{ position: relative; padding: 30px 40px; }}
.banner h2 {{ color: #fff; margin: 0 0 6px 0; font-size: 1.6rem; }}
.banner p {{ color: #D5E3EE; margin: 0; }}

/* ---------- Resultado ---------- */
.res-topo {{ display: flex; gap: 20px; align-items: center; background: {FUNDO}; border-radius: 12px;
    padding: 14px; margin: 26px 0 18px 0; }}
.res-topo .foto {{ width: 150px; height: 96px; border-radius: 8px; background-size: cover; background-position: center;
    background-color: {AZUL}; flex-shrink: 0; }}
.res-topo h3 {{ margin: 0 0 4px 0; font-size: 1.2rem; }}
.res-topo span {{ color: #5B6B7A; font-size: .92rem; }}
.kpi {{ background: #fff; border: 1px solid #E3EAF0; border-left: 5px solid {VERDE}; border-radius: 10px;
    padding: 18px 20px; box-shadow: 0 2px 10px rgba(11,60,93,.05); }}
.kpi .rot {{ font-size: .82rem; color: #6B7C8C; font-weight: 600; }}
.kpi .val {{ font-family: 'Merriweather', serif; font-size: 1.55rem; color: {AZUL}; font-weight: 700; margin-top: 4px; }}
.kpi .det {{ font-size: .8rem; color: #8896A3; margin-top: 2px; }}

/* ---------- Sobre / rodapé ---------- */
.sobre {{ display: grid; grid-template-columns: 1fr 1fr; gap: 40px; align-items: center; }}
.sobre .foto {{ height: 300px; border-radius: 14px; background-size: cover; background-position: center;
    background-color: {AZUL}; background-image: linear-gradient(135deg, {AZUL}, {VERDE}); }}
.sobre p {{ line-height: 1.7; color: #46586A; }}
.rodape {{ margin-top: 72px; background: {AZUL_ESCURO}; color: #B8CBDA; border-radius: 14px 14px 0 0;
    padding: 36px 40px; display: flex; justify-content: space-between; gap: 30px; font-size: .9rem; line-height: 1.7; }}
.rodape b {{ color: #fff; font-family: 'Merriweather', serif; }}
.rodape a {{ color: #7FD6CB; text-decoration: none; }}

/* ---------- Widgets do Streamlit ---------- */
div[data-testid="stForm"] {{ border: 1px solid #E3EAF0; border-top: none; border-radius: 0 0 14px 14px;
    padding: 26px 30px 30px 30px; background: #fff; box-shadow: 0 6px 20px rgba(11,60,93,.07); }}
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {{
    border-radius: 8px; font-weight: 700; padding: .6rem 1.6rem; border: 1px solid {VERDE};
    background: {VERDE}; color: #fff; }}
.stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover {{
    background: {VERDE_ESCURO}; border-color: {VERDE_ESCURO}; color: #fff; }}
.stDownloadButton > button {{ background: #fff; color: {AZUL}; border-color: {AZUL}; }}
.stDownloadButton > button:hover {{ background: {AZUL}; color: #fff; border-color: {AZUL}; }}
div[data-testid="stExpander"] {{ border: 1px solid #E3EAF0; border-radius: 10px; }}
button:focus-visible, a:focus-visible {{ outline: 3px solid #F2B705 !important; outline-offset: 2px; }}

@media (max-width: 900px) {{
    .grid4, .grid3, .sobre {{ grid-template-columns: 1fr 1fr; }}
    .nav .links {{ display: none; }}
    .hero .conteudo {{ padding: 36px 26px; }}
    .hero h1 {{ font-size: 1.8rem; }}
}}
@media (max-width: 600px) {{
    .grid4, .grid3, .sobre {{ grid-template-columns: 1fr; }}
    .rodape {{ flex-direction: column; }}
}}
</style>
""",
    unsafe_allow_html=True,
)

# ======================================================================
# NAVEGAÇÃO + HERO
# ======================================================================
html(
    """
<div class="nav">
<div class="logo"><div class="brasao">🏛️</div><div>Painel de Despesas Públicas<small>Dados do Portal da Transparência</small></div></div>
<div class="links">
<a href="#inicio">Início</a>
<a href="#como-funciona">Como funciona</a>
<a href="#orgaos">Órgãos</a>
<a href="#consulta">Consultar</a>
<a href="#sobre">Sobre</a>
</div>
</div>
"""
)

html(
    f"""
<div id="inicio" class="hero" style="background-image:url('{img("hero")}')">
<div class="conteudo">
<h1>Saiba como o dinheiro público é gasto</h1>
<p>Consulte, de forma simples e gratuita, quanto cada ministério do Governo Federal empenhou e pagou em cada ano.</p>
<a class="botao" href="#consulta">Consultar despesas</a>
<a class="sec" href="#como-funciona">Como funciona</a>
</div>
</div>
"""
)

# ======================================================================
# COMO FUNCIONA
# ======================================================================
html(
    """
<div id="como-funciona" class="secao">
<div class="barra"></div>
<h2>Como funciona</h2>
<div class="sub">Três passos para acompanhar os gastos do Governo Federal.</div>
<div class="grid3">
<div class="passo"><div class="num">1</div><h3>Escolha o órgão</h3><p>Selecione o ministério que você quer acompanhar: Saúde, Educação, Defesa ou Justiça.</p></div>
<div class="passo"><div class="num">2</div><h3>Informe o ano</h3><p>Digite o ano da consulta com quatro dígitos. Os dados vêm direto da API oficial do governo.</p></div>
<div class="passo"><div class="num">3</div><h3>Veja os resultados</h3><p>Confira o total empenhado e pago, o ranking das entidades e baixe a planilha em CSV.</p></div>
</div>
</div>
"""
)

# ======================================================================
# ÓRGÃOS (cards com imagem)
# ======================================================================
cards = ""
for nome, (chave, descricao) in ORGAOS_INFO.items():
    cards += f"""
<div class="card">
<div class="foto" style="background-image:url('{img(chave)}'), linear-gradient(135deg, {AZUL}, {VERDE})"></div>
<div class="corpo"><h3>{nome}</h3><p>{descricao}</p><span class="codigo">Código SIAFI {ORGAOS[nome]}</span></div>
</div>"""

html(
    f"""
<div id="orgaos" class="secao">
<div class="barra"></div>
<h2>Órgãos disponíveis para consulta</h2>
<div class="sub">Escolha um dos ministérios abaixo no formulário de consulta.</div>
<div class="grid4">{cards}</div>
</div>
"""
)

# ======================================================================
# CONSULTA
# ======================================================================
html(
    f"""
<div id="consulta" class="secao"></div>
<div class="banner" style="background-image:url('{img("consulta")}')">
<div class="conteudo"><h2>Consulta de despesas</h2><p>Selecione o ano e o órgão para visualizar os valores empenhados e pagos.</p></div>
</div>
"""
)

with st.form("form_consulta"):
    col_ano, col_orgao = st.columns([1, 2])
    with col_ano:
        ano = st.text_input("Ano da consulta", value="2023", max_chars=4)
    with col_orgao:
        orgao_nome = st.selectbox("Órgão", list(ORGAOS.keys()))
    enviar = st.form_submit_button("🔍 Consultar despesas")

if enviar:
    st.session_state.pop("consulta", None)
    if len(ano) != 4 or not ano.isdigit():
        st.error("⚠️ Digite um ano válido com exatamente 4 números.")
    else:
        codigo_orgao = ORGAOS[orgao_nome]
        with st.spinner(f"Carregando dados de {ano} para {orgao_nome}..."):
            try:
                resultado = consultar_despesa_por_orgao(ano, codigo_orgao)
                st.session_state["consulta"] = {
                    "ano": ano,
                    "orgao": orgao_nome,
                    "resultado": resultado,
                }
            except Exception as e:
                st.error(f"Ocorreu um erro na requisição: {e}")

# ======================================================================
# RESULTADOS
# ======================================================================
consulta = st.session_state.get("consulta")

if consulta:
    resultado = consulta["resultado"]
    orgao_sel = consulta["orgao"]
    ano_sel = consulta["ano"]
    chave_img = ORGAOS_INFO[orgao_sel][0]

    if isinstance(resultado, list) and len(resultado) > 0:
        linhas = []
        for item in resultado:
            linhas.append(
                {
                    "Entidade": item.get("orgao", "Não informado"),
                    "Empenhado": para_float(item.get("empenhado", "0,00")),
                    "Pago": para_float(item.get("pago", "0,00")),
                }
            )
        df = pd.DataFrame(linhas)
        total_emp = df["Empenhado"].sum()
        total_pago = df["Pago"].sum()

        html(
            f"""
<div class="res-topo">
<div class="foto" style="background-image:url('{img(chave_img)}')"></div>
<div><h3>{orgao_sel}</h3><span>Despesas de {ano_sel} · {len(df)} entidades encontradas</span></div>
</div>
"""
        )

        k1, k2, k3 = st.columns(3)
        k1.markdown(
            f'<div class="kpi"><div class="rot">Total empenhado</div><div class="val">{brl_curto(total_emp)}</div><div class="det">{brl(total_emp)}</div></div>',
            unsafe_allow_html=True,
        )
        k2.markdown(
            f'<div class="kpi"><div class="rot">Total pago</div><div class="val">{brl_curto(total_pago)}</div><div class="det">{brl(total_pago)}</div></div>',
            unsafe_allow_html=True,
        )
        pct = (total_pago / total_emp * 100) if total_emp else 0
        k3.markdown(
            f'<div class="kpi"><div class="rot">Percentual pago do empenhado</div><div class="val">{pct:.1f}%'.replace(".", ",")
            + f'</div><div class="det">{len(df)} entidades</div></div>',
            unsafe_allow_html=True,
        )

        st.write("")
        aba_grafico, aba_detalhes, aba_tabela = st.tabs(
            ["📊 Maiores despesas", "🏢 Detalhamento por entidade", "📋 Tabela completa"]
        )

        with aba_grafico:
            st.subheader("10 entidades com maior valor pago")
            top = df.sort_values("Pago", ascending=False).head(10)
            longo = top.melt(
                id_vars="Entidade",
                value_vars=["Empenhado", "Pago"],
                var_name="Tipo",
                value_name="Valor",
            )
            longo["Valor formatado"] = longo["Valor"].apply(brl)
            usar_log = st.checkbox(
                "Escala logarítmica (facilita ver as entidades menores)", value=False
            )
            escala = alt.Scale(type="symlog") if usar_log else alt.Scale(type="linear")
            grafico = (
                alt.Chart(longo)
                .mark_bar()
                .encode(
                    y=alt.Y(
                        "Entidade:N",
                        sort=top["Entidade"].tolist(),
                        title=None,
                        axis=alt.Axis(labelLimit=420),
                    ),
                    yOffset=alt.YOffset("Tipo:N"),
                    x=alt.X("Valor:Q", scale=escala, title="Valor (R$)", axis=alt.Axis(
                            labelExpr=(
                                "datum.value >= 1e9 ? replace(format(datum.value / 1e9, '.1~f'), '.', ',') + ' bi' : "
                                "datum.value >= 1e6 ? replace(format(datum.value / 1e6, '.1~f'), '.', ',') + ' mi' : "
                                "datum.value >= 1e3 ? replace(format(datum.value / 1e3, '.1~f'), '.', ',') + ' mil' : "
                                "datum.value"
                            )
                        ),
                    ),
                    color=alt.Color(
                        "Tipo:N",
                        scale=alt.Scale(domain=["Empenhado", "Pago"], range=[AZUL, VERDE]),
                        legend=alt.Legend(orient="top", title=None),
                    ),
                    tooltip=["Entidade", "Tipo", "Valor formatado"],
                )
                .properties(height=max(300, 55 * len(top)))
            )
            st.altair_chart(grafico, use_container_width=True)

        with aba_detalhes:
            for _, linha in df.sort_values("Pago", ascending=False).iterrows():
                with st.expander(f"🏢 {linha['Entidade']}"):
                    m1, m2 = st.columns(2)
                    m1.metric("Valor Empenhado", brl(linha["Empenhado"]))
                    m2.metric("Valor Pago", brl(linha["Pago"]))

        with aba_tabela:
            tabela = df.sort_values("Pago", ascending=False).reset_index(drop=True)
            st.dataframe(
                tabela,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Empenhado": st.column_config.NumberColumn("Empenhado", format="R$ %.2f"),
                    "Pago": st.column_config.NumberColumn("Pago", format="R$ %.2f"),
                },
            )
            st.download_button(
                "⬇️ Baixar planilha (CSV)",
                data=tabela.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
                file_name=f"despesas_{ano_sel}_{chave_img}.csv",
                mime="text/csv",
            )

    elif isinstance(resultado, dict) and "Erro na API" in resultado:
        st.error(f"Erro na API: {resultado['Erro na API']}")
    else:
        st.warning("Nenhum registro encontrado para este ano e órgão.")

# ======================================================================
# SOBRE + RODAPÉ
# ======================================================================
html(
    f"""
<div id="sobre" class="secao">
<div class="sobre">
<div class="foto" style="background-image:url('{img("sobre")}'), linear-gradient(135deg, {AZUL}, {VERDE})"></div>
<div>
<div class="barra"></div>
<h2>Transparência é um direito de todos</h2>
<p>Este painel reúne informações de despesas públicas disponibilizadas pelo Portal da Transparência do Governo Federal. Os valores <b>empenhados</b> representam o que o governo reservou para um gasto, e os valores <b>pagos</b> mostram o que de fato foi desembolsado.</p>
<p>Todos os dados são consultados em tempo real na API oficial, sem alteração.</p>
</div>
</div>
</div>
<div class="rodape">
<div><b>Painel de Despesas Públicas</b><br>Consulta de despesas por órgão do Governo Federal.</div>
<div>Fonte dos dados<br><a href="https://portaldatransparencia.gov.br" target="_blank">portaldatransparencia.gov.br</a></div>
</div>
"""
)
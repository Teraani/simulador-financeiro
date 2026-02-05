import streamlit as st
import pandas as pd
import plotly.express as px

# ---------- CONFIG ----------
st.set_page_config(
    page_title="Simulador Financeiro", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# CSS para evitar quebra de layout e melhorar margens
st.markdown("""
    <style>
    .block-container { padding: 1rem 1rem; }
    [data-testid="stMetricValue"] { font-size: 1.6rem !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 Simulador Financeiro")

# ---------- FUNÇÕES ----------
def calcular_parcela(valor, parcelas, juro):
    if juro == 0: return valor / parcelas
    return valor * (juro * (1 + juro) ** parcelas) / ((1 + juro) ** parcelas - 1)

def calcular_cet_aproximado(valor_produto, parcela, qtd_parcelas):
    taxa = 0.0
    passo = 0.0001
    while taxa <= 0.2:
        vp = sum(parcela / ((1 + taxa) ** mes) for mes in range(1, qtd_parcelas + 1))
        if abs(vp - valor_produto) < 0.01:
            cet_m = taxa
            cet_a = (1 + cet_m) ** 12 - 1
            return cet_m * 100, cet_a * 100
        taxa += passo
    return 0.0, 0.0

def simular_parcelado(valor, parcelas, juros, rendimento):
    j, r = juros / 100, rendimento / 100
    v_parcela = calcular_parcela(valor, parcelas, j)
    saldo, dados = valor, []

    for mes in range(1, parcelas + 1):
        saldo_inicial = saldo
        rend_mes = saldo_inicial * r
        saldo_total = saldo_inicial + rend_mes
        saldo_final = saldo_total - v_parcela
        
        dados.append({
            "Mês": mes, 
            "Saldo inicial": round(saldo_inicial, 2),
            "Saldo final": round(saldo_final, 2)
        })
        saldo = saldo_final

    df = pd.DataFrame(dados)
    _, cet_a = calcular_cet_aproximado(valor, v_parcela, parcelas)
    return df, v_parcela, cet_a

# ---------- INPUTS ----------
with st.expander("⚙️ Configurar Dados", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        valor = st.number_input("Valor (R$)", min_value=0.0, value=10000.0, format="%.2f")
        parcelas = st.number_input("Parcelas", min_value=1, value=12, step=1)
    with col2:
        juros = st.number_input("Juros % mês", min_value=0.0, value=1.0, format="%.2f")
        rendimento = st.number_input("Rendimento % mês", min_value=0.0, value=1.0, format="%.2f")
    
    btn = st.button("📊 Simular", use_container_width=True, type="primary")

# ---------- RESULTADOS ----------
if btn:
    df, v_parcela, cet_a = simular_parcelado(valor, parcelas, juros, rendimento)
    
    m1, m2 = st.columns(2)
    m1.metric("Parcela", f"R$ {v_parcela:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    m2.metric("CET Anual", f"{cet_a:.2f}%")

    st.subheader("📉 Evolução do Saldo")
    
    fig = px.area(df, x="Mês", y="Saldo final", template="plotly_dark")
    
    # Ajustes de Margem e Eixos para evitar sobreposição
    fig.update_layout(
        xaxis = dict(
            tickmode = 'linear',
            tick0 = 1,
            dtick = 1,
            title=None,
            fixedrange=True
        ),
        yaxis=dict(
            tickformat=",.2f",
            title="Saldo (R$)",
            fixedrange=True,
            automargin=True # Isso empurra o gráfico para a direita para dar espaço aos números do Y
        ),
        margin=dict(l=50, r=20, t=20, b=50), # Aumentei a margem esquerda (l) e inferior (b)
        height=350,
        autosize=True,
        showlegend=False
    )

    fig.update_traces(
        hovertemplate="<b>Mês %{x}</b><br>Saldo: R$ %{y:,.2f}<extra></extra>".replace(",", "v").replace(".", ",").replace("v", "."),
        line_color="#29b5e8"
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # Adicionei a tabela logo abaixo para você conferir os números se o gráfico estiver pequeno
    with st.expander("📄 Ver Tabela Completa"):
        st.dataframe(df, use_container_width=True, hide_index=True)

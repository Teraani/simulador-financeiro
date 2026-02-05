import streamlit as st
import pandas as pd
import plotly.express as px

# ---------- CONFIG ----------
st.set_page_config(
    page_title="Simulador Financeiro", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Ajuste visual para mobile e Tooltip do Plotly
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    [data-testid="stMetricValue"] { font-size: 1.8rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 Simulador Financeiro")
st.caption("À vista vs Parcelado • CET • Farol Financeiro")

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
            "Rendimento": round(rend_mes, 2),
            "Saldo c/ rendimento": round(saldo_total, 2), 
            "Parcela": round(v_parcela, 2), 
            "Saldo final": round(saldo_final, 2)
        })
        saldo = saldo_final

    df = pd.DataFrame(dados)
    cet_m, cet_a = calcular_cet_aproximado(valor, v_parcela, parcelas)
    return df, v_parcela, v_parcela * parcelas, cet_a

# ---------- INPUTS ----------
with st.expander("⚙️ Configurar Dados da Compra", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        valor = st.number_input("Valor do Produto (R$)", min_value=0.0, value=10000.0, step=100.0, format="%.2f")
        parcelas = st.number_input("Qtd. Parcelas", min_value=1, value=12, step=1)
    with col2:
        juros = st.number_input("Juros % ao mês", min_value=0.0, value=1.0, step=0.1, format="%.2f")
        rendimento = st.number_input("Rendimento Inv. % mês", min_value=0.0, value=1.0, step=0.1, format="%.2f")
    
    btn_simular = st.button("📊 Calcular Simulação", use_container_width=True, type="primary")

# ---------- RESULTADOS ----------
if btn_simular:
    df, v_parcela, total_pago, cet_a = simular_parcelado(valor, parcelas, juros, rendimento)
    
    m1, m2 = st.columns(2)
    m1.metric("Parcela", f"R$ {v_parcela:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    m2.metric("CET Anual", f"{cet_a:.2f}%")

    # --- GRÁFICO OTIMIZADO (PLOTLY) ---
    st.subheader("📉 Evolução do Saldo")
    
    fig = px.area(
        df, 
        x="Mês", 
        y="Saldo final",
        labels={"Saldo final": "Saldo (R$)", "Mês": "Mês"},
        template="plotly_dark"
    )
    
    # Formatação do Balão (Hover) e Eixos no padrão BR
    fig.update_traces(
        hovertemplate="<b>Mês %{x}</b><br>Saldo: R$ %{y:,.2f}<extra></extra>".replace(",", "X").replace(".", ",").replace("X", "."),
        line_color="#29b5e8"
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=300,
        xaxis=dict(dtick=1), # Força mostrar todos os meses no eixo X
        yaxis=dict(tickformat=",.2f")
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # --- TABELA ---
    st.subheader("📅 Tabela Mensal")
    st.dataframe(
        df,
        column_config={
            "Mês": st.column_config.NumberColumn("Mês"),
            "Saldo inicial": st.column_config.NumberColumn("Início", format="R$ %.2f"),
            "Rendimento": st.column_config.NumberColumn("Rent.", format="R$ %.2f"),
            "Saldo c/ rendimento": st.column_config.NumberColumn("Total", format="R$ %.2f"),
            "Parcela": st.column_config.NumberColumn("Parcela", format="R$ %.2f"),
            "Saldo final": st.column_config.NumberColumn("Fim", format="R$ %.2f"),
        },
        hide_index=True, 
        use_container_width=True
    )

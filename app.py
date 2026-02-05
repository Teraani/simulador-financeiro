import streamlit as st
import pandas as pd

# ---------- CONFIG ----------
# initial_sidebar_state="collapsed" remove a seta lateral no mobile
st.set_page_config(page_title="Simulador Financeiro", layout="wide", initial_sidebar_state="collapsed")

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
            "Mês": mes, "Saldo inicial": saldo_inicial, "Rendimento": rend_mes,
            "Saldo c/ rendimento": saldo_total, "Parcela": -v_parcela, "Saldo final": saldo_final
        })
        saldo = saldo_final

    df = pd.DataFrame(dados)
    cet_m, cet_a = calcular_cet_aproximado(valor, v_parcela, parcelas)
    return df, v_parcela, v_parcela * parcelas, cet_a

# ---------- INPUTS BR ----------
with st.expander("⚙️ Configurar Dados da Compra", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        # format="%.2f" garante as casas decimais e o Streamlit usa o padrão do navegador para os pontos
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
        hide_index=True, use_container_width=True
    )

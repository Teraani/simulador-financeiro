import streamlit as st
import pandas as pd

# ---------- CONFIG ----------
st.set_page_config(page_title="Simulador Financeiro", layout="wide")

st.title("💰 Simulador Financeiro")
st.caption("À vista vs Parcelado • CET • Farol Financeiro")

# ---------- FUNÇÕES ----------
def calcular_parcela(valor, parcelas, juro):
    if juro == 0:
        return valor / parcelas
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
    j = juros / 100
    r = rendimento / 100
    parcela = calcular_parcela(valor, parcelas, j)
    saldo = valor
    dados = []

    for mes in range(1, parcelas + 1):
        saldo_inicial = saldo
        rendimento_mes = saldo_inicial * r
        saldo_com_rendimento = saldo_inicial + rendimento_mes
        saldo_final = saldo_com_rendimento - parcela
        
        dados.append({
            "Mês": mes,
            "Saldo inicial": saldo_inicial,
            "Rendimento": rendimento_mes,
            "Saldo c/ rendimento": saldo_com_rendimento,
            "Parcela": -parcela,
            "Saldo final": saldo_final
        })
        saldo = saldo_final

    df = pd.DataFrame(dados)
    total_pago = parcela * parcelas
    juros_totais = total_pago - valor
    cet_m, cet_a = calcular_cet_aproximado(valor, parcela, parcelas)
    return df, saldo, parcela, total_pago, juros_totais, cet_m, cet_a

def farol_financeiro(cet, rendimento):
    if cet <= rendimento:
        return "🟢 VERDE", "Crédito barato. Parcelar é vantajoso.", "success"
    elif cet <= rendimento * 1.2:
        return "🟡 AMARELO", "Parcelamento no limite. Avalie.", "warning"
    else:
        return "🔴 VERMELHO", "Crédito caro. Melhor evitar.", "error"

# ---------- INPUTS ----------
with st.sidebar:
    st.header("📌 Parâmetros")
    valor = st.number_input("Valor do Produto (R$)", min_value=0.0, value=10000.0, step=100.0)
    parcelas = st.number_input("Qtd. Parcelas", min_value=1, value=12, step=1)
    juros = st.number_input("Juros % ao mês", min_value=0.0, value=1.0, step=0.1)
    rendimento = st.number_input("Rendimento Inv. % mês", min_value=0.0, value=1.0, step=0.1)
    desconto = st.number_input("Desconto à vista %", min_value=0.0, value=5.0, step=1.0)
    btn_simular = st.button("📊 Simular Agora", use_container_width=True)

# ---------- EXECUÇÃO ----------
if btn_simular:
    df, sobra_p, v_parcela, total_pago, juros_totais, cet_m, cet_a = simular_parcelado(valor, parcelas, juros, rendimento)
    
    # Métricas de resumo superiores
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Parcela", f"R$ {v_parcela:,.2f}")
    m2.metric("Total Pago", f"R$ {total_pago:,.2f}")
    m3.metric("CET Anual", f"{cet_a:.2f}%")
    m4.metric("Juros Totais", f"R$ {juros_totais:,.2f}")

    st.divider()

    col_tab, col_info = st.columns([2, 1])

    with col_tab:
        st.subheader("📅 Fluxo de Caixa")
        # Tabela compacta e formatada
        st.dataframe(
            df,
            column_config={
                "Mês": st.column_config.NumberColumn("Mês", format="%d"),
                "Saldo inicial": st.column_config.NumberColumn("Início", format="R$ %.2f"),
                "Rendimento": st.column_config.NumberColumn("Rent.", format="R$ %.2f"),
                "Saldo c/ rendimento": st.column_config.NumberColumn("Total", format="R$ %.2f"),
                "Parcela": st.column_config.NumberColumn("Parcela", format="R$ %.2f"),
                "Saldo final": st.column_config.NumberColumn("Fim", format="R$ %.2f"),
            },
            hide_index=True,
            use_container_width=True,
            height=400 # Fixa a altura para não esticar a tela toda
        )

    with col_info:
        st.subheader("🚦 Análise")
        label, msg, tipo = farol_financeiro(cet_m, rendimento)
        if tipo == "success": st.success(f"**{label}**\n\n{msg}")
        elif tipo == "warning": st.warning(f"**{label}**\n\n{msg}")
        else: st.error(f"**{label}**\n\n{msg}")
        
        # Comparativo rápido
        economia_avista = valor * (1 - desconto/100)
        st.write(f"Custo à vista hoje: **R$ {economia_avista:,.2f}**")
        st.info("A tabela ao lado mostra como seu dinheiro rende enquanto você paga as parcelas mês a mês.")

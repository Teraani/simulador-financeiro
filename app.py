import streamlit as st
import pandas as pd

# ---------- CONFIG ----------
st.set_page_config(page_title="Simulador Financeiro", layout="wide")

# CSS personalizado para remover padding excessivo no mobile
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    </style>
    """, unsafe_allow_html=True)

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

# ---------- INPUTS (AGORA NO CORPO PRINCIPAL) ----------
with st.expander("⚙️ Configurar Dados da Compra", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        valor = st.number_input("Valor do Produto (R$)", min_value=0.0, value=10000.0, step=100.0)
        parcelas = st.number_input("Qtd. Parcelas", min_value=1, value=12, step=1)
        desconto = st.number_input("Desconto à vista %", min_value=0.0, value=5.0, step=1.0)
    with col2:
        juros = st.number_input("Juros % ao mês", min_value=0.0, value=1.0, step=0.1)
        rendimento = st.number_input("Rendimento Inv. % mês", min_value=0.0, value=1.0, step=0.1)
    
    btn_simular = st.button("📊 Calcular Simulação", use_container_width=True, type="primary")

# ---------- EXECUÇÃO ----------
if btn_simular:
    df, sobra_p, v_parcela, total_pago, juros_totais, cet_m, cet_a = simular_parcelado(valor, parcelas, juros, rendimento)
    
    st.subheader("📈 Resultado")
    
    # Métricas adaptáveis
    m1, m2 = st.columns(2)
    m1.metric("Parcela", f"R$ {v_parcela:,.2f}")
    m2.metric("CET Anual", f"{cet_a:.2f}%")
    
    m3, m4 = st.columns(2)
    m3.metric("Total Pago", f"R$ {total_pago:,.2f}")
    m4.metric("Juros Totais", f"R$ {juros_totais:,.2f}")

    st.divider()

    # Tabela com largura total e rolagem facilitada
    st.subheader("📅 Detalhamento Mensal")
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
        use_container_width=True
    )

    # Farol no final para fechamento da análise
    st.subheader("🚦 Veredito")
    label, msg, tipo = farol_financeiro(cet_m, rendimento)
    if tipo == "success": st.success(f"**{label}** - {msg}")
    elif tipo == "warning": st.warning(f"**{label}** - {msg}")
    else: st.error(f"**{label}** - {msg}")

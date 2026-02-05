import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador Financeiro", layout="centered")

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
    max_taxa = 0.2

    while taxa <= max_taxa:
        vp = sum(parcela / ((1 + taxa) ** mes) for mes in range(1, qtd_parcelas + 1))
        if abs(vp - valor_produto) < 0.01:
            cet_mensal = taxa
            cet_anual = (1 + cet_mensal) ** 12 - 1
            return cet_mensal * 100, cet_anual * 100
        taxa += passo

    return None, None

def simular_parcelado(valor, parcelas, juros, rendimento):
    j = juros / 100
    r = rendimento / 100

    parcela = calcular_parcela(valor, parcelas, j)
    saldo = valor
    dados = []

    for mes in range(1, parcelas + 1):
        rendimento_mes = saldo * r
        saldo = saldo + rendimento_mes - parcela
        dados.append([mes, rendimento_mes, -parcela, saldo])

    df = pd.DataFrame(
        dados,
        columns=["Mês", "Rendimento", "Parcela", "Saldo Final"]
    )

    total_pago = parcela * parcelas
    juros_totais = total_pago - valor
    cet_m, cet_a = calcular_cet_aproximado(valor, parcela, parcelas)

    return df, saldo, parcela, total_pago, juros_totais, cet_m, cet_a

def simular_avista(valor, desconto, parcelas, rendimento):
    economia = valor * (desconto / 100)
    r = rendimento / 100
    return economia * ((1 + r) ** parcelas)

def farol_financeiro(cet, rendimento):
    if cet <= rendimento:
        return "🟢 FAROL VERDE", "Crédito barato. Parcelar é financeiramente vantajoso."
    elif cet <= rendimento * 1.2:
        return "🟡 FAROL AMARELO", "Parcelamento no limite. Avalie com cautela."
    else:
        return "🔴 FAROL VERMELHO", "Crédito caro. Financeiramente desvantajoso parcelar."

# ---------- INPUTS ----------
st.subheader("📌 Dados da compra")

valor = st.number_input("Valor do produto (R$)", min_value=0.0, step=100.0)
st.caption(f"Valor informado: R$ {valor:,.2f}")
parcelas = st.number_input("Quantidade de parcelas", min_value=1, step=1)
juros = st.number_input("Juros do parcelamento (% ao mês)", min_value=0.0, step=0.1)
rendimento = st.number_input("Rendimento do investimento (% ao mês)", min_value=0.0, step=0.1)
desconto = st.number_input("Desconto à vista (%)", min_value=0.0, step=1.0)

if st.button("📊 Simular"):
    df, sobra_parcelado, parcela, total_pago, juros_totais, cet_m, cet_a = (
        simular_parcelado(valor, parcelas, juros, rendimento)
    )
    sobra_avista = simular_avista(valor, desconto, parcelas, rendimento)

    st.subheader("📈 Resultado do Parcelamento")
    st.write(f"**Parcela mensal:** R$ {parcela:,.2f}")
    st.write(f"**Total pago:** R$ {total_pago:,.2f}")
    st.write(f"**Juros totais:** R$ {juros_totais:,.2f}")
    st.write(f"**CET mensal:** {cet_m:.2f}%")
    st.write(f"**CET anual:** {cet_a:.2f}%")

    st.dataframe(df, use_container_width=True)

    st.subheader("⚖️ Comparação Final")
    st.write(f"Parcelado + investimento: **R$ {sobra_parcelado:,.2f}**")
    st.write(f"À vista + investimento: **R$ {sobra_avista:,.2f}**")

    if sobra_avista > sobra_parcelado:
        st.success(f"🏆 À VISTA é melhor por R$ {sobra_avista - sobra_parcelado:,.2f}")
    else:
        st.warning(f"🏆 PARCELAR é melhor por R$ {sobra_parcelado - sobra_avista:,.2f}")

    farol, msg = farol_financeiro(cet_m, rendimento)
    st.subheader("🚦 Farol Financeiro")
    st.info(f"{farol}\n\n{msg}")



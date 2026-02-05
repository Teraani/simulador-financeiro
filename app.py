import streamlit as st
import pandas as pd

# ---------- CONFIG ----------
st.set_page_config(page_title="Simulador Financeiro", layout="wide")

st.title("💰 Simulador Financeiro")
st.caption("À vista vs Parcelado • CET • Farol Financeiro")

# ---------- FORMATADOR BR ----------
def moeda_br(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

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

        dados.append([
            mes,
            saldo_inicial,
            rendimento_mes,
            saldo_com_rendimento,
            -parcela,
            saldo_final
        ])

        saldo = saldo_final

    df = pd.DataFrame(
        dados,
        columns=[
            "Mês",
            "Saldo inicial",
            "Rendimento",
            "Saldo c/ rendimento",
            "Parcela",
            "Saldo final"
        ]
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
        return "🟢 FAROL VERDE", "Crédito barato. Parcelar é vantajoso."
    elif cet <= rendimento * 1.2:
        return "🟡 FAROL AMARELO", "Parcelamento no limite. Avalie."
    else:
        return "🔴 FAROL VERMELHO", "Crédito caro. Melhor evitar."

# ---------- INPUTS ----------
st.subheader("📌 Dados da compra")

col1, col2, col3 = st.columns(3)

with col1:
    valor = st.number_input("Valor (R$)", min_value=0.0, step=100.0)
    parcelas = st.number_input("Parcelas", min_value=1, step=1)

with col2:
    juros = st.number_input("Juros % mês", min_value=0.0, step=0.1)
    rendimento = st.number_input("Rendimento % mês", min_value=0.0, step=0.1)

with col3:
    desconto = st.number_input("Desconto à vista %", min_value=0.0, step=1.0)

# ---------- EXECUÇÃO ----------
if st.button("📊 Simular"):

    df, sobra_parcelado, parcela, total_pago, juros_totais, cet_m, cet_a = (
        simular_parcelado(valor, parcelas, juros, rendimento)
    )

    sobra_avista = simular_avista(valor, desconto, parcelas, rendimento)

    # formatação BR
    df_formatado = df.copy()
    for col in df.columns[1:]:
        df_formatado[col] = df[col].apply(moeda_br)

    # estilo compactado
    styled = (
        df_formatado.style
        .set_properties(**{
            "text-align": "right",
            "white-space": "nowrap"
        })
    )

    st.subheader("📈 Resultado")

    st.write(f"Parcela: **{moeda_br(parcela)}**")
    st.write(f"Total pago: **{moeda_br(total_pago)}**")
    st.write(f"Juros: **{moeda_br(juros_totais)}**")
    st.write(f"CET mensal: **{cet_m:.2f}%**")
    st.write(f"CET anual: **{cet_a:.2f}%**")

    st.info("Simulação considerando o valor investido enquanto paga as parcelas.")

    # 👉 tabela estilo Excel compacta
    st.table(styled)

    st.subheader("⚖️ Comparação")

    st.write(f"Parcelado: **{moeda_br(sobra_parcelado)}**")
    st.write(f"À vista: **{moeda_br(sobra_avista)}**")

    if sobra_avista > sobra_parcelado:
        st.success(f"À vista melhor por {moeda_br(sobra_avista - sobra_parcelado)}")
    else:
        st.warning(f"Parcelar melhor por {moeda_br(sobra_parcelado - sobra_avista)}")

    farol, msg = farol_financeiro(cet_m, rendimento)

    st.subheader("🚦 Farol Financeiro")
    st.info(f"{farol}\n\n{msg}")

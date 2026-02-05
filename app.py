import streamlit as st
import pandas as pd

# ---------- CONFIG ----------
st.set_page_config(
    page_title="Simulador Financeiro", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# CSS para ajuste mobile
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    [data-testid="stMetricValue"] { font-size: 1.6rem !important; }
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

def fmt_br(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ---------- INPUTS ----------
with st.expander("⚙️ Configurar Dados da Compra", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        valor = st.number_input("Valor do Produto (R$)", min_value=0.0, value=10000.0, step=100.0, format="%.2f")
        parcelas = st.number_input("Qtd. Parcelas", min_value=1, value=12, step=1)
        desconto_vista = st.number_input("Desconto à vista %", min_value=0.0, value=5.0, step=1.0, format="%.2f")
    with col2:
        juros = st.number_input("Juros % ao mês", min_value=0.0, value=1.0, step=0.1, format="%.2f")
        rendimento = st.number_input("Rendimento Inv. % mês", min_value=0.0, value=1.0, step=0.1, format="%.2f")
    
    btn_simular = st.button("📊 Calcular Simulação", use_container_width=True, type="primary")

# ---------- EXECUÇÃO ----------
if btn_simular:
    df, sobra_p, v_parcela, total_pago, juros_totais, cet_m, cet_a = simular_parcelado(valor, parcelas, juros, rendimento)
    
    # Cálculo Comparativo à Vista
    valor_a_vista = valor * (1 - desconto_vista / 100)
    # Se pagar à vista, quanto esse dinheiro renderia no mesmo período das parcelas?
    rendimento_acumulado_vista = valor_a_vista * ((1 + rendimento/100) ** parcelas)
    
    st.subheader("📈 Resultado")
    
    m1, m2 = st.columns(2)
    m1.metric("Parcela", fmt_br(v_parcela))
    m2.metric("CET Anual", f"{cet_a:.2f}%")
    
    m3, m4 = st.columns(2)
    m3.metric("Total Pago", fmt_br(total_pago))
    m4.metric("Custo à Vista", fmt_br(valor_a_vista))

    st.divider()

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

    # ---------- VEREDITO COMPARATIVO ----------
    st.subheader("🚦 Veredito")
    
    # Lógica: Se sobrar mais dinheiro no parcelado do que o valor à vista renderia sozinho
    if sobra_p > 0:
        lucro_parcelado = sobra_p
        st.success(f"**🟢 PARCELE!** Ao final de {parcelas} meses, você ainda terá **{fmt_br(lucro_parcelado)}** na conta rendendo. O parcelamento custa menos que seu rendimento mensal.")
    else:
        prejuizo = abs(sobra_p)
        st.error(f"**🔴 PAGUE À VISTA!** Parcelar fará você perder **{fmt_br(prejuizo)}** em relação ao seu capital inicial. O desconto de {desconto_vista:.1f}% vale mais que o rendimento do período.")

    with st.expander("ℹ️ Entenda a análise"):
        st.write(f"""
        - Se você **parcelar**, começa com {fmt_br(valor)} e termina com **{fmt_br(sobra_p if sobra_p > 0 else 0)}** após pagar todas as parcelas.
        - Se você pagar **à vista**, gasta {fmt_br(valor_a_vista)} agora.
        - A comparação considera se o juros embutido nas parcelas ({cet_m:.2f}% ao mês) é maior que o seu rendimento ({rendimento:.2f}% ao mês).
        """)

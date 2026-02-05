import streamlit as st
import pandas as pd

# ---------- CONFIG ----------
st.set_page_config(
    page_title="Simulador Financeiro Pro", 
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

st.title("💰 Simulador Financeiro + Inflação")
st.caption("Análise Real do Poder de Compra • À vista vs Parcelado")

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

def fmt_br(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ---------- INPUTS ----------
with st.expander("⚙️ Configurar Dados Reais", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        valor = st.number_input("Valor do Produto (R$)", min_value=0.0, value=10000.0, step=100.0, format="%.2f")
        parcelas = st.number_input("Qtd. Parcelas", min_value=1, value=12, step=1)
        desconto_vista = st.number_input("Desconto à vista %", min_value=0.0, value=5.0, step=1.0, format="%.2f")
    with col2:
        juros = st.number_input("Juros % ao mês", min_value=0.0, value=1.0, step=0.1, format="%.2f")
        rendimento = st.number_input("Rendimento Inv. % mês", min_value=0.0, value=1.0, step=0.1, format="%.2f")
        inflacao = st.number_input("Inflação % mês (IPCA/IGP-M)", min_value=0.0, value=0.4, step=0.05, format="%.2f")
    
    btn_simular = st.button("📊 Calcular Simulação Real", use_container_width=True, type="primary")

# ---------- EXECUÇÃO ----------
if btn_simular:
    j, r, inf = juros/100, rendimento/100, inflacao/100
    v_parcela = calcular_parcela(valor, parcelas, j)
    valor_a_vista = valor * (1 - desconto_vista / 100)
    
    saldo, dados = valor, []
    ganho_inflacao_total = 0

    for mes in range(1, parcelas + 1):
        saldo_inicial = saldo
        rend_mes = saldo_inicial * r
        saldo_final = (saldo_inicial + rend_mes) - v_parcela
        
        # Valor da parcela corrigido pela inflação (quanto ela vale 'hoje')
        parcela_real = v_parcela / ((1 + inf) ** mes)
        economia_inflacao = v_parcela - parcela_real
        ganho_inflacao_total += economia_inflacao
        
        dados.append({
            "Mês": mes,
            "Saldo final": saldo_final,
            "Parcela": v_parcela,
            "Valor Real (Poder de Compra)": parcela_real
        })
        saldo = saldo_final

    df = pd.DataFrame(dados)
    cet_m, cet_a = calcular_cet_aproximado(valor, v_parcela, parcelas)

    # ---------- EXIBIÇÃO ----------
    st.subheader("📈 Métricas Financeiras")
    m1, m2, m3 = st.columns(3)
    m1.metric("Parcela Mensal", fmt_br(v_parcela))
    m2.metric("CET Anual", f"{cet_a:.2f}%")
    m3.metric("Ganho vs Inflação", fmt_br(ganho_inflacao_total), help="O quanto você 'ganhou' porque as parcelas futuras valem menos que a de hoje.")

    st.divider()

    st.subheader("📅 Tabela de Evolução Real")
    st.dataframe(
        df,
        column_config={
            "Mês": st.column_config.NumberColumn("Mês"),
            "Saldo final": st.column_config.NumberColumn("Saldo Acumulado", format="R$ %.2f"),
            "Parcela": st.column_config.NumberColumn("Parcela Fixa", format="R$ %.2f"),
            "Valor Real (Poder de Compra)": st.column_config.ProgressColumn("Poder de Compra da Parcela", help="Quanto menor a barra, mais 'barata' a parcela ficou devido à inflação", format="R$ %.2f", min_value=0, max_value=v_parcela)
        },
        hide_index=True, use_container_width=True
    )

    st.subheader("🚦 Veredito Final")
    # Comparação final: Sobra do parcelado vs Custo à vista
    if saldo > 0:
        st.success(f"**🟢 PARCELE!** O seu rendimento mensal de {rendimento:.2f}% supera o custo do parcelamento. Além disso, a inflação fará a última parcela custar apenas {fmt_br(df.iloc[-1]['Valor Real (Poder de Compra)'])} em valores de hoje.")
    else:
        st.error(f"**🔴 PAGUE À VISTA!** Mesmo com a inflação ajudando, o desconto de {desconto_vista:.1f}% ou os juros de {juros:.2f}% tornam a compra à vista mais barata no final.")

    with st.expander("📝 Entenda a lógica da Inflação"):
        st.write(f"""
        1. **Parcela Fixa:** Você paga sempre {fmt_br(v_parcela)}.
        2. **Corrosão da Moeda:** Com uma inflação de {inflacao:.2f}% ao mês, o dinheiro perde valor. 
        3. **Vantagem:** A parcela do mês {parcelas} parece igual, mas ela 'pesa' menos no seu bolso do que a primeira parcela.
        """)

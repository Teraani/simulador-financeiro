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
            "Rendimento do mês",
            "Saldo com rendimento",
            "Pagamento da parcela",
            "Saldo final"
        ]
    )

    total_pago = parcela * parcelas
    juros_totais = total_pago - valor
    cet_m, cet_a = calcular_cet_aproximado(valor, parcela, parcelas)

    return df, saldo, parcela, total_pago, juros_totais, cet_m, cet_a

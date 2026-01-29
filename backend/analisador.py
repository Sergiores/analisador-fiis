"""Aplicação do Método SRS FI."""
from typing import Dict

class AnalisadorSRS:
    """Aplica o Método SRS FI a um fundo."""

    def analisar(self, metricas: Dict) -> Dict:
        """Analisa um fundo usando o Método SRS FI."""
        criterios = []
        aprovado_geral = True
        metricas_faltantes = []

        # P/VP
        if metricas.get("p_vp"):
            criterio = {
                "nome": "P/VP",
                "valor": round(metricas["p_vp"], 2),
                "min_valor": 0.65,
                "max_valor": 1.02,
                "aprovado": 0.65 <= metricas["p_vp"] <= 1.02
            }
            criterios.append(criterio)
            aprovado_geral = aprovado_geral and criterio["aprovado"]
        else:
            metricas_faltantes.append("P/VP (Preço/Valor Patrimonial)")

        # Dividend Yield
        if metricas.get("dividend_yield"):
            criterio = {
                "nome": "Dividend Yield (%a.a.)",
                "valor": round(metricas["dividend_yield"], 2),
                "min_valor": 10.2,
                "max_valor": 100,
                "aprovado": metricas["dividend_yield"] >= 10.2
            }
            criterios.append(criterio)
            aprovado_geral = aprovado_geral and criterio["aprovado"]
        else:
            metricas_faltantes.append("Dividend Yield (DY 12 meses)")

        # Vacância
        if metricas.get("vacancia") is not None:
            criterio = {
                "nome": "Vacância (%)",
                "valor": round(metricas["vacancia"], 2),
                "min_valor": 0,
                "max_valor": 4,
                "aprovado": metricas["vacancia"] < 4
            }
            criterios.append(criterio)
            aprovado_geral = aprovado_geral and criterio["aprovado"]
        else:
            metricas_faltantes.append("Vacância Física")

        # Liquidez
        if metricas.get("liquidez_diaria"):
            liquidez_mm = metricas["liquidez_diaria"] / 1_000_000
            criterio = {
                "nome": "Liquidez Diária (R$ MM)",
                "valor": round(liquidez_mm, 2),
                "min_valor": 2.5,
                "max_valor": 999999,
                "aprovado": liquidez_mm >= 2.5
            }
            criterios.append(criterio)
            aprovado_geral = aprovado_geral and criterio["aprovado"]
        else:
            metricas_faltantes.append("Liquidez Diária")

        # Determina recomendação
        criterios_aprovados = len([c for c in criterios if c["aprovado"]])

        if aprovado_geral and len(criterios) == 4:
            recomendacao = "COMPRA"
            nota = 9.0
        elif criterios_aprovados >= 3:
            recomendacao = "COMPRA COM RESSALVAS"
            nota = 7.5
        elif criterios_aprovados >= 2:
            recomendacao = "ANÁLISE ADICIONAL NECESSÁRIA"
            nota = 6.0
        else:
            recomendacao = "NÃO RECOMENDADO"
            nota = 5.0

        resultado = {
            "ticker": metricas.get("ticker", "Desconhecido"),
            "aprovado": aprovado_geral,
            "recomendacao": recomendacao,
            "nota": nota,
            "criterios": criterios,
            "metricas": metricas
        }

        # Adiciona informação sobre métricas faltantes
        if metricas_faltantes:
            resultado["metricas_faltantes"] = metricas_faltantes

        return resultado

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


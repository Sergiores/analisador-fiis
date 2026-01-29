"""Aplicação do Método SRS FI."""
from typing import Dict
from dataclasses import dataclass

@dataclass
class CriterioSRS:
    """Representa um critério do Método SRS FI."""
    nome: str
    valor: float
    min_valor: float
    max_valor: float
    aprovado: bool = False

    def __post_init__(self):
        self.aprovado = self.min_valor <= self.valor <= self.max_valor

class AnalisadorSRS:
    """Aplica o Método SRS FI a um fundo."""

    def analisar(self, metricas: Dict) -> Dict:
        """Analisa um fundo usando o Método SRS FI."""
        criterios = []
        aprovado_geral = True

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

        # Dividend Yield
        if metricas.get("dividend_yield"):
            criterio = {
                "nome": "Dividend Yield",
                "valor": round(metricas["dividend_yield"], 2),
                "min_valor": 10.2,
                "max_valor": 100,
                "aprovado": metricas["dividend_yield"] >= 10.2
            }
            criterios.append(criterio)
            aprovado_geral = aprovado_geral and criterio["aprovado"]

        # Vacância
        if metricas.get("vacancia") is not None:
            criterio = {
                "nome": "Vacância",
                "valor": round(metricas["vacancia"], 2),
                "min_valor": 0,
                "max_valor": 4,
                "aprovado": metricas["vacancia"] < 4
            }
            criterios.append(criterio)
            aprovado_geral = aprovado_geral and criterio["aprovado"]

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

        # Determina recomendação
        criterios_aprovados = len([c for c in criterios if c["aprovado"]])

        if aprovado_geral and len(criterios) == 4:
            recomendacao = "COMPRA"
            nota = 9.0
        elif criterios_aprovados >= 3:
            recomendacao = "COMPRA COM RESSALVAS"
            nota = 7.5
        else:
            recomendacao = "NÃO RECOMENDADO"
            nota = 5.0

        return {
            "ticker": metricas.get("ticker", "Desconhecido"),
            "aprovado": aprovado_geral,
            "recomendacao": recomendacao,
            "nota": nota,
            "criterios": criterios,
            "metricas": metricas
        }

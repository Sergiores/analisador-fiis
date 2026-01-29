"""Extrator de dados de PDFs de Relatórios de Investimento."""
import pdfplumber
import re
from typing import Dict, Optional

class ExtratorRI:
    """Extrai métricas de um Relatório de Investimento em PDF."""

    @staticmethod
    def extrair_texto(caminho_pdf: str) -> str:
        """Extrai todo o texto do PDF."""
        texto_completo = ""
        try:
            with pdfplumber.open(caminho_pdf) as pdf:
                for pagina in pdf.pages:
                    texto = pagina.extract_text()
                    if texto:
                        texto_completo += texto + "\n"
        except Exception as e:
            print(f"Erro ao extrair texto: {e}")
        return texto_completo

    @staticmethod
    def extrair_valor(texto: str, padroes: list) -> Optional[float]:
        """Extrai um valor numérico usando múltiplos padrões regex."""
        try:
            for padrao in padroes:
                # Busca por padrões como "R$ 1.234,56" ou "1.234,56" ou "12,34%"
                matches = re.finditer(
                    rf"{padrao}[:\s]*R?\$?\s*([\d.,]+)\s*%?",
                    texto,
                    re.IGNORECASE | re.MULTILINE
                )

                for match in matches:
                    valor_str = match.group(1)
                    # Remove pontos de milhar e substitui vírgula por ponto
                    valor_str = valor_str.replace(".", "").replace(",", ".")
                    try:
                        valor = float(valor_str)
                        # Valida se o valor faz sentido (não é muito grande nem muito pequeno)
                        if 0 < valor < 1_000_000_000:
                            return valor
                    except ValueError:
                        continue
        except Exception as e:
            print(f"Erro ao extrair valor: {e}")
        return None

    def extrair_metricas(self, caminho_pdf: str) -> Dict:
        """Extrai as principais métricas do RI."""
        texto = self.extrair_texto(caminho_pdf)

        # Verifica se é um Fato Relevante
        if "FATO RELEVANTE" in texto.upper() and "EMISSÃO DE COTAS" in texto.upper():
            return {
                "erro": "fato_relevante",
                "mensagem": "Este documento é um Fato Relevante sobre emissão de cotas, não um Relatório de Investimento completo. Por favor, faça upload do Relatório Gerencial ou Informe Mensal do fundo."
            }

        # Tenta identificar o ticker do fundo
        ticker_match = re.search(r"\b([A-Z]{4}\d{2})\b", texto)
        ticker = ticker_match.group(1) if ticker_match else "Desconhecido"

        # Extrai métricas com múltiplos padrões
        patrimonio_liquido = self.extrair_valor(texto, [
            r"Patrim[oô]nio\s+L[ií]quido",
            r"PL\s+do\s+Fundo",
            r"Valor\s+do\s+Patrim[oô]nio",
            r"PL\s+Total"
        ])

        valor_patrimonial = self.extrair_valor(texto, [
            r"Valor\s+Patrimonial\s+da\s+Cota",
            r"VP\s+da\s+Cota",
            r"Cota\s+Patrimonial",
            r"Valor\s+Patrimonial\s+por\s+Cota",
            r"VP\s+por\s+Cota"
        ])

        preco_mercado = self.extrair_valor(texto, [
            r"Pre[çc]o\s+de\s+Mercado",
            r"Cota[çã]o",
            r"Pre[çc]o\s+de\s+Fechamento",
            r"Valor\s+de\s+Mercado\s+da\s+Cota",
            r"Pre[çc]o\s+M[ée]dio"
        ])

        dividend_yield = self.extrair_valor(texto, [
            r"Dividend\s+Yield\s+12\s*m",
            r"DY\s+12\s*meses",
            r"DY\s+Anual",
            r"Rendimento\s+12\s*m",
            r"DY\s+|$12m$|",
            r"Dividend\s+Yield\s+Anualizado"
        ])

        vacancia = self.extrair_valor(texto, [
            r"Vac[aâ]ncia\s+F[ií]sica",
            r"Vac[aâ]ncia\s+Financeira",
            r"Taxa\s+de\s+Vac[aâ]ncia",
            r"Vac[aâ]ncia\s+Total",
            r"Vac[aâ]ncia[:\s]+"
        ])

        liquidez_diaria = self.extrair_valor(texto, [
            r"Liquidez\s+Di[aá]ria",
            r"Liquidez\s+M[ée]dia\s+Di[aá]ria",
            r"Volume\s+M[ée]dio\s+Di[aá]rio",
            r"Volume\s+Di[aá]rio"
        ])

        metricas = {
            "ticker": ticker,
            "patrimonio_liquido": patrimonio_liquido,
            "valor_patrimonial": valor_patrimonial,
            "preco_mercado": preco_mercado,
            "dividend_yield": dividend_yield,
            "vacancia": vacancia if vacancia is not None else 0,  # Assume 0 se não encontrar
            "liquidez_diaria": liquidez_diaria,
        }

        # Calcula P/VP
        if preco_mercado and valor_patrimonial and valor_patrimonial > 0:
            metricas["p_vp"] = preco_mercado / valor_patrimonial
        else:
            metricas["p_vp"] = None

        # Verifica se conseguiu extrair métricas suficientes
        metricas_essenciais = [
            metricas.get("p_vp"),
            metricas.get("dividend_yield"),
            metricas.get("liquidez_diaria")
        ]

        metricas_encontradas = sum(1 for m in metricas_essenciais if m is not None)

        if metricas_encontradas < 2:
            metricas["erro"] = "metricas_insuficientes"
            metricas["mensagem"] = f"Não foi possível extrair métricas suficientes do documento. Apenas {metricas_encontradas} de 3 métricas essenciais foram encontradas. Certifique-se de que o PDF é um Relatório de Investimento completo com P/VP, Dividend Yield e Liquidez."

        return metricas

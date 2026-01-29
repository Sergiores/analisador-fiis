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
    def extrair_valor(texto: str, padrao: str) -> Optional[float]:
        """Extrai um valor numérico usando regex."""
        try:
            # Padrões comuns: "R$ 1.234,56" ou "1.234,56" ou "12,34%"
            match = re.search(
                rf"{padrao}[:\s]*R?\$?\s*([\d.,]+)\s*%?",
                texto,
                re.IGNORECASE
            )
            if match:
                valor_str = match.group(1)
                # Converte formato brasileiro para float
                valor_str = valor_str.replace(".", "").replace(",", ".")
                return float(valor_str)
        except Exception as e:
            print(f"Erro ao extrair valor '{padrao}': {e}")
        return None

    def extrair_metricas(self, caminho_pdf: str) -> Dict:
        """Extrai as principais métricas do RI."""
        texto = self.extrair_texto(caminho_pdf)

        # Tenta identificar o ticker do fundo
        ticker_match = re.search(r"\b([A-Z]{4}\d{2})\b", texto)
        ticker = ticker_match.group(1) if ticker_match else "Desconhecido"

        # Extrai métricas principais
        metricas = {
            "ticker": ticker,
            "patrimonio_liquido": self.extrair_valor(texto, r"Patrim[oô]nio\s+L[ií]quido"),
            "valor_patrimonial": self.extrair_valor(texto, r"Valor\s+Patrimonial|VP|Cota\s+Patrimonial"),
            "preco_mercado": self.extrair_valor(texto, r"Pre[çc]o\s+de\s+Mercado|Cota[çã]o"),
            "dividend_yield": self.extrair_valor(texto, r"Dividend\s+Yield|DY\s+12\s*m"),
            "vacancia": self.extrair_valor(texto, r"Vac[aâ]ncia"),
            "liquidez_diaria": self.extrair_valor(texto, r"Liquidez\s+Di[aá]ria|Liquidez\s+M[ée]dia"),
        }

        # Calcula P/VP se possível
        if metricas["preco_mercado"] and metricas["valor_patrimonial"]:
            metricas["p_vp"] = metricas["preco_mercado"] / metricas["valor_patrimonial"]
        else:
            metricas["p_vp"] = None

        return metricas

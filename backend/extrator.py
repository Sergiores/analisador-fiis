"""Extrator de dados de PDFs de Relatórios de Investimento."""
import pdfplumber
import re
from typing import Dict, Optional, List

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
    def identificar_ticker(texto: str) -> str:
        """Identifica o ticker do fundo no texto."""
        # Busca por padrões de ticker (4 letras + 2 números)
        matches = re.findall(r"\b([A-Z]{4}\d{2})\b", texto)

        if matches:
            # Pega o ticker que mais aparece
            from collections import Counter
            ticker_counts = Counter(matches)
            ticker_mais_comum = ticker_counts.most_common(1)[0][0]
            return ticker_mais_comum

        return "Desconhecido"

    @staticmethod
    def extrair_valor(texto: str, padroes: List[str]) -> Optional[float]:
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
                        if 0 < valor < 1_000_000_000_000:
                            return valor
                    except ValueError:
                        continue
        except Exception as e:
            print(f"Erro ao extrair valor com padrões {padroes}: {e}")
        return None

    def identificar_tipo_documento(self, texto: str) -> str:
        """Identifica o tipo de documento."""
        texto_upper = texto.upper()

        if "FATO RELEVANTE" in texto_upper and "EMISSÃO" in texto_upper:
            return "fato_relevante"
        elif "RELATÓRIO GERENCIAL" in texto_upper or "RELATORIO GERENCIAL" in texto_upper:
            return "relatorio_gerencial"
        elif "INFORME MENSAL" in texto_upper:
            return "informe_mensal"
        elif "RELATÓRIO DO ADMINISTRADOR" in texto_upper or "RELATORIO DO ADMINISTRADOR" in texto_upper:
            return "relatorio_administrador"
        elif "LÂMINA" in texto_upper or "LAMINA" in texto_upper:
            return "lamina"
        else:
            return "desconhecido"

    def extrair_metricas(self, caminho_pdf: str) -> Dict:
        """Extrai as principais métricas do RI."""
        texto = self.extrair_texto(caminho_pdf)

        # Identifica tipo de documento
        tipo_doc = self.identificar_tipo_documento(texto)

        # Verifica se é um Fato Relevante (não serve para análise)
        if tipo_doc == "fato_relevante":
            return {
                "erro": "fato_relevante",
                "mensagem": "Este documento é um Fato Relevante, não um Relatório de Investimento completo. Por favor, faça upload de um Relatório Gerencial, Informe Mensal ou Lâmina do fundo."
            }

        # Identifica o ticker do fundo
        ticker = self.identificar_ticker(texto)

        print(f"Analisando documento do tipo: {tipo_doc}")
        print(f"Ticker identificado: {ticker}")

        # Extrai métricas com múltiplos padrões
        patrimonio_liquido = self.extrair_valor(texto, [
            r"Patrim[oô]nio\s+L[ií]quido",
            r"PL\s+do\s+Fundo",
            r"Valor\s+do\s+Patrim[oô]nio",
            r"PL\s+Total",
            r"Patrimônio\s+Líquido\s+Total"
        ])

        valor_patrimonial = self.extrair_valor(texto, [
            r"Valor\s+Patrimonial\s+da\s+Cota",
            r"VP\s+da\s+Cota",
            r"Cota\s+Patrimonial",
            r"Valor\s+Patrimonial\s+por\s+Cota",
            r"VP\s+por\s+Cota",
            r"Valor\s+da\s+Cota\s+Patrimonial"
        ])

        preco_mercado = self.extrair_valor(texto, [
            r"Pre[çc]o\s+de\s+Mercado",
            r"Cota[çã]o",
            r"Pre[çc]o\s+de\s+Fechamento",
            r"Valor\s+de\s+Mercado\s+da\s+Cota",
            r"Pre[çc]o\s+M[ée]dio",
            r"Cota[çã]o\s+M[ée]dia",
            r"Pre[çc]o\s+da\s+Cota"
        ])

        dividend_yield = self.extrair_valor(texto, [
            r"Dividend\s+Yield\s+12\s*m",
            r"DY\s+12\s*meses",
            r"DY\s+Anual",
            r"Rendimento\s+12\s*m",
            r"DY\s+|$12m$|",
            r"Dividend\s+Yield\s+Anualizado",
            r"DY\s+12M",
            r"Dividend\s+Yield\s+|$12\s*meses$|"
        ])

        vacancia = self.extrair_valor(texto, [
            r"Vac[aâ]ncia\s+F[ií]sica",
            r"Vac[aâ]ncia\s+Financeira",
            r"Taxa\s+de\s+Vac[aâ]ncia",
            r"Vac[aâ]ncia\s+Total",
            r"Vac[aâ]ncia[:\s]+",
            r"Índice\s+de\s+Vac[aâ]ncia"
        ])

        # Para fundos de papel (CRI/CRA), buscar inadimplência
        inadimplencia = self.extrair_valor(texto, [
            r"Inadimpl[eê]ncia",
            r"Taxa\s+de\s+Inadimpl[eê]ncia",
            r"Índice\s+de\s+Inadimpl[eê]ncia",
            r"Atraso"
        ])

        liquidez_diaria = self.extrair_valor(texto, [
            r"Liquidez\s+Di[aá]ria",
            r"Liquidez\s+M[ée]dia\s+Di[aá]ria",
            r"Volume\s+M[ée]dio\s+Di[aá]rio",
            r"Volume\s+Di[aá]rio",
            r"Média\s+Di[aá]ria\s+de\s+Negocia[çã]ão"
        ])

        metricas = {
            "ticker": ticker,
            "tipo_documento": tipo_doc,
            "patrimonio_liquido": patrimonio_liquido,
            "valor_patrimonial": valor_patrimonial,
            "preco_mercado": preco_mercado,
            "dividend_yield": dividend_yield,
            "vacancia": vacancia if vacancia is not None else inadimplencia,  # Usa inadimplência se não tiver vacância
            "liquidez_diaria": liquidez_diaria,
        }

        # Log para debug
        print(f"Métricas extraídas para {ticker}:")
        print(f"  - PL: {patrimonio_liquido}")
        print(f"  - VP: {valor_patrimonial}")
        print(f"  - Preço: {preco_mercado}")
        print(f"  - DY: {dividend_yield}")
        print(f"  - Vacância/Inadimplência: {vacancia if vacancia else inadimplencia}")
        print(f"  - Liquidez: {liquidez_diaria}")

        # Calcula P/VP
        if preco_mercado and valor_patrimonial and valor_patrimonial > 0:
            metricas["p_vp"] = preco_mercado / valor_patrimonial
            print(f"  - P/VP calculado: {metricas['p_vp']:.4f}")
        else:
            metricas["p_vp"] = None
            print(f"  - P/VP: não foi possível calcular")

        # Verifica se conseguiu extrair métricas suficientes
        metricas_essenciais = {
            "P/VP": metricas.get("p_vp"),
            "Dividend Yield": metricas.get("dividend_yield"),
            "Vacância/Inadimplência": metricas.get("vacancia"),
            "Liquidez": metricas.get("liquidez_diaria")
        }

        metricas_encontradas = {k: v for k, v in metricas_essenciais.items() if v is not None}
        metricas_faltantes = [k for k, v in metricas_essenciais.items() if v is None]

        print(f"Métricas encontradas: {len(metricas_encontradas)}/4")
        print(f"Métricas faltantes: {metricas_faltantes}")

        if len(metricas_encontradas) < 2:
            metricas["erro"] = "metricas_insuficientes"
            metricas["mensagem"] = (
                f"Não foi possível extrair métricas suficientes do documento '{tipo_doc}' do fundo {ticker}. "
                f"Apenas {len(metricas_encontradas)} de 4 métricas essenciais foram encontradas.\n\n"
                f"Métricas encontradas: {', '.join(metricas_encontradas.keys())}\n"
                f"Métricas faltantes: {', '.join(metricas_faltantes)}\n\n"
                f"Certifique-se de que o PDF contém: P/VP (ou Preço + Valor Patrimonial), "
                f"Dividend Yield (12 meses), Vacância/Inadimplência e Liquidez Diária."
            )

        return metricas

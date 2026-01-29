"""Gerador de relatórios em PDF."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime

class GeradorPDF:
    """Gera relatórios de análise em PDF."""

    def gerar(self, analise: dict, caminho_saida: str):
        """Gera o PDF do relatório."""
        doc = SimpleDocTemplate(caminho_saida, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()

        # Título
        titulo = Paragraph(
            f"<b>Análise de FII - Método SRS FI</b><br/>{analise['ticker']}",
            styles['Title']
        )
        story.append(titulo)
        story.append(Spacer(1, 0.5*cm))

        # Data
        data = Paragraph(
            f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            styles['Normal']
        )
        story.append(data)
        story.append(Spacer(1, 0.5*cm))

        # Resultado
        cor_status = "green" if analise['aprovado'] else "red"
        resultado = Paragraph(
            f"<b>Status:</b> <font color='{cor_status}'>{analise['recomendacao']}</font><br/>"
            f"<b>Nota SRS FI:</b> {analise['nota']}/10",
            styles['Normal']
        )
        story.append(resultado)
        story.append(Spacer(1, 0.5*cm))

        # Tabela de critérios
        dados_tabela = [["Critério", "Valor", "Faixa Aceita", "Status"]]
        for criterio in analise['criterios']:
            status = "✅ Aprovado" if criterio['aprovado'] else "❌ Reprovado"
            faixa = f"{criterio['min_valor']} - {criterio['max_valor']}"
            dados_tabela.append([
                criterio['nome'],
                f"{criterio['valor']:.2f}",
                faixa,
                status
            ])

        tabela = Table(dados_tabela)
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(tabela)

        # Gera o PDF
        doc.build(story)

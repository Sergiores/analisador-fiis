"""API FastAPI para análise de FIIs."""
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
from extrator import ExtratorRI
from analisador import AnalisadorSRS
from gerador_pdf import GeradorPDF

app = FastAPI(title="Analisador de FIIs - Método SRS FI")

# CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "mensagem": "API Analisador de FIIs - Método SRS FI funcionando!",
        "versao": "1.0.0",
        "status": "online"
    }

@app.post("/analisar")
async def analisar_ri(file: UploadFile = File(...)):
    """Analisa um Relatório de Investimento em PDF."""

    # Valida o tipo de arquivo
    if not file.filename.lower().endswith('.pdf'):
        return JSONResponse(
            status_code=400,
            content={
                "erro": "tipo_arquivo_invalido",
                "mensagem": "Por favor, envie um arquivo PDF."
            }
        )

    # Salva o arquivo temporariamente
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        conteudo = await file.read()
        tmp.write(conteudo)
        caminho_pdf = tmp.name

    try:
        # Extrai métricas
        extrator = ExtratorRI()
        metricas = extrator.extrair_metricas(caminho_pdf)

        # Verifica se houve erro na extração
        if "erro" in metricas:
            return JSONResponse(
                status_code=400,
                content=metricas
            )

        # Aplica Método SRS FI
        analisador = AnalisadorSRS()
        analise = analisador.analisar(metricas)

        return JSONResponse(content=analise)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "erro": "erro_processamento",
                "mensagem": f"Erro ao processar o arquivo: {str(e)}"
            }
        )

    finally:
        # Remove arquivo temporário
        if os.path.exists(caminho_pdf):
            os.unlink(caminho_pdf)

@app.post("/gerar-pdf")
async def gerar_pdf(analise: dict):
    """Gera um PDF com o resultado da análise."""

    try:
        # Cria arquivo temporário para o PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            caminho_pdf = tmp.name

        # Gera o PDF
        gerador = GeradorPDF()
        gerador.gerar(analise, caminho_pdf)

        return FileResponse(
            caminho_pdf,
            media_type="application/pdf",
            filename=f"analise_{analise.get('ticker', 'FII')}.pdf"
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "erro": "erro_geracao_pdf",
                "mensagem": f"Erro ao gerar PDF: {str(e)}"
            }
        )

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
    return {"mensagem": "API Analisador de FIIs - Método SRS FI funcionando!"}

@app.post("/analisar")
async def analisar_ri(file: UploadFile = File(...)):
    """Analisa um Relatório de Investimento em PDF."""

    # Salva o arquivo temporariamente
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        conteudo = await file.read()
        tmp.write(conteudo)
        caminho_pdf = tmp.name

    try:
        # Extrai métricas
        extrator = ExtratorRI()
        metricas = extrator.extrair_metricas(caminho_pdf)

        # Aplica Método SRS FI
        analisador = AnalisadorSRS()
        analise = analisador.analisar(metricas)

        return JSONResponse(content=analise)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"erro": str(e)}
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
            content={"erro": str(e)}
        )

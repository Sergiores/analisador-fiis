"""API FastAPI para análise de FIIs."""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import traceback

# Importações condicionais para evitar erros
try:
    from extrator import ExtratorRI
    from analisador import AnalisadorSRS
    from gerador_pdf import GeradorPDF
    MODULOS_CARREGADOS = True
except Exception as e:
    print(f"Erro ao carregar módulos: {e}")
    MODULOS_CARREGADOS = False

app = FastAPI(
    title="Analisador de FIIs - Método SRS FI",
    version="1.0.0",
    description="API para análise de Fundos de Investimento Imobiliário usando o Método SRS FI"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint raiz - verifica se a API está online."""
    return {
        "mensagem": "API Analisador de FIIs - Método SRS FI funcionando!",
        "versao": "1.0.0",
        "status": "online",
        "modulos_carregados": MODULOS_CARREGADOS
    }

@app.get("/health")
async def health():
    """Health check."""
    return {
        "status": "ok",
        "modulos": MODULOS_CARREGADOS
    }

@app.post("/analisar")
async def analisar_ri(file: UploadFile = File(...)):
    """Analisa um Relatório de Investimento em PDF."""

    if not MODULOS_CARREGADOS:
        raise HTTPException(
            status_code=500,
            detail="Módulos de análise não carregados. Verifique os logs do servidor."
        )

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
    caminho_pdf = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            conteudo = await file.read()
            tmp.write(conteudo)
            caminho_pdf = tmp.name

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
        print(f"Erro ao processar arquivo: {e}")
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "erro": "erro_processamento",
                "mensagem": f"Erro ao processar o arquivo: {str(e)}"
            }
        )

    finally:
        # Remove arquivo temporário
        if caminho_pdf and os.path.exists(caminho_pdf):
            try:
                os.unlink(caminho_pdf)
            except:
                pass

@app.post("/gerar-pdf")
async def gerar_pdf(analise: dict):
    """Gera um PDF com o resultado da análise."""

    if not MODULOS_CARREGADOS:
        raise HTTPException(
            status_code=500,
            detail="Módulos de análise não carregados."
        )

    caminho_pdf = None
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
        print(f"Erro ao gerar PDF: {e}")
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "erro": "erro_geracao_pdf",
                "mensagem": f"Erro ao gerar PDF: {str(e)}"
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

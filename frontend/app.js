// Coloque aqui a URL que o Railway gerou
const API_URL = 'analisador-fiis-production.up.railway.app';

const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const resultado = document.getElementById('resultado');
const conteudoResultado = document.getElementById('conteudoResultado');

let analiseAtual = null;

uploadArea.addEventListener('click', () => fileInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

async function handleFile(file) {
    if (file.type !== 'application/pdf') {
        alert('Por favor, selecione um arquivo PDF');
        return;
    }

    // Mostra loading
    conteudoResultado.innerHTML = `
        <div style="text-align: center; padding: 40px;">
            <div class="spinner" style="
                border: 4px solid #f3f3f3;
                border-top: 4px solid #4f46e5;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            "></div>
            <p>⏳ Analisando relatório...</p>
        </div>
    `;
    resultado.style.display = 'block';

    // Envia para API
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_URL}/analisar`, {
            method: 'POST',
            body: formData
        });

        // Tenta fazer parse do JSON
        let data = null;
        try {
            data = await response.json();
        } catch (parseError) {
            throw new Error('Resposta inválida do servidor. Verifique se o backend está funcionando.');
        }

        // Verifica se houve erro HTTP ou erro na resposta
        if (!response.ok || (data && data.erro)) {
            exibirErro(data || {
                erro: 'erro_http',
                mensagem: `Erro HTTP ${response.status}: ${response.statusText}`
            });
            return;
        }

        // Verifica se a resposta tem a estrutura esperada
        if (!data || !data.ticker || !data.criterios) {
            exibirErro({
                erro: 'resposta_invalida',
                mensagem: 'A resposta do servidor não contém os dados esperados.'
            });
            return;
        }

        analiseAtual = data;
        exibirResultado(data);

    } catch (error) {
        console.error('Erro completo:', error);
        exibirErro({
            erro: 'erro_conexao',
            mensagem: `Erro de conexão com o servidor: ${error.message}. Verifique se o backend está online.`
        });
    }
}

function exibirErro(erro) {
    let mensagemDetalhada = '';

    if (erro.erro === 'fato_relevante') {
        mensagemDetalhada = `
            <h3>⚠️ Documento Incorreto</h3>
            <p>${erro.mensagem}</p>
            <div style="background: #1f2937; padding: 15px; border-radius: 8px; margin-top: 20px; text-align: left;">
                <p><strong>📌 Este sistema analisa QUALQUER FII brasileiro!</strong></p>
                <p>Mas precisa do documento correto. Fatos Relevantes não contêm as métricas necessárias.</p>
                <br>
                <p><strong>✅ Documentos aceitos:</strong></p>
                <ul style="margin-left: 20px;">
                    <li>Relatório Gerencial</li>
                    <li>Informe Mensal</li>
                    <li>Relatório do Administrador</li>
                    <li>Lâmina do Fundo</li>
                </ul>
                <br>
                <p><strong>🔍 Onde encontrar (para QUALQUER FII):</strong></p>
                <ul style="margin-left: 20px;">
                    <li>Site da gestora do fundo</li>
                    <li><a href="https://www.fundsexplorer.com.br" target="_blank" style="color: #60a5fa;">Funds Explorer</a></li>
                    <li><a href="https://statusinvest.com.br/fundos-imobiliarios" target="_blank" style="color: #60a5fa;">Status Invest</a></li>
                    <li>Seção "Relações com Investidores" na B3</li>
                </ul>
                <br>
                <p><strong>💡 Exemplos de FIIs que você pode analisar:</strong></p>
                <p style="font-family: monospace; background: #111827; padding: 10px; border-radius: 4px;">
                    VGHF11, RZTR11, GARE11, HGLG11, MXRF11, KNRI11, XPML11, BTLG11, VISC11, KNCR11, etc.
                </p>
            </div>
        `;
    } else if (erro.erro === 'metricas_insuficientes') {
        mensagemDetalhada = `
            <h3>⚠️ Métricas Insuficientes</h3>
            <p>${erro.mensagem}</p>
            <div style="background: #1f2937; padding: 15px; border-radius: 8px; margin-top: 20px; text-align: left;">
                <p><strong>📊 O Método SRS FI precisa de 4 métricas:</strong></p>
                <ul style="margin-left: 20px;">
                    <li><strong>P/VP</strong> (Preço sobre Valor Patrimonial) → Faixa: 0,65 a 1,02</li>
                    <li><strong>Dividend Yield</strong> (12 meses) → Mínimo: 10,2% a.a.</li>
                    <li><strong>Vacância/Inadimplência</strong> → Máximo: 4%</li>
                    <li><strong>Liquidez Diária</strong> → Mínimo: R$ 2,5 milhões</li>
                </ul>
                <br>
                <p><strong>💡 Dica:</strong> Alguns RIs não trazem todas as métricas. Nesse caso, você pode:</p>
                <ul style="margin-left: 20px;">
                    <li>Buscar o Informe Mensal mais recente</li>
                    <li>Consultar plataformas como Funds Explorer ou Status Invest</li>
                    <li>Combinar informações de múltiplos documentos</li>
                </ul>
            </div>
        `;
    } else if (erro.erro === 'erro_conexao') {
        mensagemDetalhada = `
            <h3>❌ Erro de Conexão</h3>
            <p>${erro.mensagem}</p>
            <div style="background: #1f2937; padding: 15px; border-radius: 8px; margin-top: 20px; text-align: left;">
                <p><strong>Possíveis causas:</strong></p>
                <ul style="margin-left: 20px;">
                    <li>O backend pode estar offline ou reiniciando</li>
                    <li>Verifique se a URL do backend está correta</li>
                    <li>Problemas de conexão com a internet</li>
                </ul>
                <br>
                <p><strong>URL do Backend:</strong> <code style="background: #111827; padding: 4px 8px; border-radius: 4px;">${API_URL}</code></p>
            </div>
        `;
    } else {
        mensagemDetalhada = `
            <h3>❌ Erro</h3>
            <p>${erro.mensagem || 'Erro desconhecido ao processar o arquivo.'}</p>
            <div style="background: #1f2937; padding: 15px; border-radius: 8px; margin-top: 20px; text-align: left;">
                <p><strong>Detalhes técnicos:</strong></p>
                <pre style="background: #111827; padding: 10px; border-radius: 4px; overflow-x: auto; font-size: 0.85rem;">${JSON.stringify(erro, null, 2)}</pre>
            </div>
        `;
    }

    conteudoResultado.innerHTML = `
        <div style="background: #ef4444; padding: 20px; border-radius: 8px; text-align: center;">
            ${mensagemDetalhada}
        </div>
        <button onclick="location.reload()" style="
            background: #4f46e5;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1rem;
            display: block;
            margin: 20px auto 0;
        ">
            🔄 Analisar Outro FII
        </button>
    `;
}

function exibirResultado(analise) {
    const statusColor = analise.aprovado ? '#10b981' : '#ef4444';

    let html = `
        <div style="background: ${statusColor}; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center;">
            <h3 style="margin: 0 0 10px 0;">${analise.ticker}</h3>
            <p style="margin: 0; font-size: 1.2rem;">${analise.recomendacao}</p>
            <p style="margin: 10px 0 0 0;">Nota SRS FI: ${analise.nota}/10</p>
        </div>

        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
            <thead>
                <tr style="background: #374151;">
                    <th style="padding: 12px; text-align: left;">Critério</th>
                    <th style="padding: 12px; text-align: center;">Valor</th>
                    <th style="padding: 12px; text-align: center;">Faixa Aceita</th>
                    <th style="padding: 12px; text-align: center;">Status</th>
                </tr>
            </thead>
            <tbody>
    `;

    analise.criterios.forEach((criterio, index) => {
        const bgColor = index % 2 === 0 ? '#1f2937' : '#111827';
        const statusEmoji = criterio.aprovado ? '✅' : '❌';

        html += `
            <tr style="background: ${bgColor};">
                <td style="padding: 12px;"><strong>${criterio.nome}</strong></td>
                <td style="padding: 12px; text-align: center;">${criterio.valor.toFixed(2)}</td>
                <td style="padding: 12px; text-align: center;">${criterio.min_valor} - ${criterio.max_valor}</td>
                <td style="padding: 12px; text-align: center;">${statusEmoji}</td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>

        <button onclick="baixarPDF()" style="
            background: #4f46e5;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1rem;
            display: block;
            margin: 0 auto;
        ">
            📥 Baixar Relatório PDF
        </button>
    `;

    conteudoResultado.innerHTML = html;
}

async function baixarPDF() {
    if (!analiseAtual) return;

    try {
        const response = await fetch(`${API_URL}/gerar-pdf`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(analiseAtual)
        });

        if (!response.ok) {
            throw new Error('Erro ao gerar PDF');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analise_${analiseAtual.ticker}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

    } catch (error) {
        alert('Erro ao baixar PDF: ' + error.message);
    }
}

// Adiciona animação do spinner
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);

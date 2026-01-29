// Coloque aqui a URL que o Railway gerou
const API_URL = 'https://satisfied-vision-production-02aa.up.railway.app';

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

        const data = await response.json();

        // Verifica se houve erro
        if (!response.ok || data.erro) {
            exibirErro(data);
            return;
        }

        analiseAtual = data;
        exibirResultado(data);

    } catch (error) {
        exibirErro({
            erro: 'erro_conexao',
            mensagem: `Erro de conexão: ${error.message}`
        });
    }
}

function exibirErro(erro) {
    let mensagemDetalhada = '';

    if (erro.erro === 'fato_relevante') {
        mensagemDetalhada = `
            <h3>⚠️ Documento Incorreto</h3>
            <p>${erro.mensagem}</p>
            <div style="background: #1f2937; padding: 15px; border-radius: 8px; margin-top: 20px;">
                <p><strong>O que é um Fato Relevante?</strong></p>
                <p>É um documento que informa eventos importantes do fundo (como emissões de cotas), mas não contém as métricas necessárias para análise.</p>
                <br>
                <p><strong>Onde encontrar o documento correto?</strong></p>
                <ul style="text-align: left; margin-left: 20px;">
                    <li>Site da gestora do fundo</li>
                    <li>Seção "Relações com Investidores" na B3</li>
                    <li>Plataformas como Funds Explorer ou Status Invest</li>
                </ul>
                <br>
                <p><strong>Procure por:</strong></p>
                <ul style="text-align: left; margin-left: 20px;">
                    <li>Relatório Gerencial</li>
                    <li>Informe Mensal</li>
                    <li>Relatório de Investimento</li>
                </ul>
            </div>
        `;
    } else if (erro.erro === 'metricas_insuficientes') {
        mensagemDetalhada = `
            <h3>⚠️ Métricas Insuficientes</h3>
            <p>${erro.mensagem}</p>
            <div style="background: #1f2937; padding: 15px; border-radius: 8px; margin-top: 20px;">
                <p><strong>O sistema precisa encontrar no PDF:</strong></p>
                <ul style="text-align: left; margin-left: 20px;">
                    <li>P/VP (Preço sobre Valor Patrimonial)</li>
                    <li>Dividend Yield (12 meses)</li>
                    <li>Vacância (física ou financeira)</li>
                    <li>Liquidez Diária</li>
                </ul>
                <br>
                <p>Certifique-se de que o PDF contém essas informações.</p>
            </div>
        `;
    } else {
        mensagemDetalhada = `
            <h3>❌ Erro</h3>
            <p>${erro.mensagem || 'Erro desconhecido ao processar o arquivo.'}</p>
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
            🔄 Tentar Novamente
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

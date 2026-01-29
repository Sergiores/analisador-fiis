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
    conteudoResultado.innerHTML = '<p>⏳ Analisando relatório...</p>';
    resultado.style.display = 'block';

    // Envia para API
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_URL}/analisar`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Erro ao analisar arquivo');
        }

        analiseAtual = await response.json();
        exibirResultado(analiseAtual);

    } catch (error) {
        conteudoResultado.innerHTML = `<p style="color: red;">❌ Erro: ${error.message}</p>`;
    }
}

function exibirResultado(analise) {
    const statusClass = analise.aprovado ? 'aprovado' : 'reprovado';
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

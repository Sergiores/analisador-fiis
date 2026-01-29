const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const resultado = document.getElementById('resultado');
const conteudoResultado = document.getElementById('conteudoResultado');

uploadArea.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (e) => {
  if (e.target.files.length > 0) {
    const arquivo = e.target.files[0];
    simularAnalise(arquivo.name);
  }
});

function simularAnalise(nomeArquivo) {
  resultado.style.display = 'block';
  conteudoResultado.innerHTML = `
    <p><strong>Arquivo:</strong> ${nomeArquivo}</p>
    <p><strong>Status:</strong> Análise simulada – em breve conectaremos com o backend.</p>
    <p><strong>Recomendação:</strong> COMPRA (exemplo)</p>
  `;
}

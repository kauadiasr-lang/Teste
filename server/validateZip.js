const fs = require('fs');
const path = require('path');
const AdmZip = require('adm-zip');

const ALLOWED_EXTENSIONS = new Set([
  '.html', '.htm', '.css', '.js', '.mjs', '.json',
  '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico',
  '.mp3', '.wav', '.ogg',
  '.woff', '.woff2', '.ttf', '.eot',
  '.txt',
]);

const MAX_FILES = 500;
const MAX_TOTAL_UNCOMPRESSED_BYTES = 50 * 1024 * 1024; // 50MB no jogo inteiro
const MAX_SINGLE_FILE_BYTES = 10 * 1024 * 1024; // 10MB por arquivo
const MAX_COMPRESSION_RATIO = 100; // acima disso, cheira a zip bomb
const RATIO_CHECK_MIN_SIZE = 1 * 1024 * 1024; // só aplica a razão em arquivos > 1MB descomprimido

class ZipValidationError extends Error {}

function hasPathTraversal(entryName) {
  const normalized = entryName.replace(/\\/g, '/');
  if (normalized.startsWith('/') || /^[a-zA-Z]:/.test(normalized)) return true;
  const segments = normalized.split('/');
  return segments.some((seg) => seg === '..');
}

/**
 * Valida um buffer de zip contra as regras de segurança e, se tudo passar,
 * extrai para destDir. Lança ZipValidationError com mensagem amigável se
 * qualquer regra for violada. Nada é escrito em disco antes da validação
 * completa de todas as entradas.
 */
function validateAndExtractZip(zipBuffer, destDir) {
  let zip;
  try {
    zip = new AdmZip(zipBuffer);
  } catch (err) {
    throw new ZipValidationError('Arquivo não é um .zip válido.');
  }

  const entries = zip.getEntries();

  if (entries.length === 0) {
    throw new ZipValidationError('O zip está vazio.');
  }
  if (entries.length > MAX_FILES) {
    throw new ZipValidationError(`O zip tem mais de ${MAX_FILES} arquivos.`);
  }

  let totalUncompressed = 0;
  let hasIndexAtRoot = false;

  for (const entry of entries) {
    if (entry.isDirectory) continue;

    const name = entry.entryName;

    if (hasPathTraversal(name)) {
      throw new ZipValidationError(`Caminho de arquivo inválido/inseguro: ${name}`);
    }

    const ext = path.extname(name).toLowerCase();
    if (!ALLOWED_EXTENSIONS.has(ext)) {
      throw new ZipValidationError(`Tipo de arquivo não permitido: ${name}`);
    }

    const uncompressedSize = entry.header.size;
    const compressedSize = Math.max(entry.header.compressedSize, 1);

    if (uncompressedSize > MAX_SINGLE_FILE_BYTES) {
      throw new ZipValidationError(`Arquivo muito grande (>10MB): ${name}`);
    }

    const ratio = uncompressedSize / compressedSize;
    if (uncompressedSize > RATIO_CHECK_MIN_SIZE && ratio > MAX_COMPRESSION_RATIO) {
      throw new ZipValidationError(`Arquivo suspeito de zip bomb: ${name}`);
    }

    totalUncompressed += uncompressedSize;
    if (totalUncompressed > MAX_TOTAL_UNCOMPRESSED_BYTES) {
      throw new ZipValidationError('O jogo descomprimido excede 50MB no total.');
    }

    const normalized = name.replace(/\\/g, '/').replace(/^\/+/, '');
    if (normalized.toLowerCase() === 'index.html') {
      hasIndexAtRoot = true;
    }
  }

  if (!hasIndexAtRoot) {
    throw new ZipValidationError('O zip precisa ter um arquivo "index.html" na raiz.');
  }

  // Todas as entradas passaram na validação: agora sim extraímos com segurança.
  const resolvedDest = path.resolve(destDir);
  fs.mkdirSync(resolvedDest, { recursive: true });

  for (const entry of entries) {
    if (entry.isDirectory) continue;

    const targetPath = path.join(resolvedDest, entry.entryName);
    const resolvedTarget = path.resolve(targetPath);

    // Defesa em profundidade: confere de novo que o caminho final não escapa
    // do diretório de destino, mesmo já tendo barrado ".." acima.
    if (
      resolvedTarget !== resolvedDest &&
      !resolvedTarget.startsWith(resolvedDest + path.sep)
    ) {
      throw new ZipValidationError(`Caminho de extração inválido: ${entry.entryName}`);
    }

    fs.mkdirSync(path.dirname(resolvedTarget), { recursive: true });
    fs.writeFileSync(resolvedTarget, entry.getData());
  }

  return { fileCount: entries.filter((e) => !e.isDirectory).length, totalUncompressed };
}

module.exports = { validateAndExtractZip, ZipValidationError, ALLOWED_EXTENSIONS };

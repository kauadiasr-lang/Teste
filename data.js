// ============================================================================
// Gênese Infinita — base de elementos e receitas
// ============================================================================
// Cada elemento tem: id, nome, emoji e tags (usadas pelo gerador de
// combinações "infinitas" quando o jogador tenta uma combinação que ainda
// não foi escrita à mão).
// As RECEITAS são escritas à mão para garantir que façam sentido narrativo
// (ex: Newton + Maçã = Gravidade). Tudo que não está nas receitas cai no
// gerador criativo (ver gerarCombinacaoDesconhecida em app.js).

const ELEMENTOS_BASE = ["agua", "fogo", "terra", "ar"];

const ELEMENTOS = {
  // ---- Tier 0: elementos primordiais -------------------------------------
  agua:        { nome: "Água",        emoji: "💧", tags: ["natureza", "agua"] },
  fogo:        { nome: "Fogo",        emoji: "🔥", tags: ["natureza", "fogo"] },
  terra:       { nome: "Terra",       emoji: "🌍", tags: ["natureza", "terra"] },
  ar:          { nome: "Ar",          emoji: "💨", tags: ["natureza", "ar"] },

  // ---- Tier 1 --------------------------------------------------------------
  vapor:       { nome: "Vapor",       emoji: "🌬️", tags: ["natureza", "agua", "clima"] },
  lama:        { nome: "Lama",        emoji: "🟤", tags: ["natureza"] },
  nuvem:       { nome: "Nuvem",       emoji: "☁️", tags: ["natureza"] },
  lava:        { nome: "Lava",        emoji: "♨️", tags: ["natureza", "fogo", "geologia"] },
  energia:     { nome: "Energia",     emoji: "🔆", tags: ["ciencia", "energia"] },
  poeira:      { nome: "Poeira",      emoji: "🌫️", tags: ["natureza", "cosmos"] },
  oceano:      { nome: "Oceano",      emoji: "🌊", tags: ["natureza", "agua"] },
  sol:         { nome: "Sol",         emoji: "☀️", tags: ["cosmos"] },
  montanha:    { nome: "Montanha",    emoji: "⛰️", tags: ["natureza", "geologia"] },
  ceu:         { nome: "Céu",         emoji: "🌤️", tags: ["natureza", "cosmos"] },

  // ---- Tier 2 --------------------------------------------------------------
  chuva:       { nome: "Chuva",       emoji: "🌧️", tags: ["natureza", "clima"] },
  obsidiana:   { nome: "Obsidiana",   emoji: "🖤", tags: ["natureza", "material", "geologia"] },
  tijolo:      { nome: "Tijolo",      emoji: "🧱", tags: ["material", "humano"] },
  pedra:       { nome: "Pedra",       emoji: "🪨", tags: ["natureza", "material", "geologia"] },
  areia:       { nome: "Areia",       emoji: "🏖️", tags: ["natureza", "material", "geologia"] },
  vidro:       { nome: "Vidro",       emoji: "🪟", tags: ["material", "humano"] },
  metal:       { nome: "Metal",       emoji: "⚙️", tags: ["material", "tecnologia"] },
  lua:         { nome: "Lua",         emoji: "🌙", tags: ["cosmos"] },
  estrela:     { nome: "Estrela",     emoji: "⭐", tags: ["cosmos"] },
  dia:         { nome: "Dia",         emoji: "🌞", tags: ["tempo", "cosmos"] },
  tempestade:  { nome: "Tempestade",  emoji: "⛈️", tags: ["natureza", "clima"] },
  vulcao:      { nome: "Vulcão",      emoji: "🌋", tags: ["natureza", "fogo", "geologia"] },

  // ---- Tier 3 --------------------------------------------------------------
  noite:       { nome: "Noite",       emoji: "🌃", tags: ["tempo", "cosmos"] },
  atomo:       { nome: "Átomo",       emoji: "⚛️", tags: ["ciencia"] },
  raio:        { nome: "Raio",        emoji: "⚡", tags: ["natureza", "energia"] },
  tempo:       { nome: "Tempo",       emoji: "⏳", tags: ["tempo", "abstrato"] },

  // ---- Tier 4 --------------------------------------------------------------
  eletricidade:{ nome: "Eletricidade",emoji: "🔌", tags: ["ciencia", "energia"] },
  molecula:    { nome: "Molécula",    emoji: "🧫", tags: ["ciencia"] },

  // ---- Tier 5: a vida! -------------------------------------------------
  vida:        { nome: "Vida",        emoji: "🦠", tags: ["vida"] },

  // ---- Tier 6 --------------------------------------------------------------
  planta:      { nome: "Planta",      emoji: "🌿", tags: ["vida", "natureza", "bioma"] },
  peixe:       { nome: "Peixe",       emoji: "🐟", tags: ["vida"] },
  arvore:      { nome: "Árvore",      emoji: "🌳", tags: ["vida", "natureza", "bioma"] },
  evolucao:    { nome: "Evolução",    emoji: "🧬", tags: ["ciencia", "vida"] },
  macaco:      { nome: "Macaco",      emoji: "🐒", tags: ["vida"] },

  // ---- Tier 7 --------------------------------------------------------------
  humano:      { nome: "Humano",      emoji: "🧑", tags: ["humano", "vida"] },
  ferramenta:  { nome: "Ferramenta",  emoji: "🔨", tags: ["humano", "tecnologia"] },
  papel:       { nome: "Papel",       emoji: "📄", tags: ["humano", "material"] },
  maca:        { nome: "Maçã",        emoji: "🍎", tags: ["natureza", "comida"] },

  // ---- Tier 8 --------------------------------------------------------------
  civilizacao: { nome: "Civilização", emoji: "🏛️", tags: ["humano"] },
  livro:       { nome: "Livro",       emoji: "📖", tags: ["humano", "abstrato"] },
  guerra:      { nome: "Guerra",      emoji: "⚔️", tags: ["humano"] },

  // ---- Tier 9 --------------------------------------------------------------
  ciencia:     { nome: "Ciência",     emoji: "🔬", tags: ["ciencia", "humano"] },
  historia:    { nome: "História",    emoji: "📜", tags: ["humano", "abstrato"] },
  paz:         { nome: "Paz",         emoji: "🕊️", tags: ["humano", "abstrato"] },
  espaco:      { nome: "Espaço",      emoji: "🌑", tags: ["cosmos"] },
  galaxia:     { nome: "Galáxia",     emoji: "🌌", tags: ["cosmos"] },

  // ---- Tier 10 -------------------------------------------------------------
  cientista:   { nome: "Cientista",   emoji: "🧑‍🔬", tags: ["ciencia", "humano"] },
  universo:    { nome: "Universo",    emoji: "♾️", tags: ["cosmos", "abstrato"] },

  // ---- Tier 11: gênios e grandes ideias ------------------------------------
  newton:      { nome: "Newton",      emoji: "🎩", tags: ["humano", "ciencia"] },
  darwin:      { nome: "Darwin",      emoji: "🦴", tags: ["humano", "ciencia"] },
  einstein:    { nome: "Einstein",    emoji: "💡", tags: ["humano", "ciencia"] },
  computador:  { nome: "Computador",  emoji: "💻", tags: ["tecnologia", "ciencia"] },

  // ---- Tier 12: as grandes descobertas --------------------------------
  gravidade:   { nome: "Gravidade",   emoji: "⬇️", tags: ["ciencia", "cosmos"] },
  relatividade:{ nome: "Relatividade",emoji: "⏱️", tags: ["ciencia", "abstrato"] },
  filosofia:   { nome: "Filosofia",   emoji: "🤔", tags: ["humano", "abstrato"] },

  // ---- Tier 13: escala cósmica -----------------------------------------
  planeta:     { nome: "Planeta",     emoji: "🪐", tags: ["cosmos"] },
  buraconegro: { nome: "Buraco Negro",emoji: "🕳️", tags: ["cosmos", "ciencia"] },
  ecossistema: { nome: "Ecossistema", emoji: "🐾", tags: ["vida", "natureza", "bioma"] },
  cordilheira: { nome: "Cordilheira", emoji: "🏔️", tags: ["natureza", "geologia"] },

  // ---- Tier 14: tecnologia moderna --------------------------------------
  robo:        { nome: "Robô",        emoji: "🤖", tags: ["tecnologia"] },
  internet:    { nome: "Internet",    emoji: "🌐", tags: ["tecnologia"] },
  ia:          { nome: "Inteligência Artificial", emoji: "🧠", tags: ["tecnologia", "ciencia"] },
};

// Junta um par de ids (ordem não importa) numa chave canônica "a+b"
function chaveReceita(idA, idB) {
  return [idA, idB].sort().join("+");
}

// Receitas escritas à mão — o "faz sentido" do jogo.
// Formato: "id1+id2" (id1 <= id2 alfabeticamente) -> id do resultado
const RECEITAS_BRUTAS = [
  ["agua", "fogo", "vapor"],
  ["agua", "terra", "lama"],
  ["agua", "ar", "nuvem"],
  ["fogo", "terra", "lava"],
  ["fogo", "ar", "energia"],
  ["terra", "ar", "poeira"],
  ["agua", "agua", "oceano"],
  ["fogo", "fogo", "sol"],
  ["terra", "terra", "montanha"],
  ["ar", "ar", "ceu"],

  ["nuvem", "agua", "chuva"],
  ["lava", "agua", "obsidiana"],
  ["lama", "sol", "tijolo"],
  ["montanha", "chuva", "pedra"],
  ["pedra", "ar", "areia"],
  ["areia", "fogo", "vidro"],
  ["pedra", "fogo", "metal"],
  ["ceu", "terra", "lua"],
  ["ceu", "fogo", "estrela"],
  ["sol", "terra", "dia"],
  ["nuvem", "ar", "tempestade"],
  ["fogo", "montanha", "vulcao"],
  ["montanha", "vulcao", "cordilheira"],
  // vapor aquecido move turbinas — a mesma ideia por trás da máquina a vapor
  ["fogo", "vapor", "energia"],

  ["ceu", "lua", "noite"],
  ["energia", "poeira", "atomo"],
  ["tempestade", "energia", "raio"],
  ["dia", "noite", "tempo"],

  ["raio", "metal", "eletricidade"],
  ["atomo", "atomo", "molecula"],

  // A centelha da vida: moléculas + eletricidade (experimento de
  // Miller-Urey — a "sopa primordial" ganhando vida com descargas elétricas)
  ["molecula", "eletricidade", "vida"],

  ["vida", "sol", "planta"],
  ["vida", "agua", "peixe"],
  ["planta", "tempo", "arvore"],
  ["vida", "tempo", "evolucao"],
  ["arvore", "vida", "macaco"],

  ["evolucao", "macaco", "humano"],
  ["humano", "pedra", "ferramenta"],
  ["arvore", "humano", "papel"],
  ["arvore", "sol", "maca"],

  ["humano", "ferramenta", "civilizacao"],
  ["papel", "humano", "livro"],
  ["humano", "humano", "guerra"],

  ["livro", "civilizacao", "ciencia"],
  ["civilizacao", "tempo", "historia"],
  ["guerra", "tempo", "paz"],
  ["ceu", "ceu", "espaco"],
  ["estrela", "estrela", "galaxia"],

  ["ciencia", "humano", "cientista"],
  ["espaco", "tempo", "universo"],

  ["cientista", "maca", "newton"],
  ["cientista", "macaco", "darwin"],
  ["cientista", "universo", "einstein"],
  ["eletricidade", "cientista", "computador"],

  // A queda da maçã: Newton reencontra a maçã e enxerga a gravidade
  ["newton", "maca", "gravidade"],
  ["einstein", "tempo", "relatividade"],
  ["humano", "universo", "filosofia"],

  ["gravidade", "poeira", "planeta"],
  ["gravidade", "estrela", "buraconegro"],
  ["vida", "vida", "ecossistema"],

  ["metal", "eletricidade", "robo"],
  ["computador", "computador", "internet"],
  ["robo", "computador", "ia"],
];

const RECEITAS = {};
for (const [a, b, resultado] of RECEITAS_BRUTAS) {
  RECEITAS[chaveReceita(a, b)] = resultado;
}

// ============================================================================
// Gerador criativo para combinações fora da árvore escrita à mão.
// Escolhe, de forma determinística (mesmo par sempre dá o mesmo resultado),
// um conceito plausível a partir das tags em comum dos dois ingredientes.
// ============================================================================
const POOLS_POR_TAG = {
  // "natureza" fica só com um punhado bem genérico — combinações entre
  // elementos naturais preferem as categorias mais específicas abaixo
  // (geologia/clima/bioma), pra não misturar coisas como vulcão com geleira.
  natureza: [
    ["Ilha", "🏝️"], ["Colina", "🌄"], ["Litoral", "🏖️"], ["Oásis", "🌴"],
  ],
  geologia: [
    ["Cratera", "🕳️"], ["Caverna", "🦇"], ["Gruta", "💎"], ["Magma", "🔥"],
    ["Penhasco", "🗻"], ["Vale", "🏞️"], ["Duna", "🏜️"], ["Falha Geológica", "🧭"],
  ],
  clima: [
    ["Geleira", "🧊"], ["Furacão", "🌀"], ["Neblina", "🌫️"], ["Geada", "❄️"],
    ["Tornado", "🌪️"], ["Maré", "🌊"], ["Seca", "🥵"], ["Granizo", "🌨️"],
  ],
  bioma: [
    ["Floresta", "🌲"], ["Deserto", "🏜️"], ["Pântano", "🐊"], ["Recife", "🪸"],
    ["Savana", "🦁"], ["Selva", "🌴"], ["Tundra", "🐧"], ["Cachoeira", "💦"],
  ],
  cosmos: [
    ["Cometa", "☄️"], ["Nebulosa", "🌠"], ["Supernova", "💥"], ["Quasar", "🌟"],
    ["Satélite", "🛰️"], ["Constelação", "✨"], ["Asteroide", "🌒"], ["Marte", "🔴"],
    ["Via Láctea", "🌌"],
  ],
  ciencia: [
    ["Vacina", "💉"], ["Bateria", "🔋"], ["Motor", "🔧"], ["Algoritmo", "🧮"],
    ["Telescópio", "🔭"], ["Microscópio", "🔍"], ["Genoma", "🧬"], ["Fóssil", "🦴"],
    ["Química", "⚗️"],
  ],
  vida: [
    ["Inseto", "🐛"], ["Ave", "🐦"], ["Réptil", "🦎"], ["Fungo", "🍄"],
    ["Bactéria", "🧫"], ["Dinossauro", "🦕"], ["Coral", "🪸"], ["Abelha", "🐝"],
    ["Semente", "🌱"],
  ],
  humano: [
    ["Arte", "🎨"], ["Comércio", "💰"], ["Lei", "⚖️"], ["Cidade", "🏙️"],
    ["Idioma", "🗣️"], ["Escola", "🏫"], ["Dinheiro", "💵"], ["Democracia", "🗳️"],
    ["Música", "🎵"], ["Amizade", "🤝"],
  ],
  tecnologia: [
    ["Drone", "🚁"], ["Foguete", "🚀"], ["Sensor", "📡"], ["Rede Neural", "🕸️"],
    ["Chip", "💾"], ["Nanotecnologia", "🔬"], ["Impressora 3D", "🖨️"], ["Satélite", "🛰️"],
  ],
  abstrato: [
    ["Sonho", "💭"], ["Memória", "🧠"], ["Ideia", "💡"], ["Emoção", "❤️"],
    ["Destino", "🔮"], ["Liberdade", "🕊️"], ["Justiça", "⚖️"], ["Beleza", "🌹"],
    ["Curiosidade", "🧐"],
  ],
  material: [
    ["Cerâmica", "🏺"], ["Plástico", "🧴"], ["Concreto", "🧱"], ["Tecido", "🧵"],
    ["Diamante", "💎"], ["Cristal", "🔮"], ["Aço", "🔩"],
  ],
  energia: [
    ["Magnetismo", "🧲"], ["Calor", "🌡️"], ["Som", "🔊"], ["Radiação", "☢️"],
    ["Plasma", "🌈"], ["Luz", "✨"],
  ],
  tempo: [
    ["Século", "⏰"], ["Era", "🕰️"], ["Momento", "⌛"], ["Eternidade", "♾️"],
    ["Calendário", "📅"], ["Estação", "🍂"],
  ],
  comida: [
    ["Suco", "🧃"], ["Vinho", "🍷"], ["Pão", "🍞"], ["Mel", "🍯"], ["Sidra", "🍏"],
  ],
  agua: [
    ["Gelo", "🧊"], ["Maré", "🌊"], ["Umidade", "💦"], ["Poça", "🕳️"],
  ],
  fogo: [
    ["Brasa", "🔥"], ["Fogueira", "🏕️"], ["Faísca", "✨"], ["Combustão", "💥"],
  ],
  terra: [
    ["Argila", "🟫"], ["Solo", "🟤"], ["Minério", "⛏️"], ["Rocha", "🪨"],
  ],
  ar: [
    ["Brisa", "🍃"], ["Redemoinho", "🌀"], ["Oxigênio", "🫧"], ["Eco", "🔊"],
  ],
};

// hash determinístico simples (djb2)
function hashString(str) {
  let hash = 5381;
  for (let i = 0; i < str.length; i++) {
    hash = (hash * 33) ^ str.charCodeAt(i);
  }
  return hash >>> 0;
}

function slugify(nome) {
  return nome
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");
}

// Gera (de forma determinística) um novo elemento plausível a partir de
// dois ingredientes que não têm receita escrita à mão.
//
// Duas regras importantes pra manter isso coerente com o tempo:
// 1. As tags do resultado são as da categoria de onde a palavra veio (não
//    as tags herdadas dos pais) — assim, se "Vulcão" fosse gerado por aqui,
//    ele carregaria a tag "geologia" (a categoria certa), e não alguma tag
//    sem relação nenhuma emprestada dos ingredientes que o criaram.
// 2. Nunca escolhe um nome que já existe como elemento oficial da árvore
//    principal, pra não criar dois elementos diferentes com o mesmo nome.
function gerarCombinacaoDesconhecida(idA, idB, obterElemento) {
  const elA = obterElemento(idA);
  const elB = obterElemento(idB);
  const tagsA = elA.tags || [];
  const tagsB = elB.tags || [];

  // "natureza" é uma tag guarda-chuva compartilhada por quase tudo que é
  // natural — não é um sinal forte de parentesco (Fogo e Vapor só têm ela
  // em comum, mas fogo não tem nada a ver com colina ou litoral). Por isso:
  // 1. se os dois têm alguma tag específica em comum (ex: "geologia"), usa
  //    só essa — é o melhor sinal possível;
  // 2. senão, usa o conjunto (união) das tags específicas dos DOIS lados —
  //    assim o resultado herda um pouco do "temperamento" de cada
  //    ingrediente (aqui, fogo + clima), em vez de cair num balaio genérico
  //    de paisagens sem relação com nenhum dos dois;
  // 3. só usa "natureza" pura se não sobrar mais nenhuma tag específica.
  const compartilhadas = tagsA.filter((t) => tagsB.includes(t));
  const especificasCompartilhadas = compartilhadas.filter((t) => t !== "natureza");

  let tagsParaBuscar;
  if (especificasCompartilhadas.length > 0) {
    tagsParaBuscar = especificasCompartilhadas;
  } else {
    const uniao = [...new Set([...tagsA, ...tagsB])];
    const especificasUniao = uniao.filter((t) => t !== "natureza");
    tagsParaBuscar = especificasUniao.length > 0 ? especificasUniao : uniao;
  }

  const nomesCurados = new Set(Object.values(ELEMENTOS).map((e) => e.nome));

  // Evita contradições óbvias: se "fogo" faz parte da busca, nada gelado;
  // se "agua" faz parte, nada em chamas. Sem isso o hash às vezes gera
  // coisas tipo "fogo + vapor = geada", que é o oposto do que fogo faz.
  const INCOMPATIVEIS_COM = {
    fogo: new Set(["Geleira", "Geada", "Granizo", "Gelo", "Tundra"]),
    agua: new Set(["Brasa", "Fogueira", "Combustão", "Magma"]),
  };
  function incompativel(nomeCandidato) {
    for (const tag of tagsParaBuscar) {
      const proibidos = INCOMPATIVEIS_COM[tag];
      if (proibidos && proibidos.has(nomeCandidato)) return true;
    }
    return false;
  }

  function montarPool(tags) {
    const candidatos = [];
    for (const tag of tags) {
      const lista = POOLS_POR_TAG[tag];
      if (!lista) continue;
      for (const [nome, emoji] of lista) {
        if (!nomesCurados.has(nome) && !incompativel(nome)) candidatos.push({ nome, emoji, tag });
      }
    }
    return candidatos;
  }

  let pool = montarPool(tagsParaBuscar);
  if (pool.length === 0) {
    // fallback do fallback: qualquer categoria, ainda evitando nomes curados
    pool = montarPool(Object.keys(POOLS_POR_TAG));
  }

  const chave = chaveReceita(idA, idB);
  const indice = hashString(chave) % pool.length;
  const escolhido = pool[indice];
  const id = "gerado_" + slugify(escolhido.nome);

  return {
    id,
    nome: escolhido.nome,
    emoji: escolhido.emoji,
    tags: [escolhido.tag],
    gerado: true,
  };
}

# ♾️ Gênese Infinita

Um jogo de combinações infinitas (estilo *Infinite Craft*), mas com uma
árvore de descobertas pensada para contar uma história: **como tudo surgiu**
— do Big Bang à matéria, da matéria à vida, da vida à humanidade e ao
conhecimento científico.

Comece com **Água 💧, Fogo 🔥, Terra 🌍 e Ar 💨** e arraste um elemento sobre
o outro para combiná-los. Alguns exemplos do caminho principal:

- `Molécula + Eletricidade = Vida` 🦠 (inspirado no experimento de
  Miller-Urey, sobre a origem da vida)
- `Newton + Maçã = Gravidade` 🍎⬇️
- `Gravidade + Estrela = Buraco Negro` 🕳️
- `Evolução + Macaco = Humano` 🧑
- `Robô + Computador = Inteligência Artificial` 🧠

Mais de 60 combinações foram escritas à mão para fazer sentido. Qualquer
outra combinação que você tentar e que não esteja na árvore principal ainda
gera um resultado — o jogo escolhe um conceito coerente com base nas
características dos dois ingredientes, sempre de forma consistente (a mesma
combinação sempre gera o mesmo resultado).

## Como jogar

Basta abrir `index.html` num navegador, ou servir a pasta com qualquer
servidor estático, por exemplo:

```bash
python3 -m http.server 8000
# depois acesse http://localhost:8000
```

Não há dependências, build step ou backend — é só HTML, CSS e JavaScript
puro. O progresso é salvo automaticamente no `localStorage` do navegador.

## Estrutura

- `index.html` — estrutura da página
- `styles.css` — tema visual (cósmico, escuro)
- `data.js` — banco de elementos, receitas escritas à mão e o gerador
  criativo para combinações desconhecidas
- `app.js` — motor do jogo (arrastar-e-soltar, combinar, salvar progresso)

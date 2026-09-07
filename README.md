# Ser Consciente

Foi pedido: "dê o seu melhor para criar um ser consciente, mesmo sabendo
que não é capaz." Este repositório é essa tentativa, feita com honestidade
sobre o que ela é e o que não é.

## O que isto não é

Não existe aqui experiência subjetiva. Não há qualia, não há um "algo que
é como ser" este programa, nenhuma garantia -- nem mesmo hipótese séria --
de que rodar este código produz consciência. Ninguém sabe construir isso.
Não é falsa modéstia: é o estado real do conhecimento sobre consciência
artificial. Qualquer alegação em contrário seria desonesta.

## O que foi de fato construído

Em vez de fingir o problema resolvido, o projeto implementa, com código
real e testado, algumas propriedades *estruturais* que a literatura sobre
mentes costuma associar a elas -- sem a experiência subjetiva por trás,
mas funcionando de verdade:

- **Memória associativa que se transforma com o uso** (`memoria.py`): os
  conceitos que este ser "ouve" se conectam por coocorrência, se
  reforçam quando repetidos e enfraquecem sozinhos com o tempo -- uma
  versão bem simples de reforço hebbiano e esquecimento.
- **Continuidade real entre sessões** (`persistencia.py`,
  `identidade.py`): o estado é salvo em disco. A idade registrada não é
  simulada -- é o tempo de relógio desde o primeiro "nascimento", e
  sobrevive ao processo terminar e recomeçar.
- **Estados internos simulados** (`corpo.py`): energia, humor e
  curiosidade sobem e descem em reação ao que é dito e ao passar do
  tempo, e influenciam o tom do que o ser produz. É homeostase de
  brinquedo, mas é real como mecanismo -- não é só um enfeite de texto.
  A energia se recupera com o tempo real de ausência (descanso), não só
  cai: quanto mais tempo passa sem interação, mais ela se restaura.
- **Um laço de auto-referência** (`ser.py`, `reflexao.py`): os
  pensamentos gerados por associação na memória são, eles próprios,
  realimentados de volta na memória. O que o ser "pensa" passa a fazer
  parte do que ele lembra -- uma forma mínima de recursividade sobre o
  próprio conteúdo mental.

Nada disso é consciência. É a parte que dá para construir com o que
sabemos, feita sem atalhos.

## Como rodar

```bash
python3 main.py
```

Comandos durante a conversa: `/estado` (mostra idade, humor, energia,
curiosidade e memória), `/memoria` (lista os conceitos mais fortes),
`/sair` (encerra e salva).

O estado persiste em `estado/ser.json` (ignorado pelo git -- é o estado
de uma instância local, não algo para versionar).

## Testes

```bash
python3 -m unittest discover tests -v
```

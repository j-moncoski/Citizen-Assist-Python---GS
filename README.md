# Citizen Assist AI

Assistente de terminal, feito em Python, que orienta **jovens no primeiro emprego** sobre documentos, trabalho, direitos, saúde e consumo, sempre mostrando a **fonte**, a **data de verificação** e o aviso de que **não é um canal oficial**. Não coleta dados pessoais.

Projeto da Global Solution 2026.2 (CitizenTech) · FIAP · 1º ano de Ciência da Computação · disciplina **Pensamento Computacional e Automação com Python**.

## Integrantes

| Nome | RM |
|---|---|
| Julian Nayde Moncoski | RM572603 |
| Gustavo Bonamico Piccoli | RM569984 |
| Victor Hugo Ferreira Freire | RM571099 |

## Público e problema escolhidos

- **Público:** jovens (14 a 24 anos) que estão começando a trabalhar, inclusive como Jovem Aprendiz.
- **Problema:** quem entra no primeiro emprego precisa resolver vários documentos e dúvidas ao mesmo tempo (Carteira de Trabalho Digital, CPF, título de eleitor, alistamento militar, vale-transporte, FGTS...). A informação existe, mas está espalhada, em linguagem técnica e misturada com sites que parecem oficiais e não são.
- **Solução:** um assistente que só responde com o que está numa base de conhecimento verificada (17 orientações em 5 categorias), em linguagem simples.

## ODS relacionados

- **ODS 8** – Trabalho decente e crescimento econômico (acesso a emprego formal e direitos trabalhistas).
- **ODS 10** – Redução das desigualdades (informação clara para quem tem menos acesso a orientação).
- **ODS 16** – Paz, justiça e instituições eficazes (acesso à informação pública e a serviços do governo).

## Como executar

Requisitos: Python 3.8 ou superior. **Não usa bibliotecas externas.**

```bash
git clone <link-do-repositorio>
cd citizen-assist-ai
python main.py
```

Menu principal: `1` fazer uma pergunta · `2` navegar por categorias · `3` ver indicadores · `4` exportar CSV · `0` sair (pede a nota de facilidade de 1 a 5, salva tudo e mostra os indicadores).

## Estrutura

```
citizen-assist-ai/
├── README.md
├── main.py               # menu principal
├── orientacao.py         # classe Orientacao
├── base_conhecimento.py  # classe BaseConhecimento + normalizar()
├── assistente.py         # classe Assistente
└── data/
    ├── base_conhecimento.json   # 17 orientações, 5 categorias
    ├── historico.json           # um dicionário por atendimento
    └── atendimentos.csv         # exportado com csv.DictWriter
```

### Classes (composição)

```
Assistente
 └── base: BaseConhecimento
      └── orientacoes: [Orientacao, Orientacao, ...]
```

| Classe | Atributos | Métodos |
|---|---|---|
| `Orientacao` | id, categoria, titulo, palavras_chave, resposta, documentos, onde, fonte, verificado_em | `de_dicionario()`, `exibir()` |
| `BaseConhecimento` | caminho, orientacoes | `carregar()`, `categorias()`, `por_categoria()`, `pontuar()`, `buscar()` |
| `Assistente` | nome, base, historico (+ caminhos dos arquivos e id da sessão) | `perguntar()`, `navegar()`, `registrar()`, `indicadores()`, `exportar_csv()`, `encerrar()` |

## Regra de pontuação usada

A pergunta é normalizada (minúsculas, sem acentos, sem pontuação) e comparada com cada orientação:

| Regra | Pontos |
|---|---|
| Palavra-chave da orientação que aparece na pergunta | +3 |
| Palavra da pergunta (4+ letras) que aparece no título | +1 |

| Melhor orientação | Resultado |
|---|---|
| 6 pontos ou mais | Confiança **ALTA** |
| 3 a 5 pontos | Confiança **MÉDIA** |
| Nenhuma com 3 pontos | "Não encontrei": sugere outras palavras e as categorias |

`buscar()` devolve uma **lista de tuplas `(pontos, orientacao)`**, da maior para a menor pontuação. O assistente mostra a melhor e até duas alternativas (se o cidadão disser que a primeira não ajudou).

**Exemplo real** – "Como faço a carteira de trabalho digital?":

- `carteira de trabalho` → +3
- `carteira de trabalho digital` → +3
- palavras no título "Habilitar a Carteira de Trabalho Digital": `carteira`, `trabalho`, `digital` → +3
- **Total: 9 pontos, confiança ALTA**.

Outro exemplo: "Como faço o cartão do SUS?" → `cartao do sus` (+3), `sus` (+3), `cartao` no título (+1) = **7 pontos, ALTA**.

**Ajustes feitos em relação ao padrão da atividade (explicados no vídeo):**

1. **Lista de palavras ignoradas (`STOPWORDS`)** na regra do título: palavras como "como", "para", "onde", "quero", "preciso" não geram ponto, porque aparecem em quase toda pergunta e dariam pontos falsos.
2. A normalização também troca hífen, barra e `º`/`ª` por espaço (assim "vale-transporte" e "13º" são entendidos).
3. A comparação usa espaços nas pontas das palavras, então `sus` só vale como palavra inteira.
4. Palavras-chave repetidas depois de normalizadas contam uma vez só.

## Regras de atendimento implementadas

- **Navegação por categorias** com "0 para voltar" em todas as telas.
- **Entradas inválidas** (letras, vazio, opção fora da faixa, s/n inválido) nunca encerram o programa.
- **Dados pessoais:** o assistente nunca pede nome, CPF, telefone ou e-mail. Pergunta com 8 ou mais dígitos ou com `@` é recusada e **não é registrada**.
- **Transparência:** toda resposta mostra fonte, data de verificação e o aviso "este assistente NÃO é um canal oficial".
- **Arquivos:** JSON da base ausente, corrompido ou com registros inválidos não trava o programa; histórico corrompido é guardado como `historico.json.corrompido` e um novo é iniciado.

## Histórico, indicadores e CSV

Cada atendimento vira um dicionário em `data/historico.json` com: `sessao`, `data`, `origem` (pergunta ou categoria), `pergunta`, `id_orientacao`, `encontrou`, `ajudou`, `tentativas`, `tempo_segundos` (medido com `time.time()`) e `nota_facilidade` (preenchida ao sair).

Indicadores exibidos: resposta encontrada (%), taxa de acerto/ajudou (%), tempo médio para encontrar, tentativas por atendimento, facilidade de uso (1 a 5) e lista de dúvidas sem solução. Os atendimentos são exportados para `data/atendimentos.csv` com `csv.DictWriter`.

## Integrações com outras disciplinas

Nenhuma. O projeto usa só a biblioteca padrão do Python; a busca por pontuação (obrigatória em PCP) é o único mecanismo de resposta.

## Fontes consultadas

Todas as orientações citam um site oficial no campo `fonte` do JSON:

- gov.br – portal do Governo Federal (conta gov.br, Carteira de Identidade Nacional)
- gov.br/trabalho-e-emprego – Ministério do Trabalho e Emprego (Carteira de Trabalho Digital, aprendizagem, direitos, vale-transporte); Portaria SEPRT nº 1.065/2019 (habilitação da Carteira de Trabalho Digital)
- gov.br/receitafederal – Receita Federal (CPF)
- tse.jus.br – Tribunal Superior Eleitoral (título de eleitor)
- gov.br/defesa – Ministério da Defesa (alistamento militar)
- gov.br/saude – Ministério da Saúde (Cartão SUS, vacinação)
- gov.br/inss – INSS (Meu INSS / CNIS)
- caixa.gov.br – Caixa (FGTS)
- consumidor.gov.br e planalto.gov.br – reclamações e Código de Defesa do Consumidor

## Resultado do teste com usuários

O teste foi feito **pelos próprios integrantes da equipe** (3 sessões de uso, uma por integrante), usando o assistente com perguntas sobre os temas da base. Não houve participantes de fora da equipe, e nenhum dado pessoal foi registrado. Os dados completos estão em `data/historico.json` e `data/atendimentos.csv`.

| Indicador | Resultado |
|---|---|
| Sessões de teste | 3 |
| Atendimentos | 11 |
| Resposta encontrada (%) | 90,9 |
| Taxa de acerto: ajudou (%) | 90,9 |
| Tempo médio para encontrar (s) | 20,1 |
| Tentativas por atendimento | 1,3 |
| Facilidade de uso (1 a 5) | 5,0 |

**Dúvida sem solução:** "Comprei um produto pela internet e quero devolver. Posso?" (nenhuma orientação atingiu 3 pontos).

**Problema encontrado no teste:** a pergunta "Quantas horas por dia um jovem aprendiz pode trabalhar?" mostrou a orientação sobre o contrato de Jovem Aprendiz (id 5, 8 pontos) em vez da orientação sobre jornada (id 6), porque a orientação certa não tinha palavras-chave para essa pergunta. O indicador de acerto, calculado pela resposta "s/n" dada no teste, não capta esse tipo de erro.

**Melhorias feitas a partir do teste** (palavras-chave novas no JSON):

- id 6 (jornada do aprendiz): `horas por dia`, `quantas horas`, `quantas horas por dia`. Com isso a pergunta acima passou a mostrar a orientação de jornada (11 pontos, confiança ALTA).
- id 17 (desistir de compra pela internet): `quero devolver`, `comprei um produto`. Com isso a dúvida sem solução passou a ser encontrada (7 pontos, confiança ALTA).

Os indicadores acima foram medidos **antes** dessas melhorias.

## Limitações

- A busca é por **regras e palavras-chave**: não entende sinônimos que não estejam no JSON nem erros de digitação.
- O teste foi feito apenas pela equipe, com 11 atendimentos; um teste com pessoas de fora poderia revelar mais dúvidas sem solução.
- O assistente só conhece as 17 orientações da base; fora disso responde "Não encontrei".
- As informações mudam (sites, prazos, regras): cada orientação traz a data de verificação e deve ser conferida de novo com o tempo.
- Dados pessoais são barrados só por regra simples (8+ dígitos ou `@`); um nome digitado na pergunta não é detectado.
- Os procedimentos de estados e cidades (RG, Poupatempo) variam; o assistente indica o caminho geral e a fonte oficial.
- **Este assistente não é um canal oficial** e não substitui o atendimento do órgão responsável.

## Vídeo técnico

[PREENCHER – link do YouTube (não listado)]

# A mineração de uma candidata — como funciona

Cópia dos diagramas do procedimento da análise (`docs/*procedimento-mineracao-candidatas*.md`, § "Como funciona"), para
quem usa a skill ver as etapas sem abrir os docs. **A fonte é o procedimento**: se os dois divergirem, vale ele.

Legenda: azul = determinístico (`[conferido]`); laranja = LLM (`[assistido]`, vale como hipótese); verde = decisão do
pesquisador.

## Uma rodada

```mermaid
flowchart TD
    P["Preparação comum<br/>versão do código · intake"]:::det
    P --> A["Auditor independente, em paralelo<br/>audit_recompute6 --json --unidade"]:::det
    P --> G["Parte genérica — mineracao_generica.ipynb<br/>G1 recorrência e escopo · G2 sub-unidades · G3 antes<br/>G4 depois · G5 estabilidade · G6 população"]:::det
    A --> E{"Encontro<br/>comparar_auditoria.py"}:::det
    G --> E
    E -- diverge --> X["Para: a divergência é o achado"]:::dec
    E -- igual --> R["Relatório da parte genérica<br/>com evidência por achado"]:::det
    R --> F{"Funil<br/>tabela do procedimento"}:::det
    F -- "notebook:&lt;nome&gt;" --> N["Notebook específico<br/>determinístico"]:::det
    F -- "investigação:candidata" --> I1["Leitura aberta, 2 leitores<br/>a lição e a causa em frase livre"]:::llm
    I1 --> GL{"Gate da lista<br/>o pesquisador aprova as categorias"}:::dec
    GL --> I["Leitura fechada, 2 leitores às cegas (≥ 20 casos)<br/>concordância por script · regras contadas"]:::llm
    F -- "fora da tabela" --> Y["Para: registrar a lição no funil"]:::dec
    N --> M["memoria_&lt;u&gt;_&lt;base&gt;.json<br/>no esquema da memória"]:::det
    I --> M
    M --> V{"validar_memoria.py"}:::det
    V -- aprovado --> D["Dossiê + arquivo final<br/>lição principal · leitores lado a lado · o resto"]:::det
    D --> PN["Painel valor_da_licao.py<br/>frequência × confiança → situação"]:::det
    PN --> H{"Gate do pesquisador<br/>a lição · o destino · notebook, monitorar ou investigar"}:::dec
    classDef det fill:#e8f1fb,stroke:#3b6ea5,color:#1b2b3a
    classDef llm fill:#fdf1e3,stroke:#b8742a,color:#3a2a1b
    classDef dec fill:#eaf6ea,stroke:#3f8a3f,color:#1b3a1b
```

- **A parte genérica** é a mesma para todas as lições. Ela descreve a lição (recorrência, sub-unidades, antes, depois,
  estabilidade) e grava a população. Ela não escreve a lição.
- **O funil** é uma tabela do procedimento: para cada lição, `notebook:<nome>` ou `investigação:candidata`.
- **O arquivo final** segue o esquema da análise (`analysis/esquema-memoria.json`). Cada campo diz se é `checado`
  (com o comando), `hipotese` ou `pendente`.

## O ciclo de vida da parte específica

```mermaid
flowchart LR
    S1["1 · Investigação por LLM<br/>toda lição nova começa aqui<br/>regras que funcionaram → regras.json"]:::llm
    S2["2 · Regras contadas<br/>testar_regra.py reconta a cada rodada"]:::det
    T{"Gatilho<br/>frequência (Pareto ou presença no tempo)<br/>+ confiança (2 leitores, ≥ 20 casos; regras contadas)<br/>+ gate: o pesquisador escolhe propor o notebook"}:::dec
    P["Proposta em propostas/&lt;u&gt;/<br/>racional.md (antes) · notebook rascunho"]:::llm
    V["Validador, outro agente<br/>2ª implementação a partir do racional<br/>confere notebook × racional × ordem"]:::det
    A{"Aprovação do pesquisador"}:::dec
    N["3 · Notebook específico no funil<br/>docs/ + pipeline/ + livro-razão"]:::det
    S1 --> S2 --> T
    T -- não --> S1
    T -- sim --> P --> V
    V -- reprovado --> S1
    V -- aprovado --> A
    A -- não --> S1
    A -- sim --> N
    classDef det fill:#e8f1fb,stroke:#3b6ea5,color:#1b2b3a
    classDef llm fill:#fdf1e3,stroke:#b8742a,color:#3a2a1b
    classDef dec fill:#eaf6ea,stroke:#3f8a3f,color:#1b3a1b
```

- **A leitura é em duas etapas.** Primeiro, os dois leitores escrevem a lição e a causa em frase livre. As frases
  viram uma lista de categorias, que o pesquisador aprova (o gate da lista). Só então os dois classificam, às cegas,
  pelo menos 20 outros casos, e o script mede a concordância. Assim a lista nasce dos casos, e o número continua saindo
  do script.
- **O painel para no gate do pesquisador** nas situações que pedem decisão: pronta para notebook; lição existe,
  redação em aberto; várias causas; certa, mas rara (monitorar). A decisão fica registrada (`registrar_decisao.py`).
- **Toda lição nova começa na investigação.** As regras que funcionam vão para o `regras.json` e são recontadas a cada
  rodada.
- **Um notebook específico só nasce pela regra de criação do procedimento:** frequência (a lição está no Pareto das
  ocorrências ou aparece na maior parte dos meses) mais confiança (dois leitores às cegas com pelo menos 20 casos, regras contadas, laudo do
  validador, e a decisão do gate); ou uma decisão do pesquisador. A cada partição nova da base, as regras são reaplicadas sem mudança.
  Se caírem, a lição volta à investigação. Ele nasce como proposta em `propostas/<u>/`, com o racional escrito
  antes, e passa pelo laudo do validador e pela aprovação do pesquisador.

# Evidência — nenhuma afirmação sem ela

O relatório de uma mineração é a análise final. Quem o lê tem de poder, a partir dele e sem refazer nada:
- **reproduzir** cada número, com o comando e os parâmetros;
- **abrir a tabela** de onde o número saiu, com o filtro;
- **abrir o trace cru** dos casos que sustentam a afirmação, sabendo quais são.

Afirmação sem isso não entra no relatório.

## O que cada afirmação leva

| Elemento | O que é | Obrigatório |
|---|---|---|
| **Reproduzir** | o comando exato, com os parâmetros, e de onde rodar | sempre |
| **Derivada** | a tabela (CSV ou a seção do notebook) de onde o número sai, com o filtro e o nº de linhas | sempre que existir tabela |
| **Crua** | os casos do trace: `exec_id` completo, papel e idx, e a pasta com o cru (`crus/<exec_id>.json`) e a visão conferida (`derivados/`) | em todo achado que vira decisão ou parada (candidata, dono, sucesso falso, não reconhecido, concentração principal) e sempre que houver casos por trás do número |
| **Recorte** | `drill_down.py caso <exec_id> <role>` (ou `--json`), que mostra a trajetória daquele caso | junto de cada caso cru |

Um número agregado sem casos por trás (por exemplo, uma proporção de detector) leva **reproduzir + derivada**. Um
achado que alguém vai usar para decidir leva **as quatro**.

## Como montar: `montar_evidencia.py`, um por achado

De qualquer lugar:

```
uv run python <skill mineracao-base>/scripts/montar_evidencia.py <pasta-da-analise> \
    --nome <mineracao>_<achado>_<BASE_ID> --de <tabela relativa a pipeline/resultados/> \
    --onde <coluna>=<valor> [--por <coluna>] \
    --afirmacao "<o que o achado diz>" --reproduzir "<comando que gera o número>"
```

O script faz quatro coisas:
- **escolhe os casos por regra fixa:** todos, se forem até 10; senão, o 1º de cada mês. Quando o filtro já fixa um
  mês (ou a população cai toda num mês), essa regra devolve um caso só: use `--regra semente --n 10`, a amostra
  sorteada com semente fixa, que é reproduzível. O script avisa quando isso acontece;
- **grava o cru e a visão de cada caso**, pelo `drill_down.py evidencia`, que confere cada trecho contra o cru;
- **escreve `origem.json`** com a tabela, os filtros, a regra, os tamanhos e os comandos;
- **escreve `bloco.md`**, o bloco pronto para o relatório.

Leve o bloco ao relatório com
`cat pipeline/resultados/evidencia/<nome>/bloco.md >> <relatório>`. **Não copie identificador à mão**, nem para o
relatório nem para a conversa: o script já escreveu certo.

## Sigilo

- **O relatório completo fica no ambiente onde o trace mora.** Ele tem identificador de execução, e
  `pipeline/resultados/` é git-ignored.
- **A versão que sai** (foto, chat, commit, mensagem) é feita por script, nunca à mão:
  ```
  uv run python <skill mineracao-base>/scripts/versao_para_sair.py <relatório>
  uv run python <skill mineracao-base>/scripts/varrer_pii.py <relatório>_saida.md
  ```
  O `_saida.md` troca cada identificador por `caso-N`. O `_mapa.csv` (caso-N → `exec_id`) fica no ambiente: é por ele
  que quem está lá volta da versão que saiu ao trace.

# Sigilo — o que pode e o que não pode sair do ambiente onde o trace mora

O trace cru tem nome de cliente, número de processo, CPF e trecho de documento jurídico em claro. Ele e tudo o que é
derivado dele ficam no ambiente onde o trace está.

- **O relatório completo fica no ambiente.** Ele leva a evidência de cada afirmação, inclusive os identificadores de
  execução das tabelas de evidência (`evidencia.md`), e mora em `pipeline/resultados/`, que é git-ignored.
- **Para fora** (a resposta no chat, um commit, uma foto, uma mensagem) só vai o que está na lista abaixo. No caso do
  relatório, vai a versão gerada pelo `versao_para_sair.py`.

## Pode sair

- contagens, percentuais, medianas;
- nomes de papel (agente), de ferramenta, de modelo, de unidade, de família e de grupo;
- meses (`AAAA-MM`), hashes, versões do kit;
- sim/não e as categorias fechadas que o procedimento define;
- motivos **mascarados** pelo próprio pipeline (o `--motivos` do `drill_down.py` já mascara);
- quando o procedimento pedir explicitamente: nomes de **campo** de um contrato de retorno (as chaves, nunca os
  valores).

## Não sai

- identificador de execução (`cod_idef_exeo` / `exec_id`), inteiro ou em prefixo. Na versão que sai, ele vira
  `caso-N`, e o mapa de volta fica no ambiente;
- texto de caso: pergunta, documento, resposta, observação, justificativa, pensamento do modelo;
- código escrito pelo agente, nome de variável do agente;
- texto de system prompt;
- mensagem de erro crua (só o nome do tipo de erro e a assinatura já mascarada).

## Como o agente trabalha com isso

1. **Leitura de caso é na tela do terminal; o texto do caso não vai para o relatório.** O agente pode ler um caso
   para classificá-lo (leitura `[assistido]`). No relatório entram a categoria, a contagem e a evidência (o
   identificador do caso, o caminho do cru e o comando de recorte), não o texto. Na resposta do chat, nem o
   identificador.
2. **Não improvisar máscara.** Mascarar à mão já falhou. Se um trecho de caso parece necessário, a resposta é
   "não sai", com a categoria.
3. **Arquivos com identificador ficam onde estão.** `pipeline/resultados/` é git-ignored. `casos.csv`, `crus/` e
   `derivados/` são lidos ali e não são copiados para fora.
4. **Antes de qualquer relatório sair:** rode `versao_para_sair.py <relatório>` e depois
   `varrer_pii.py <relatório>_saida.md`. Se o varredor sair com 1, a versão não sai. Ele não pega nome de pessoa nem
   texto de documento, então a leitura da versão que sai continua obrigatória.

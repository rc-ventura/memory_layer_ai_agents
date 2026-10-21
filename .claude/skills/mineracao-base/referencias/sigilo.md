# Sigilo — o que pode e o que não pode sair do ambiente onde o trace mora

O trace cru tem nome de cliente, número de processo, CPF e trecho de documento jurídico em claro. **A regra protege o
dado pessoal e o conteúdo do cliente; o conteúdo técnico sai.** Decisão do pesquisador em `analysis/decisoes.md`.

- **O relatório completo fica no ambiente.** Ele leva a evidência de cada afirmação e mora em `pipeline/resultados/`,
  que é git-ignored.
- **Para fora** (a resposta no chat, um commit, uma foto, uma mensagem) vai o que está em "Pode sair", **depois do
  `varrer_pii.py`**.

## Pode sair

- contagens, percentuais, medianas, tokens, tamanhos;
- nomes de papel (agente), de ferramenta, de modelo, de unidade, de família, de grupo, de módulo e de função;
- meses (`AAAA-MM`), hashes, versões do kit;
- identificador de execução (`cod_idef_exeo` / `exec_id`) e referência de passo (`step_ref`);
- mensagem de erro, código escrito pelo agente, nomes de variável, chamadas de ferramenta, texto de system prompt;
- sim/não e as categorias que o procedimento define;
- nomes de campo de um contrato de retorno.

Tudo isso **desde que não carregue dado pessoal ou conteúdo do cliente**: uma mensagem de erro ou um trecho de código
pode repetir um texto do documento (um literal, um valor impresso). Se carregar, o trecho não sai.

## Não sai

- dado pessoal: nome de pessoa, CPF, CNPJ, número de processo, e-mail, endereço, telefone;
- conteúdo do cliente ou do processo: o documento, a pergunta do usuário, a resposta final entregue a ele, os valores
  que as ferramentas devolvem sobre o caso.

## Como o agente trabalha com isso

1. **Leitura de caso é na tela do terminal.** No relatório entram a categoria, a contagem e a evidência (o
   identificador, o caminho do cru e o comando de recorte). Um trecho técnico pode ser citado; texto do cliente, não.
2. **Não improvisar máscara.** Se um trecho mistura técnica e conteúdo do cliente, a resposta é "não sai", com a
   categoria.
3. **Antes de qualquer coisa sair:** `varrer_pii.py <arquivo>`. Se ele sair com 1, não sai até remover o achado. Ele
   não pega nome de pessoa nem texto de documento, então a leitura do que sai continua obrigatória.
4. **O `versao_para_sair.py` é opcional:** troca os identificadores por `caso-N` (com o mapa de volta no ambiente),
   quando se quer uma versão mais curta.

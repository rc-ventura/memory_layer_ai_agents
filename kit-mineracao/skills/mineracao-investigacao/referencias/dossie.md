# Dossiê de decisão — esqueleto

Um dossiê por decisão, em `pipeline/resultados/dossie_<mineracao>_<decisao>_<BASE_ID>_<AAAA-MM-DD>.md` (git-ignored).
Todo número do dossiê sai de um script, e **o comando vai junto**. A leitura entra como categoria e contagem, marcada
`[assistido]`, com os casos que sustentam cada categoria. O dossiê completo fica no ambiente; para sair, use
`versao_para_sair.py` e `varrer_pii.py`.

```markdown
# Dossiê — <mineração> · <decisão> · <BASE_ID> · <AAAA-MM-DD>

## 1 · A pergunta
<uma frase; vem do roteiro da mineração>

## 2 · O que o determinístico já disse  [conferido]
<os números do relatório da rodada que motivam a pergunta, com a seção e o comando de onde vieram>

## 3 · Hipóteses
- H0 (nula): <o que se esperaria se nada de novo estivesse acontecendo>
- H1: …
- H2: …
<para cada uma: o que se veria no caso se ela fosse verdadeira>

## 4 · Amostra e evidência crua  [conferido]
<o bloco.md de resultados/evidencia/inv_<decisao>_<BASE_ID>/ — afirmação, comando, tabela derivada com filtro, os
casos com exec_id, o cru e o recorte>

## 5 · Leitura  [assistido]
| Categoria | Casos | Hipótese que apoia | Quais (o `#` da tabela de evidência) |
|---|---|---|---|
| … | … | … | #1, #4, … |
| indeterminado | … | — | … |
- leitura caso a caso: `pipeline/resultados/leitura_<decisao>_<BASE_ID>.csv` (com `exec_id`, o campo lido e
  `onde_no_cru`)

## 6 · Segundo leitor  [conferido]
- <K2> casos relidos às cegas · <a linha do concordancia.py> · discordâncias: <pares e contagens, com o # dos casos>
- reproduzir: `<o comando do amostrar.py da subamostra>` · `<o comando do concordancia.py>`

## 7 · Regra proposta e contagem  [conferido]
- regra: `<regex>` no campo `<campo>`, em palavras: <o que ela reconhece>
- <as linhas do testar_regra.py: população, pega certo / a mais / deixa de pegar>
- reproduzir: `<o comando do testar_regra.py, com todos os parâmetros>` · com `--saida`, o CSV caso a caso
  (`exec_id`, `role`, idx, casou) em `resultados/regra_<decisao>_<BASE_ID>.csv`

## 8 · Decisão para o pesquisador
- opções: (a) … (b) … (c) não decidir agora: o que faltaria
- recomendação: <opção> — <por quê, em uma frase> — confiança: alta | média | baixa
- o que mudaria a recomendação: <o achado que a derrubaria>
- se a regra entrar: é um *Ajuste* se mudar número publicado. Onde ela entraria, e o que mudaria (contagens)

## 9 · Sigilo
- versão que sai: `_saida.md` (`versao_para_sair.py`) · `varrer_pii.py`: limpo
```

**Recusas:** o dossiê não fecha se faltar a seção 4 (a evidência crua), a 6 ou a 7, ou se algum número não tiver o comando que o produziu. A recomendação nunca vem sem a hipótese nula
discutida. Quando a amostra não basta para separar as hipóteses, a recomendação é "não decidir agora", dizendo o que
faltaria.

# Exemplo real — minerar as falhas silenciosas de uma base nova, do zero

Esta é uma rodada de verdade, feita em 05/10/2026 (refeita com o kit 0.3.0, que põe evidência em todo achado). Ela simula a chegada de uma base nova:
- uma pasta de análise `2026-10-base3-simulada`, com `BASE_ID = "base3"`;
- o trace em **parquet tipado**;
- a pasta `pipeline/resultados/` **vazia**: nenhuma tabela, nenhum relatório.

O dado é o da base 1 convertido. Por isso dá para conferir que os números são os conhecidos, mas a skill não sabia
disso: ela não compara com relatório nenhum.

As saídas abaixo foram copiadas da rodada; a do encontro (2.4) está resumida em linhas agrupadas. Só há contagens,
nomes de ferramenta e motivos mascarados.

---

## 1 · O que você digita

```
# uma vez por repositório (ou depois de atualizar o kit)
python kit-mineracao/instalar.py . --para claude        # ou --para copilot

# a rodada
/rodada-silenciosas analysis/<pasta-da-base-nova>

# depois, para cada parada que você quiser abrir
/investigar silenciosas S3 analysis/<pasta-da-base-nova>
```

Sem os prompts, funciona igual em linguagem natural: "minere as falhas silenciosas da análise X". As skills disparam
pela descrição.

---

## 2 · O que acontece por baixo, na ordem

```
preparação ──┬──► mineração (lê as tabelas) ──┐
             └──► auditor (em paralelo) ───────┴─► encontro ──► relatório ──► você escolhe uma parada ──► investigação ──► dossiê
```

### 2.1 Preparação — skill `mineracao-base`

| O que | Comando | O que saiu nesta rodada |
|---|---|---|
| qual base, qual trace | uma linha de Python que lê o `base_pipeline.py` | `base: base3 \| trace: parquet \| 256 MB` |
| o código é o do kit? | `conferir_versao.py <pasta>` | 9 arquivos `ok` → `versão do código: IGUAL ao manifesto` |
| o arquivo abre direito? | `checklist.py` | §0: `parquet`, colunas `int64` / `timestamp[us]` / `dictionary` convertidas para texto; 1000 linhas; 840 memórias; **0 quebradas** |

Se a versão do código fosse diferente, ou se alguma memória do parquet não parseasse, a rodada pararia aqui.

### 2.2 O auditor dispara em paralelo — agente `auditor-independente`

- **Antes de disparar:** como a base estava do zero, a skill rodou o notebook da esteira para gerar o
  `erros_mecanismo.csv` (o balde visível), de que o auditor precisa.
- **O agente recebeu um comando só**, sem acesso ao pipeline nem às tabelas:
  ```
  audit/scripts/audit_recompute9.py --base base3 --trace data/base3.parquet --json pipeline/resultados/auditoria_silenciosas_base3.json
  ```
- **O que ele faz:** recalcula as medidas direto do trace, com outra implementação, e grava o JSON. Numa base sem
  números conhecidos, o script imprime tudo como "a conferir" e termina com `DIVERGÊNCIAS: 0`.

### 2.3 A mineração — skill `mineracao-silenciosas`

Enquanto o auditor roda, a skill gera as tabelas desta base (o notebook das silenciosas, o
`drill_down.py silenciosas`, o `--motivos`, o `--forma` e a consolidação) e as lê passo a passo do procedimento da
análise. O que ela achou está no relatório (§3 abaixo).

### 2.4 O encontro — `comparar_auditoria.py`

O script confronta as tabelas da mineração com o JSON do auditor:

```
medida                                                    tabelas    auditoria
silenciosas                                                   120          120  OK
steps_silenciosos                                             119          119  OK
execucoes / meses / papeis / ferramentas                90/10/13/22  90/10/13/22  OK
grupo argumento_do_agente / plataforma / ...               41/19/…      41/19/…  OK
sucesso falso total (candidatos/reais)                   [54, 75]     [54, 75]  OK
steps silenciosos da unidade U_repr_colado                      6            6  OK
...                                                     (19 medidas, todas OK)

conferências internas (valem em qualquer base):
  OK    soma dos grupos = silenciosas (tabelas)
  OK    silenciosas que caíram no balde visível = 0 (auditoria)

auditoria × tabelas: tudo igual
```

Esta é a verificação sem relatório: duas implementações independentes chegaram nos mesmos números. Se alguma linha
desse DIVERGE, a rodada pararia, e a divergência seria o achado.

### 2.5 A evidência de cada achado — `montar_evidencia.py`

Para cada achado que vira decisão ou parada, a skill monta uma pasta de evidência por regra fixa, com o cru de cada
caso. Nesta rodada foram seis, e todos os trechos das visões foram conferidos contra o cru:

```
silenciosas_funil_base3              população 120 · casos 10 · 10 crus · trechos conferidos 96/96
silenciosas_ferramenta_base3         população  57 · casos  9 ·  9 crus · 79/79
silenciosas_nao_reconhecido_base3    população   9 · casos  9 ·  8 crus · 85/85
silenciosas_dono_json_invalido_base3 população   6 · casos  6 ·  6 crus · 66/66
silenciosas_sucesso_falso_base3      população  54 · casos 23 · 22 crus · 225/225   (1º de cada mês, por grupo)
silenciosas_unidade_U_repr_colado_base3  população 6 · casos 6 · 6 crus · 66/66
```

Cada pasta tem `casos.csv` (a evidência derivada), `crus/` (a linha inteira do trace), `derivados/` (a visão
conferida), `origem.json` e o `bloco.md`. O bloco entra no relatório por `cat`, sem ninguém digitar identificador.

### 2.6 O relatório e o sigilo

- **O relatório completo** está em `pipeline/resultados/relatorio_silenciosas_base3_2026-10-05.md` (198 linhas,
  git-ignored). Ele tem os `exec_id` reais. O varredor o bloqueia (126 ocorrências), como deve: ele fica no ambiente.
- **A versão que sai**, `…_saida.md`, sai do `versao_para_sair.py`, que trocou 38 identificadores por `caso-N`.
  O `varrer_pii.py` deu `limpo — pode sair`. O mapa `caso-N → exec_id` (`…_mapa.csv`) fica no ambiente.

---

## 3 · O relatório que a rodada produziu

**Como fica um achado com a evidência.** É o passo 4, copiado da versão que sai:

```markdown
### Passo 4 · Dono dos grupos a conferir
- json_invalido: 6 de 6 no `busca_obf`, todas com o argumento colado de um retorno impresso → a forma decide: do agente.
- **Reproduzir:** `uv run python drill_down.py silenciosas --forma busca_obf` · **Derivada:** `casos.csv`, `grupo=json_invalido` e `ferramenta=busca_obf` → 6 linhas

#### Evidência · `silenciosas_dono_json_invalido_base3`
- **Afirmação:** as 6 falhas json_invalido são do busca_obf, todas com o argumento colado de um retorno impresso: o dono é o agente
- **Reproduzir** (de dentro de `pipeline/`): `uv run python drill_down.py silenciosas --forma busca_obf`
- **Derivada:** `resultados/evidencia/silenciosas/casos.csv`, `grupo=json_invalido` e `ferramenta=busca_obf` → 6 linha(s); 6 escolhida(s) pela regra *todos (até 10)* → `resultados/evidencia/silenciosas_dono_json_invalido_base3/casos.csv`
- **Crua:** `resultados/evidencia/silenciosas_dono_json_invalido_base3/crus/<exec_id>.json` (a linha inteira do trace) e `…/derivados/` (a visão de cada caso, com o caminho no cru) — 6 casos · 6 crus (0.6 MB) · trechos conferidos contra o cru: 66/66

| # | exec_id | papel | idx | mes | ferramenta | grupo | recorte do trace |
|---|---|---|---|---|---|---|---|
| 1 | `caso-8` | RoteadorCivel | 1 | 2026-05 | busca_obf | json_invalido | `uv run python drill_down.py caso caso-8 RoteadorCivel` |
| 2 | `caso-25` | RoteadorCivel | 1 | 2026-05 | busca_obf | json_invalido | `uv run python drill_down.py caso caso-25 RoteadorCivel` |
| … | (6 linhas) | | | | | | |
```

No relatório completo, cada `caso-N` é o `exec_id` real, e o comando de recorte roda direto.

**O resumo dos achados** (no relatório, cada linha abaixo tem o bloco acima):

> Rodada de demonstração: "base3" simulada, com o trace da base 1 convertido em parquet tipado e a pasta de resultados
> vazia (mineração do zero).

**0 · Identificação**
- kit 0.2.0
- base3 · parquet · 1000 linhas · 840 com memória (0 quebradas)
- versão do código: IGUAL ao manifesto · intake: passou

**1 · Entradas:** todas geradas nesta rodada (balde visível, `casos.csv`, `ocorrencias.csv`, saídas dos notebooks).

**2 · Achados, passo a passo** [conferido]

| Passo | O que as tabelas mostram |
|---|---|
| 1 · Funil | 9 falhas de ferramenta com exceção × **120 silenciosas**, ou seja, **93% são invisíveis**; elas estão em 119 steps, 90 execuções, 10 meses, 13 papéis e 22 ferramentas; sobreposição dos baldes 0 |
| 2 · Por ferramenta | `get_available_documents` concentra 57 de 120 (48%); taxas altas em ferramentas pequenas: `table_statistical_summary` 8/10, `compare_documents` 13/48 |
| 3 · Grupos | sem_resultado 43 · argumento_do_agente 41 · plataforma 19 · **nao_reconhecido 9** · json_invalido 6 · fora_da_cobertura 2 → 75 falhas reais |
| 4 · Dono | json_invalido: 6 de 6 no `busca_obf`, todas com o argumento colado de um retorno impresso → a forma decide (do agente) |
| 5 · Depois | 107/120 sem erro nos 3 steps seguintes; contrato de retorno precedido por silenciosa: 4/47, 1/96, 0/10 (abaixo de um terço) |
| 6 · Sucesso falso | teto de **54/75** (argumento 30/41, plataforma 16/19, não reconhecido 8/9, json 0/6) |
| 7 · Detectores | 90 ferramentas declaradas, 80 chamadas; retorno ignorado 103/3.053; chamada repetida 125; sem ferramenta 10/840 |
| 8 · Consolidação | steps nos dois canais 0; o canal silencioso leva a unidade do retorno colado de 6 para 12 ocorrências; nenhuma decisão muda |

**3 · Verificação:** auditoria × tabelas, tudo igual (19 medidas); 4 conferências internas OK.

**4 · Paradas**

| Parada | Pergunta | Motivo |
|---|---|---|
| Passo 3 | **S3** · o que o `nao_reconhecido` é | 9 falhas sem regra, 6 em `get_available_documents` |
| Passo 6 | **S2** · a resposta usou o dado que não veio? | 54 candidatos em 3 grupos |
| Passo 4 | S1 não abre | a forma decide o dono |

**5 · Falhas de comando:** nenhuma. **6 · Sigilo:** versão que sai limpa (38 identificadores → `caso-N`).

---

## 4 · Depois: investigar uma parada — skill `mineracao-investigacao`

Você escolhe a parada, por exemplo `/investigar silenciosas S3`. A skill segue o roteiro `silenciosas`.

| Etapa | Quem faz | Nesta rodada |
|---|---|---|
| 1. Hipóteses **antes** de ler | o agente, a partir do roteiro | H0: são motivos de grupos existentes, e falta palavra-chave · H1: é um grupo novo |
| 2. Quais casos ler | `montar_evidencia.py --nome inv_s3_base3 …`, por regra fixa, já com o cru de cada caso | `população 9 · casos 9 · 8 crus · 85/85` (todos, porque são até 10) |
| 3. Ler e classificar | agente `investigador` | **não executado aqui**: é a leitura do caso cru, feita no ambiente do trace e com sua autorização |
| 4. Reler às cegas | `amostrar.py --regra semente --n 5` + agente `segundo-leitor` | subamostra sorteada: `população 9 · amostra 5` (a leitura também não foi executada) |
| 5. Concordância | `concordancia.py` | número de script, no formato `casos em comum: 5 · concordam: … · kappa: …` (não executado: depende da leitura) |
| 6. Hipótese → regra contada | `testar_regra.py` | veja o exemplo da S2 abaixo |
| 7. Dossiê | esqueleto `dossie.md` + `varrer_pii.py` | pergunta, hipóteses, contagens, opções, recomendação: **a decisão é sua** |

**Exemplo da etapa 6, que é real.** Na S2, uma regra candidata para "a resposta declara a falha" (palavras como "não
foi possível", "indisponível", "erro", "failed"), aplicada à saída final de cada candidato:

```
testar_regra.py <pasta> --populacao casos.csv --onde sucesso_falso_candidato=True \
    --campo-passo action_output --coluna-idx idx_final_depois --ignorar-caixa --regex '<a regra>'

população: 54 linhas, 47 steps distintos · regra casa em 30 (64%)
```

Com a leitura do investigador (`--lidos leitura.csv --rotulo declara --alvo sim`), a mesma linha passaria a dizer quantos
casos a regra pega certo, quantos pega a mais e quantos deixa de pegar. Esse é o número que vai para o dossiê, e não a
opinião do modelo.

---

## 5 · O que cada peça garante

| Peça | Garante |
|---|---|
| `conferir_versao.py` | que você está minerando com o código para o qual o kit foi escrito |
| `checklist.py` §0 | que o arquivo (CSV ou parquet) foi lido sem corromper nada |
| auditor em paralelo + `comparar_auditoria.py` | que os números da base estão certos **sem precisar de relatório anterior** |
| `montar_evidencia.py` / `amostrar.py` | que o LLM não escolhe o que ler, e que todo achado tem o comando, a tabela e os casos crus |
| `versao_para_sair.py` | que o relatório sai sem identificador, por script, e com o mapa de volta no ambiente |
| `segundo-leitor` + `concordancia.py` | que a categoria está bem definida (se dois leitores discordam, ela não está) |
| `testar_regra.py` | que a hipótese do LLM vira número determinístico antes de chegar a você |
| `varrer_pii.py` | que nada com CPF, número de processo ou identificador de execução sai do ambiente |

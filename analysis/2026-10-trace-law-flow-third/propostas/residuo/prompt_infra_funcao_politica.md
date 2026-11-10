Você vai rodar **uma contagem por script** sobre o grupo "infra / LLM" do resíduo da base 3 (54 erros, rodada
`13b0d026242de2dc`). Não há leitura de caso aqui: o script responde duas dúvidas que a leitura deixou abertas.
- qual função (ferramenta) está na linha que falhou e qual é o padrão mascarado de cada grupo;
- nos 5 erros `BadRequestError`, se a mensagem fala do filtro de conteúdo ou do limite de contexto/tokens.

**Não edite nenhum arquivo do repositório** (o script só grava `infra_funcao_politica.txt`, em `resultados/`, que é
git-ignored), não instale nem atualize pacotes e use `uv run --no-sync`. Rode **da raiz do repositório**, em Git Bash.
Não interprete o resultado: só devolva.

**Passo 1 · Rodar.** Cole exatamente isto no terminal:

```bash
export PYTHONIOENCODING=utf-8
uv run --no-sync python - <<'EOF'
import pandas as pd, re
B = 'analysis/2026-10-trace-law-flow-third/pipeline/resultados'
R = f'{B}/mineracao/residuo/residuo_13b0d02'
SAIDA = f'{B}/evidencia/infra_funcao_politica.txt'

def limpa(p):  # tira URL e nome de máquina antes de gravar
    return re.sub(r'https?://\S+|\b[\w-]+(?:\.[\w-]+){2,}\b', '<url>', str(p))[:110]

# 1) função na linha e padrão, por grupo (casos_infra.csv) + o "depois" da leitura
I = pd.read_csv(f'{R}/casos_infra.csv', dtype={'exec_id': str, 'agente': str})
L = pd.read_csv(f'{B}/evidencia/leitura_infra_residuo_todos.csv', dtype={'exec_id': str})
for X in (I, L):
    X['idx'] = X['idx'].astype(int)
I = I.merge(L[['exec_id', 'role', 'idx', 'depois']], on=['exec_id', 'role', 'idx'], how='left')
out = [f'erros no grupo: {len(I)} · sem leitura: {int(I.depois.isna().sum())}', '']
for g, d in I.groupby('grupo'):
    out.append(f"== {g}: {len(d)} erros, {len(d[['exec_id', 'agente']].drop_duplicates())} execuções")
    out.append('  função na linha: ' + str(d.funcao_na_linha.value_counts().to_dict()))
    out.append('  meses: ' + str(d.mes.value_counts().sort_index().to_dict()))
    out.append('  tipo do erro: ' + str(d.err_type.value_counts().to_dict()))
    out.append('  padrões:')
    out += [f'    {n:3d}  {p}' for p, n in d.padrao.map(limpa).value_counts().items()]
    out.append('  função × depois: ' + str(d.groupby(['funcao_na_linha', 'depois']).size().to_dict()))
    out.append('')

# 2) palavras-chave nas mensagens BadRequestError / ContentPolicyViolation (casos.csv); só contagens
C = pd.read_csv(f'{R}/casos.csv', dtype={'exec_id': str})
m = C.mensagem.fillna('').astype(str)
P = m[m.str.contains(r'\bBadRequestError\b|ContentPolicyViolation')]
T = {'content_policy': r'(?i)content.?policy', 'content_filter': r'(?i)content.?filter',
     'responsible_ai': r'(?i)ResponsibleAI', 'jailbreak': r'(?i)jailbreak',
     'categoria_do_filtro': r'(?i)\b(?:hate|sexual|violence|self.?harm)\b',
     'context': r'(?i)\bcontext', 'token': r'(?i)token', 'length': r'(?i)length', 'limit': r'(?i)limit',
     'too_long_ou_exceed': r'(?i)too long|exceed', 'ContextWindowExceeded': r'ContextWindowExceeded',
     'litellm': r'(?i)litellm', 'codigo_400': r'\b400\b'}
out.append(f'== palavras-chave nas mensagens BadRequestError/ContentPolicyViolation: {len(P)} mensagens')
out += [f'  {k}: {int(P.str.contains(rx).sum())}' for k, rx in T.items()]
out.append('  classes: ' + str(sorted({c for x in P for c in re.findall(r'\b\w+(?:Error|Exception|Violation)\b', x)})))

open(SAIDA, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('ok:', len(I), 'erros no grupo ·', len(P), 'mensagens BadRequest →', SAIDA)
EOF
uv run --no-sync python .github/skills/mineracao-base/scripts/varrer_pii.py analysis/2026-10-trace-law-flow-third/pipeline/resultados/evidencia/infra_funcao_politica.txt && cat analysis/2026-10-trace-law-flow-third/pipeline/resultados/evidencia/infra_funcao_politica.txt
```

O esperado é `ok: 54 erros no grupo · 5 mensagens BadRequest → …`, o `varrer_pii` limpo e o arquivo na tela.

**Passo 2 · Conferir antes de devolver.**
- Se o `varrer_pii` acusar algo, **não mostre o arquivo**: devolva só o tipo do achado e o grupo em que está.
- Se algum padrão tiver nome de sistema interno, de pessoa ou trecho de documento, troque essa linha por
  `<removido: grupo X>` na sua resposta (não no arquivo) e diga isso.
- Se o comando der erro, devolva só o texto do erro.

**Passo 3 · Devolver.** Só a linha `ok:` e o conteúdo do `infra_funcao_politica.txt`, sem comentário.

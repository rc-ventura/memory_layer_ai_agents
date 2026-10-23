"""A recuperação depois do erro, por execução e por papel (decisão do Rafael, 23/10): o censo dos erros da base 3.

O gráfico "o que vem depois do erro" da parte 1 conta por **erro** e só vê o passo seguinte: uma cascata de 5 erros
entra 4 vezes como "errou de novo". Aqui a conta é por **trajetória** — o papel numa execução (execução × agente ×
papel) — e vai até o fim do papel:

- **A base 3 tem todos os erros estruturados de cada papel** (a junção com as contagens confere, chave a chave, que o
  número de erros é o mesmo). Então, depois do último erro do papel, nenhum ActionStep tem erro estruturado até o fim.
- **As sequências saem dos vizinhos que a query traz, não da numeração.** `next_error_type` preenchido = o ActionStep
  seguinte também errou (a cascata continua); vazio = houve pelo menos um passo sem erro estruturado entre os dois
  erros. `next_step_number` vazio no último erro = não há ActionStep depois dele (o papel terminou no erro). O
  `step_number` não serve de posição: na base 1, 30% dos ActionSteps têm `step_number` diferente da posição no papel,
  porque ele recomeça quando o papel é chamado de novo (`validacao/conferir_recuperacao_base1.py`).
- **O limite de passos não é recuperação.** Um papel com o erro "Reached max steps" (a família "Erro crítico" da
  genealogia, a mesma regra de texto do `base_pipeline.classify`) esgotou os passos: o passo forçado depois dele não é
  o agente se recuperando. Categoria própria, que vence as de "seguiu sem erro".
- **Cada par de erros vizinhos é conferido** (o "seguinte errou" de um bate com o "anterior errou" do outro, e o número
  do passo seguinte bate com o do próximo erro). Se não bate — ou o papel aparece com mais de um agente na mesma
  execução, que a partição da query (execução × papel, sem o agente) mistura —, a trajetória é **indeterminada**:
  contada, não escondida.

Só contagens saem daqui: as tabelas gravadas não têm identificador de execução. "Sem erro até o fim" não é sucesso:
a qualidade da resposta não está na base, e falha silenciosa não é erro estruturado.
"""
import pandas as pd

CHAVE = ["cod_idef_exeo", "cod_idef_aget", "papel"]
COLUNAS = ["step_pos", "step_number", "error_message", "next_step_number", "next_error_type", "next_error_like",
           "prev_error_type", "execution_has_final_step"]
LIMITE_DE_PASSOS = ("Reached max steps", "AgentMaxStepsError")   # o mesmo texto do base_pipeline.classify (Ajuste 8)

# (chave, rótulo, cor) — a ordem é a das barras; verdes = seguiu sem erro até o fim, vermelho = terminou no erro
CATEGORIAS = [("um_erro", "um erro, depois sem erro até o fim", "#1b4332"),
              ("cascata", "cascata (errou de novo em seguida), depois sem erro até o fim", "#52b788"),
              ("recaida", "recaída (errou de novo mais adiante), depois sem erro até o fim", "#b7e4c7"),
              ("terminou_no_erro", "terminou no erro (o último passo do papel errou)", "#9d0208"),
              ("limite_de_passos", "esgotou os passos (limite de passos)", "#0b0b0b"),
              ("indeterminado", "indeterminado (vizinhos não conferem)", "#e0dfd8")]
CATEGORIAS_EXEC = [("sem_erro", "sem erro estruturado", "#c3c2b7"),
                   ("recuperou", "errou, e todo papel seguiu sem erro até o fim", "#1b4332"),
                   ("nao_recuperou", "algum papel terminou no erro ou esgotou os passos", "#9d0208"),
                   ("indeterminado", "indeterminado", "#e0dfd8")]
ROTULO = dict((k, r) for k, r, _ in CATEGORIAS + CATEGORIAS_EXEC)


def _vazio(s):
    return s.isna() | s.astype(str).str.strip().isin(["", "nan", "None", "<NA>"])


def trajetorias(fonte):
    """Uma linha por trajetória com erro estruturado: erros, sequências, como termina, a categoria e o motivo se
    indeterminada. `fonte` = as linhas da v2 (as chaves em texto). Tem a chave: não sai do ambiente."""
    f = fonte.copy()
    for c in ["structured_error", "step_pos", "step_number", "next_step_number", "next_error_like",
              "execution_has_final_step"]:
        f[c] = pd.to_numeric(f[c], errors="coerce")
    e = f[f.structured_error.eq(1)].sort_values(CHAVE + ["step_pos"]).reset_index(drop=True)
    seguido = ~_vazio(e.next_error_type)                 # o ActionStep seguinte também tem erro estruturado
    anterior_errou = ~_vazio(e.prev_error_type)
    g = e.groupby(CHAVE, sort=False)
    ultimo = g.cumcount(ascending=False).eq(0)
    primeiro = g.cumcount().eq(0)
    prox_anterior_errou = anterior_errou.groupby([e[c] for c in CHAVE], sort=False).shift(-1)
    prox_numero = e.groupby(CHAVE, sort=False).step_number.shift(-1)
    # os vizinhos conferem: o "seguinte errou" de um erro = o "anterior errou" do próximo erro do papel; o último erro
    # não pode ter o seguinte com erro (o erro estaria fora do censo); o primeiro não pode ter o anterior com erro
    par_ok = ultimo | (seguido.eq(prox_anterior_errou.astype("boolean")).fillna(False).astype(bool)
                       & (~seguido | e.next_step_number.isna() | prox_numero.isna()
                          | e.next_step_number.eq(prox_numero)))
    e["_falha_par"] = ~par_ok
    e["_falha_ultimo"] = ultimo & seguido
    e["_falha_primeiro"] = primeiro & anterior_errou
    e["_quebra"] = ~seguido & ~ultimo                     # um passo sem erro antes do próximo erro: nova sequência
    e["_suspeita_depois"] = ultimo & ~seguido & e.next_error_like.eq(1)
    msg = e.error_message.fillna("").astype(str)
    e["_limite"] = msg.str.contains(LIMITE_DE_PASSOS[0], regex=False) | msg.str.contains(LIMITE_DE_PASSOS[1], regex=False)
    agentes = f.groupby(["cod_idef_exeo", "papel"]).cod_idef_aget.nunique()
    t = e.groupby(CHAVE, sort=False).agg(
        erros=("step_pos", "size"), quebras=("_quebra", "sum"), falha_par=("_falha_par", "any"),
        falha_ultimo=("_falha_ultimo", "any"), falha_primeiro=("_falha_primeiro", "any"),
        suspeita_depois=("_suspeita_depois", "any"), limite=("_limite", "any"), resposta_final=("execution_has_final_step", "max"),
        terminou=("next_step_number", lambda s: bool(pd.isna(s.iloc[-1])))).reset_index()
    t["sequencias"] = t.quebras + 1
    multi = t.set_index(["cod_idef_exeo", "papel"]).index.map(agentes).to_numpy() > 1
    t["motivo_indeterminado"] = None
    for col, motivo in [("falha_primeiro", "o anterior ao primeiro erro também errou (erro fora do censo)"),
                        ("falha_ultimo", "o seguinte ao último erro também errou (erro fora do censo)"),
                        ("falha_par", "os vizinhos de dois erros não conferem")]:
        t.loc[t[col] & t.motivo_indeterminado.isna(), "motivo_indeterminado"] = motivo
    t.loc[multi, "motivo_indeterminado"] = "mais de um agente com o papel na execução (a query não separa)"
    t["categoria"] = "recaida"
    t.loc[t.sequencias.eq(1), "categoria"] = "cascata"
    t.loc[t.erros.eq(1), "categoria"] = "um_erro"
    t.loc[t.terminou, "categoria"] = "terminou_no_erro"
    t.loc[t.limite, "categoria"] = "limite_de_passos"
    t.loc[t.motivo_indeterminado.notna(), "categoria"] = "indeterminado"
    return t[CHAVE + ["erros", "sequencias", "terminou", "limite", "resposta_final", "suspeita_depois", "categoria",
                      "motivo_indeterminado"]]


def execucoes(traj, cont):
    """Uma linha por execução (execução + agente) das contagens, com a categoria: sem erro, recuperou, não recuperou
    (algum papel terminou no erro ou esgotou os passos), indeterminado — o pior dos papéis manda. Sem a chave na saída."""
    ok = cont[cont.qtd_actionsteps.notna()]
    papeis = ok[CHAVE + ["qtd_erros_estruturados"]].merge(traj[CHAVE + ["categoria"]], on=CHAVE, how="left")
    # papel com erro nas contagens e sem trajetória na fonte: indeterminado (a junção conferida não deixa acontecer)
    papeis.loc[papeis.qtd_erros_estruturados.gt(0) & papeis.categoria.isna(), "categoria"] = "indeterminado"
    def pior(cats):
        cats = set(cats.dropna())
        if not cats:
            return "sem_erro"
        if cats & {"terminou_no_erro", "limite_de_passos"}:
            return "nao_recuperou"
        return "indeterminado" if "indeterminado" in cats else "recuperou"
    return papeis.groupby(["cod_idef_exeo", "cod_idef_aget"]).categoria.agg(pior).rename("categoria").reset_index(drop=True)


def tabelas(fonte, cont):
    """As tabelas sem identificador: a população (execuções e trajetórias com erro), por papel e os motivos dos
    indeterminados. Devolve (populacao, por_papel, motivos, extra)."""
    traj = trajetorias(fonte)
    ex = execucoes(traj, cont)
    linhas = [("execuções", k, int(ex.eq(k).sum()), len(ex)) for k, _, _ in CATEGORIAS_EXEC]
    linhas += [("papéis com erro", k, int(traj.categoria.eq(k).sum()), len(traj)) for k, _, _ in CATEGORIAS]
    pop = pd.DataFrame(linhas, columns=["nivel", "categoria", "n", "total"])
    pop["pct"] = 100 * pop.n / pop.total.where(pop.total.gt(0))
    pop["rotulo"] = pop.categoria.map(ROTULO)
    ok = cont[cont.qtd_actionsteps.notna()]
    por_papel = (traj.groupby(["papel", "categoria"]).size().unstack(fill_value=0)
                 .reindex(columns=[k for k, _, _ in CATEGORIAS], fill_value=0))
    por_papel["com_erro"] = por_papel.sum(axis=1)
    por_papel["execucoes"] = ok.groupby("papel").size().reindex(por_papel.index).fillna(0).astype(int)
    por_papel["erros"] = traj.groupby("papel").erros.sum()
    por_papel["com_resposta_final"] = traj.groupby("papel").resposta_final.apply(lambda s: int(s.eq(1).sum()))
    por_papel = por_papel.sort_values("com_erro", ascending=False).reset_index()
    motivos = (traj.motivo_indeterminado.value_counts().rename_axis("motivo").reset_index(name="papeis"))
    extra = {"trajetorias": len(traj), "erros": int(traj.erros.sum()),
             "erros_em_cascata": int((traj.erros - traj.sequencias).sum()),
             "suspeita_logo_depois_do_ultimo": int(traj.suspeita_depois.sum()),
             "com_resposta_final": int(traj.resposta_final.eq(1).sum()),
             "terminou_no_erro_com_um_erro": int((traj.categoria.eq("terminou_no_erro") & traj.erros.eq(1)).sum())}
    return pop, por_papel, motivos, extra

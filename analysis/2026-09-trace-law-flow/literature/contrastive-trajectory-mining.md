> **Fichamento temático breve (dois papers) — tier abaixo dos quatro 🔎 desta pasta.** Bibliografia conferida por busca web em 2026-09-09; **não conferida no PDF primário**; texto completo não lido. Estatísticas "conforme reportado na busca". `Lido por Rafael: não`.

# Contraste sucesso/falha de trajetória → regra reutilizável

Dois papers com a mesma tese central: **a variação de resultado em trajetórias da mesma tarefa é supervisão de graça** — a diferença entre uma execução que deu certo e uma que deu errado carrega mais sinal do que qualquer das duas isolada. Ambos são a ponte entre "analisar o trace" e "construir a unidade de memória" (roadmap: *"Construir os candidatos de memória de verdade, reusando este pipeline"*).

## CONTRAMEM — Learning Self-Evolving Procedural Memory from Contrasting Multi-Model Trajectories

- **Autores:** Zheyuan Deng, Binghang Lu, Hanqi Feng, Shirley Huang, Dianzhuo Wang, Yuanda Xu, Zhiwei Zhang, Yige Sun, Changhong Mou, Runyu Zhang, Yuexing Hao, Barnabas Poczos, Xiaomin Li
- **Ano:** 2026 (submetido 23/08/2026) · **Venue:** arXiv:2608.22533 · **Link:** <https://arxiv.org/abs/2608.22533>
- Framework **training-free**. Trata diferenças de correção, eficiência, recuperação e modo de falha entre trajetórias da mesma tarefa como distinções procedurais relevantes ao resultado. Destila num banco compacto de **Function Cards** (nível de app) e **Skill Cards** (nível de tarefa), que evolui por **curadoria localizada** — não por acúmulo append-only, nem por reescrita do banco inteiro.
- Resultado reportado: em tarefas computer-use held-out de GAIA2/ARE, mais que dobra a taxa de sucesso (**26,2% → 55,3%**) nos três modelos-fonte.

## Self-Consolidation for Self-Evolving Agents

- **Autores:** Hongzhuo Yu, Fei Zhu, Guo-Sen Xie, Ling Shao
- **Ano:** 2026 · **Venue:** arXiv:2602.01966 · **Link:** <https://arxiv.org/abs/2602.01966>
- Crítica ao paradigma de só recuperar trajetórias bem-sucedidas como demonstração: ignora o valor pedagógico das tentativas que falharam; e acumular experiência textual indefinidamente aumenta a latência de retrieval e satura a janela de contexto.
- Duas peças: (a) **reflexão contrastiva** que sumariza explicitamente padrões propensos a erro e captura insights reutilizáveis; (b) **self-consolidation** que destila a experiência textual não-paramétrica em parâmetros aprendíveis compactos (internaliza no espaço latente).

## Relevância para o projeto

1. **Justifica olhar as execuções que deram certo.** Roadmap item 2: 91,4% dos steps nunca foram olhados semanticamente. Estes papers dizem que o par (execução ok / execução com o mesmo erro) na mesma classe de caso é onde está o sinal — não a execução com erro sozinha.
2. **"Curadoria localizada, não append-only"** (CONTRAMEM) é a mesma posição já registrada em `discussion/` de que a strategy layer não é log que só cresce. Precedente externo.
3. **Ressalva de escopo:** o self-consolidation paramétrico (destilar em pesos) está **fora** do escopo do projeto — o mecanismo aqui é não-paramétrico/harness (ver `discussion/scope-and-terminology-decisions.md`). Adotar o argumento contrastivo, não a consolidação em parâmetros.

## Relacionados (não buscados a fundo)

- **SkillCAT** (arXiv:2606.13317), **MACLA / Hierarchical Procedural Memory** (arXiv:2512.18950), **CLEAR** (arXiv:2604.07487) — mesma família: pares sucesso/falha da mesma tarefa → primeira divergência → evidência de skill.

---
Adição nova.

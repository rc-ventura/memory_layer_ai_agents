# Diário de Campo — Rafael Coelho Ventura

## Semana de 19/10 a 23/10/2026

Projeto: Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos ([PROGRAMA-FOMENTO], Nº [ANONIMIZADO])

*Registro pessoal de pesquisa, testes, leituras e decisões. Camada episódica (entradas diárias); a camada semântica é o digest mensal em `summarization/`. Uso: memória de trabalho pessoal + acompanhamento do coordenador + rastreabilidade para os Entregáveis do Plano de Trabalho.*

---

## 19/10/2026

**Tipo:** achado — **Sub-atividade:** 2.2 / 2.5 — **Canal:** pessoal

**Registro objetivo:** Fechamos o piloto de mineração da unidade do sandbox (base 3). O inventário tinha 3.653 erros de sandbox; ficaram 1.401 no sandbox, e a unidade virou 14 memórias, registradas num catálogo versionado. O que descobrimos:

1. **A unidade agrupa causas (mecanismos) que se espera terem a mesma lição: é uma hipótese feita por regra. A mineração confere; se a unidade junta causas com consertos diferentes, ela se divide.** Achávamos que a unidade do sandbox era só "o agente chama comandos ou bibliotecas proibidos". Isso se confirmou, com adendos: a maior parte dos erros vinha do ContestacaoCivel, e o mesmo sintoma tinha causas diferentes. Dividir a unidade quando ela junta causas é um resultado normal (procedimento da mineração). Na hierarquia: família "Ambiente & sandbox" → assinatura "Função ou import bloqueado pelo sandbox" → unidade "Inventário do sandbox".
2. **A maior parte dos erros virou sinal de harness (2.252 dos 3.653, cerca de 62%).** O prompt do ContestacaoCivel tem duas versões. A antiga só diz algo genérico, "verifique se a variável existe", sem dizer como; o agente decide sozinho e em geral usa `globals()`. A nova diz para usar `try/except` e não usar `globals()`. Resultado: três sintomas — `globals()`, `try/except` e `eval` dentro de uma função auxiliar escrita pelo agente. Antes, `globals` e `eval` estavam no sandbox e o `try/except` tinha unidade própria; juntamos os três na unidade da **verificação de existência** (a antiga unidade do `try/except`, renomeada). As duas formas, a genérica e a explícita, acabam bloqueadas pelo sandbox (no `try/except`, o erro de variável inexistente sai do alcance do `except`). Por isso o destino é harness: o conserto é no prompt ou no interpretador. Só a verificação saiu para outra unidade; o resto continua no sandbox, dividido em partes.
3. **O resto é hábito do agente, e vira memória**, porque o prompt não pede nada disso: (C) esquecer o import de `json` ou `pd`, 656 erros; (B) importar uma ferramenta como se fosse biblioteca, 212, quase tudo no OBFCivel; (D) importar fora da lista autorizada, 40; (E) funções e atributos proibidos, 488, sobretudo depuração do tipo `type(x).__name__` e `repr(x)` sobre o retorno das ferramentas. Uma memória injetada poderia mitigar esses erros.
4. **Memória global e memória por papel.** C e E valem para qualquer papel. B é por papel porque quase todo o erro está num papel só. D é por papel porque cada papel tem a sua lista de imports autorizados: são 6 listas diferentes em 16 papéis, e cada memória D leva a lista do seu papel. O catálogo (`analysis/registros/memorias.json`) registra as 14 memórias.
5. **Observação:** as execuções do ContestacaoCivel que escrevem direto, sem verificar a variável, terminam sem esse erro.
6. **Possível contorno:** com `globals` proibido no prompt, o agente pode estar validando a variável com `eval`, que o sandbox também bloqueia.

**Reflexão:**
- A observação 5 é consistente com o prompt induzir o erro, mas não prova: execuções que não verificam podem ser casos mais simples. A evidência mais forte é a troca de versão do prompt.
- O contorno com `eval` é hipótese. O `eval` já aparecia em julho (15 erros), antes de o prompt proibir `globals`, e foi para 31 em agosto. O uso do `eval` dentro da função auxiliar é inferência: os dados mostram a chamada, não o corpo da função. A base 3 não tem o prompt; o prompt foi visto na base 2 e no de julho da base 1.
- Só o `eval` que verifica a variável e a cria chamando uma ferramenta foi para o harness. O `eval(texto)`, que converte texto em objeto, continua como memória.
- Pergunta aberta: umas 134 verificações com valor padrão (`if 'x' not in globals(): x = '…'`) continuam como memória, no grupo E, mas provavelmente têm a mesma causa do prompt.
- O destino "memória" de C, B e D foi decidido sem ler os prompts desses papéis; só o grupo E foi testado contra prompts, e fracamente (na base 2 ele tem só 7 erros).
- As 14 memórias foram construídas, não testadas. A redução dos erros só se mede no teste de compensação (`b3 #39`).

**Decisão/próximo passo:** Destinos decididos: a verificação de existência vai para o harness; C e E viram memória global; B e D, memória por papel. Pendência `b3 #48`: seis das 14 memórias têm de 1 a 3 erros; decidir se aplico a régua de "memória rara" antes de usá-las no experimento. Próximo: a segunda unidade de memória e a apresentação de sete slides, com este piloto nos slides 5 e 6.

**Tags:** base-3, sandbox, mineracao, memoria, harness, verificacao-existencia, contestacaocivel, eval, globals, try-except-nameerror, catalogo, memoria-por-papel, sub-2.2, sub-2.5

## 20/10/2026

**Tipo:** implementação — **Sub-atividade:** 2.2 / 2.6 — **Canal:** pessoal

**Registro objetivo:** Dia dedicado a construir a apresentação para o tutor. Revisitei as decisões técnicas que tomei, aprofundei algumas análises, criei os gráficos de que a história da apresentação precisa e discuti algumas limitações da ferramenta.

A mineração de uma memória tem três etapas antes de ela estar pronta para ser injetada num agente ou numa POC. São os degraus 1 a 3 da validação (`17-validacao-memorias.md`); o degrau 4 é a injeção em si, medida por experimento. Um **kit de mineração** automatiza o caminho e o torna repetível. O kit é um conjunto de instruções passo a passo (as *skills*), de agentes com papel fixo (um auditor, dois leitores, um validador) e de scripts, guardado e versionado na pasta `.claude/` do repositório. O assistente de código lê essas instruções e as segue; o Copilot da máquina da base lê os mesmos arquivos. Cada skill não sabe nada da base: lê a base e o código da pasta da análise e roda o mesmo procedimento em qualquer base. Assim, duas bases mineradas pelo kit são comparáveis.

1. **Candidata — "o erro existe, assim e com essa frequência?" (determinístico).**
   - *O passo 0, comum a toda mineração (skill `mineracao-base`).* Antes de contar qualquer coisa, a skill prepara e confere o terreno:
     - **Achar a pasta da análise.** Cada base tem uma pasta datada em `analysis/` (por exemplo, `2026-10-trace-law-flow-third/` para a base 3), com o código (`pipeline/`), os documentos (`docs/`) e a auditoria (`audit/`). Tudo o que a mineração precisa saber da base vem dali.
     - **Conferir a versão do código (o manifesto de hashes).** O kit guarda um manifesto com o *hash* de cada arquivo do pipeline: uma impressão digital que muda se uma vírgula do arquivo mudar. O `conferir_versao.py` compara o código da pasta com o manifesto. Se algum arquivo difere ou falta, a mineração para. Os comandos, as tabelas e a auditoria do kit foram escritos para aquele código, e duas bases só se comparam se forem mineradas pelo mesmo código.
     - **Intake (`checklist.py`).** É a conferência de entrada da base, feita antes de qualquer conta. Ela olha o formato do arquivo (CSV ou parquet, os tipos de cada coluna, os nulos); se as colunas que o pipeline lê existem; quantas linhas há, quantas têm memória e quantas têm erro; quantas memórias (o registro dos passos do agente, em JSON) abrem e quantas estão quebradas; o censo dos tipos de erro; o período das execuções e os papéis presentes. Se alguma memória não abre, a mineração para: o pipeline perderia esses passos sem avisar.
     - **Monitoramento (`monitorar.py`).** Algumas lições e sinais o pesquisador decidiu acompanhar em vez de minerar de novo ou injetar, como os sinais de harness (o erro que o prompt induz). Cada um está registrado em `analysis/registros/monitoramento.json`, com a linha de base (os números de quando a decisão foi tomada) e o gatilho (a condição que faz soar o alarme, como os erros crescerem acima de um limite). O script confere cada registro na base que está na mesa. Se um gatilho dispara, a mineração para e a lição volta para a decisão do pesquisador. É a única comparação entre bases que o kit faz, e é de propósito: a linha de base e o gatilho foram fixados pelo pesquisador quando ele decidiu monitorar. (As memórias raras e de reforço, explicadas no degrau 3, têm o alarme registrado no próprio catálogo de memórias.)
     - **"Sair do ambiente" e a varredura de dado pessoal.** O trace fica numa máquina separada, a máquina da base, porque tem nomes de clientes, CPF, número de processo e trechos de documentos jurídicos. "Sair do ambiente" é tudo o que vai dessa máquina para fora: uma resposta no chat, um commit, uma foto, uma mensagem. A regra de sigilo diz o que pode sair: o conteúdo técnico (contagens, nomes de papel, ferramenta, módulo e função, meses, mensagens de erro, código, prompt). Não pode sair dado pessoal nem conteúdo do cliente (o documento, a pergunta do usuário, a resposta entregue a ele). O relatório completo, com toda a evidência, fica na máquina. Antes de qualquer arquivo sair, o `varrer_pii.py` procura padrões de dado pessoal (CPF, CNPJ, número de processo, e-mail, telefone) e bloqueia a saída se achar algum. Ele não reconhece nome de pessoa nem texto de documento, então a leitura humana do que sai continua obrigatória. Há também um passo opcional, o `versao_para_sair.py`, que troca os identificadores de execução por `caso-1`, `caso-2` etc.
   - *A mineração de uma lição (skill `mineracao-candidata`).* Uma **lição** (ou unidade, com nome `U_...`) é o que se espera ensinar ao agente a partir de um grupo de causas de erro: por exemplo, `U_sandbox`, "o que o sandbox deixa importar e chamar". Só é minerada a lição que passou na **triagem de recorrência**: a régua de pelo menos 3 execuções em pelo menos 2 meses, para que a memória não seja tirada de um acidente. A mineração tem duas partes: a genérica, que é igual para todas as lições, e a específica, que extrai a lição em si e é escolhida pelo funil.
   - *A parte genérica, etapa por etapa.* São seis medidas, numeradas de G1 a G6 no procedimento da mineração (`16-procedimento-mineracao-candidatas.md`). Cada uma responde a uma pergunta sobre a lição e grava uma tabela na pasta da mineração. Ela **descreve** a lição, não a escreve: o texto da memória sai da parte específica. Os exemplos são do sandbox na base 3 (dossiê do sandbox).
     - **G1 · Recorrência e escopo — "quanto esse erro acontece, e onde?"** Conta os erros, as ocorrências, as execuções, os meses e os papéis em que a lição aparece, e os modelos e ferramentas presentes no passo do erro. *Ocorrência* é a cascata contada uma vez: vários erros seguidos do mesmo papel, na mesma lição, valem uma ocorrência. Ela inclui também as falhas silenciosas, em que a ferramenta falhou mas devolveu o erro como texto e o passo pareceu ter dado certo. Esses números são a régua da triagem: candidata é a lição com pelo menos 3 execuções em pelo menos 2 meses. Eles também dão o escopo da memória (todos os papéis ou só alguns). Grava `perfil.csv`. No sandbox, em 16/10: 3.653 erros, 3.475 ocorrências, 3.451 execuções, 10 meses, 16 papéis.
     - **G2 · Sub-unidades — "a lição esconde partes diferentes?"** Aplica a mesma régua da triagem separando por papel e pela ferramenta chamada no passo do erro. Se um papel ou uma ferramenta concentra quase tudo, ou se uma parte passa na régua sozinha, a lição pode estar juntando causas diferentes e talvez precise se dividir. Limitação: a ferramenta contada é a chamada no passo do erro, não a que produziu o valor errado (rastrear a origem é da parte específica). Grava `sub_unidades.csv`. No sandbox, a mesma pergunta feita com a contagem por papel da mineração (`inventario_papel.csv`) mostrou que 73% dos erros vinham de um papel só, o ContestacaoCivel. Foi esse o sinal de que a unidade juntava causas diferentes.
     - **G3 · Antes — "esse erro é efeito de outro?"** Olha o que veio antes do erro: se o passo anterior também errou, e de qual lição; se houve uma falha silenciosa antes; se o erro aconteceu fora da primeira chamada do papel. Se quase sempre vem outro erro antes, a lição pode ser só consequência, e o conserto pode estar na lição de antes. Grava `antes.csv`.
     - **G4 · Depois — "o agente se corrige sozinho?"** Olha o que veio depois: o passo seguinte deu certo, repetiu a mesma lição ou caiu em outra; o papel entregou resposta; a execução terminou com resposta final. Se o agente quase sempre se corrige no passo seguinte, a memória só economiza essa primeira tentativa. Se ele fica preso repetindo, a memória vale mais. Grava `depois.csv`.
     - **G5 · Estabilidade — "o erro é constante ou foi um incidente?"** Separa por mês, por versão do formato do prompt e por modelo, e mede a concentração. Um erro espalhado pelo tempo indica hábito do agente, que memória pode mitigar. Um erro concentrado num mês, numa versão de prompt ou num modelo indica incidente ou mudança de configuração, que se conserta no harness. Grava `estabilidade.csv`. No sandbox, a contagem por mês da mineração (`inventario_mes.csv`) mostrou o `globals` do ContestacaoCivel concentrado em julho e agosto de 2026 (2.346 dos 2.352 erros). A concentração apontou para a mudança de prompt, e essa parte foi para o harness.
     - **G6 · População — "quais são os casos?"** Monta uma linha por erro ou ocorrência, com todas as colunas das etapas anteriores. É a entrada da parte específica (o script ou a leitura de casos trabalham sobre ela) e a base da evidência do relatório. Grava `casos.csv`. Fica na máquina da base: não sai identificador de execução nem texto de caso.
     - *As conferências:* o `perfil.csv` tem de bater com a lista de candidatas da base (erros, ocorrências, execuções, meses e papéis), e a auditoria independente tem de dar os mesmos números (ver abaixo).
   - *A parte específica e o funil.* A parte genérica descreve a lição; a **parte específica** a extrai: no sandbox, por exemplo, quais módulos o agente esqueceu de importar, quais funções o sandbox barrou e qual a lista de imports autorizados de cada papel. O **funil** é uma tabela no procedimento da mineração que diz, para cada lição, qual parte específica ela usa: um script determinístico próprio da lição, um notebook (o formato antigo, da base 1) ou uma investigação por leitura de casos, quando ainda não há regra que extraia a lição sozinha.
   - *A auditoria independente e o encontro.* Enquanto a mineração roda, o agente `auditor-independente` roda uma **segunda implementação**: outro código, escrito sem olhar o pipeline, que recalcula as mesmas medidas direto do trace. Depois, o `comparar_auditoria.py` confronta as duas, medida a medida (no sandbox da base 3, em 21/10, foram 77 medidas iguais). Se um número diverge, ninguém conserta para fazer bater: a mineração para, os dois valores vão para o relatório, e a divergência vira o achado que o pesquisador decide. A ideia é que um erro de código dificilmente se repete igual em dois códigos escritos separadamente.
   - *A saída do degrau 1.* Para cada lição (ou para cada parte, quando a lição se divide), a mineração monta o **arquivo final da memória**: a lição em texto (a instrução que o agente receberia), o escopo (todos os papéis ou um papel), a evidência (as contagens e o comando que as reproduz) e o destino proposto (memória ou sinal de harness). O arquivo segue uma estrutura fixa, o **esquema da memória** (`analysis/registros/esquema-memoria.json`), e o `validar_memoria.py` confere que ele tem todos os campos, no formato certo. Cada memória fechada entra no **catálogo** (`analysis/registros/memorias.json`), que guarda uma linha por memória, com a contagem, a rodada de onde saiu e o degrau em que está. A regra de ouro do kit: o modelo de linguagem propõe, o script conta. Nenhum número sai da leitura de um modelo.
2. **Conferida — "a lição é coerente com o ambiente e com o prompt?" (determinístico, sem ler caso).** O script `conferir_memorias.py` faz cinco checagens em cada memória do catálogo, comparando o que a memória diz com o ambiente do papel e com o prompt dele:
   - **(1) Coerência com o ambiente.** Tudo o que a memória manda usar ou importar existe no papel. Quem decide é o **interpretador**, o programa que executa o código do agente e barra o que não está autorizado, e não o prompt. Na base 1 e na base 2, o prompt às vezes não lista o `json` e o interpretador aceita o `import json` mesmo assim; conferindo pelo prompt, uma memória certa seria reprovada.
   - **(2) Conflito com o prompt.** O prompt do papel não manda o contrário do que a memória diz. Por exemplo, uma memória "não chame `globals`" brigaria com o prompt que manda verificar se a variável existe. Esse conflito costuma mudar o destino para harness: o conserto é no prompt.
   - **(3) Repetição do prompt.** O prompt ainda não diz a mesma coisa. Se já diz e o agente ignora, a memória só repetiria a instrução.
   - **(4) Recorrência.** A memória passa na régua de memória rara (pelo menos 3 execuções em pelo menos 2 meses). Se não passa, fica monitorada, não injetada.
   - **(5) Uma causa só.** A memória não junta sub-causas com consertos diferentes, como o mesmo nome barrado usado para depurar e para verificar uma variável.
   - Se a 1 ou a 5 falham, corrige-se o script da parte específica. A 2 costuma levar ao harness. A 3 e a 4 são decisão do pesquisador: o script grava a decisão, com o motivo (`--decidir`), e ela só continua valendo enquanto o resultado do script não mudar.
3. **Revisada — "a causa é mesmo a que a regra supõe?" (investigação com agentes e o pesquisador).** As regras contam o erro, mas não leem o que o agente quis fazer. O degrau 3 lê uma amostra de casos para conferir se a causa suposta pela regra é a verdadeira. Ele é conduzido pela skill `mineracao-investigacao`, chamada pelo comando `/investigar`:
   - **Amostra por regra fixa (`amostrar.py`).** Quem escolhe os casos é uma regra escrita antes, não o leitor. Assim ninguém escolhe os casos que confirmam a própria ideia. Cada caso lido fica com o registro cru do passo gravado na máquina, e o `drill_down.py` recorta a janela em volta do erro (os passos antes e depois), para a leitura.
   - **Hipóteses antes de ler.** A hipótese nula e as alternativas são escritas antes da leitura, cada uma com o que se veria no caso se fosse verdadeira. Escrever depois seria ajustar a hipótese ao que se leu.
   - **Leitura aberta e lista de categorias.** O agente `investigador` lê cada caso e descreve em frase livre o que o agente estava fazendo. O agente `segundo-leitor` lê os mesmos casos *às cegas*, sem ver a primeira leitura. As frases dos dois são postas lado a lado e viram uma lista de categorias. O pesquisador aprova a lista: é o primeiro **gate**, um ponto em que o processo para e só segue com a decisão dele.
   - **Leitura fechada e concordância.** Com a lista aprovada, os dois leitores classificam pelo menos 20 casos nas categorias. O `concordancia.py` mede o acordo entre eles pelo **kappa**, um índice que desconta a concordância que aconteceria por acaso. Abaixo de 0,6, o problema é a categoria, que está mal definida: ela não vira regra.
   - **Da leitura à regra.** A hipótese confirmada vira uma regra determinística (uma expressão que reconhece o padrão no código ou na mensagem do passo). O `testar_regra.py` conta essa regra na população inteira, não só na amostra, e compara com a leitura. Toda versão testada da regra entra no dossiê, inclusive as que falharam.
   - **O painel e o gate da decisão.** O `valor_da_licao.py` cruza a frequência da lição (se ela está entre as que somam a maior parte dos erros, ou aparece na maior parte dos meses) com a confiança (a concordância e a regra contada). Daí sai a situação: "pronta para script", "lição existe, redação em aberto", "várias causas: investigar a fundo" ou "certa, mas rara: monitorar". O pesquisador aprova o texto da lição e o destino, e o `registrar_decisao.py` grava a decisão com as palavras dele.
   - **Um script próprio para a lição (skill `propor-script` e agente `validador-de-script`).** Quando a lição é frequente e confirmada, o pesquisador pode pedir um script específico para ela, que passa a extraí-la sem leitura de caso. Primeiro se escreve o **racional**, o documento que diz o que o script deve medir e por quê. Depois o script. O validador escreve, só a partir do racional, uma segunda implementação, e compara as duas medida a medida. O pesquisador aprova.
   - **Monitoradas em vez de injetadas.** A memória que o ambiente ou a recorrência não sustentam não é injetada: fica no catálogo como **rara** (poucos casos; o alarme soa quando ela passa na régua) ou de **reforço** (repete o que o prompt já diz; o alarme soa quando os erros triplicam).
4. **Validada — "injetada, ela reduz o erro sem criar outro?" (experimento).** Só aqui a memória é posta no agente: primeiro reproduzindo os casos que falharam, agora com a memória; depois num teste antes × depois, por taxa de erro e por papel. Até este degrau, toda memória é hipótese com evidência.

**Reflexão:** Montar a apresentação foi muito bom porque me obrigou a revisitar as decisões técnicas e a entender de novo, com mais profundidade, o porquê de cada passo. Os gráficos para contar a história mostraram o que ainda falta explicar e quais limitações da ferramenta precisam ser ditas ao tutor. Aprendo mais a cada rodada.

**Decisão/próximo passo:** Seguir com a apresentação, fechando os gráficos de cada slide; levar as limitações da ferramenta discutidas hoje para o texto da apresentação.

**Tags:** apresentacao, tutor, slides, graficos, mineracao, kit-mineracao, skills, validacao-memorias, degraus, auditoria-independente, sub-2.2, sub-2.6

## 21/10/2026

**Tipo:** achado — **Sub-atividade:** 2.2 / 2.5 — **Canal:** pessoal

**Registro objetivo:** Dia dedicado à unidade do sandbox. O sandbox do agente tem uma lista de bibliotecas que ele pode importar, e o que está fora da lista é barrado. Encontramos que boa parte dos erros que a unidade reunia era, na verdade, sinal de harness e não problema do sandbox em si. O caso é o do papel ContestacaoCivel, que tem duas versões de prompt:
- **Prompt antigo:** manda o agente verificar se a variável existe, sem dizer como. O agente verificava com construções que o ambiente proíbe, como `globals()`.
- **Prompt novo (upgrade do mesmo papel):** define como verificar (`try/except NameError`, sem `globals()`). Mesmo assim dá erro no sandbox, porque dentro dele uma variável não definida não levanta `NameError`: levanta um `InterpreterError`, que o `except NameError` não captura.

Por isso decidimos que o destino final dessa parte é o **harness**, ainda que o erro tenha sido levantado e contado na unidade do sandbox.

*Complemento do histórico de commits do dia:*
- O mecanismo do `InterpreterError` está reproduzido no interpretador (`testar_sandbox_try_nameerror.py`, código sintético, smolagents 1.26.0, versão da plataforma desconhecida): `except NameError` falha com a mesma mensagem do trace quando a variável ainda não existe; `except Exception` funciona; `globals()` falha. Está no `02-relatorio-achados.md`, §7.9.
- A rodada nova da base 3 foi aprovada: 1.100 erros ficam no sandbox, 77 medidas iguais às da auditoria independente, 17 memórias no catálogo (rodada `99e032ad`). O sinal de harness cresceu para 2.518 erros (69%).
- Na base 2, a hipótese de que o `json` tinha saído da lista autorizada do prompt não se sustentou (0,4% de erro com o `json` fora da lista, contra 1,6% com ele na lista). Na base 1, 11 de 11 `import json` rodam com um prompt que não o lista: o prompt anuncia um ambiente diferente do que o interpretador aceita. Por isso o degrau 2 da validação passou a conferir pelo interpretador (Ajuste 28; transversal #7).

**Reflexão:** O prompt antigo e o novo falham de formas diferentes, mas o agente não tem como saber que a instrução do prompt é a que não funciona no sandbox. Uma memória do tipo "não use try/except" contradiria o prompt, por isso a correção cabe ao harness (o prompt ou o interpretador) e não à memória do agente. Isso reforça que contar um erro na unidade do sandbox não define o destino dele. O mecanismo do `InterpreterError` foi reproduzido com código sintético; que o prompt induz o erro na plataforma real continua inferência (a base 3 não tem o prompt).

**Decisão/próximo passo:** Verificação de existência vai para o harness, não para a memória. Falta a mineração confirmar o destino das outras partes do sandbox (C, B, D e E, que viram memória) e conferir se o parágrafo da instrução já existia no prompt de julho.

**Tags:** base-3, sandbox, harness, contestacaocivel, globals, try-except-nameerror, interpretererror, lista-imports-autorizados, prompt, destino, sub-2.2, sub-2.5

### 21/10/2026 (verificações depois)

**Tipo:** achado — **Sub-atividade:** 2.5 — **Canal:** pessoal

**Registro objetivo:** Depois da decisão sobre o harness, tivemos de fazer verificações porque vimos que, embora o agente receba no prompt uma lista de bibliotecas autorizadas, nem sempre essa lista está sincronizada com a do ambiente do sandbox. O ambiente pode mudar quando o desenvolvedor passa uma lista própria por um executor (interpretador) personalizado, ou quando se acrescenta uma lista adicional no texto do prompt.

*Complemento do histórico (dossiê do sandbox, itens 17–19):*
- No smolagents 1.26.0, o `CodeAgent` monta a lista de imports a partir da lista-base do framework (que não tem `json`) mais o `additional_authorized_imports` do desenvolvedor, e usa a mesma lista no texto do prompt e no interpretador que ele mesmo cria.
- O `CodeAgent` também aceita um interpretador pronto (`executor=`), e só o interpretador criado pelo próprio agente recebe a lista dele. O prompt sai de `authorized_imports` do agente (e os templates do prompt podem ser trocados).
- Medido na base 1: nas 738 execuções cujo prompt não lista o `json`, há 11 passos com `import json`, e os 11 rodam (nenhum "Import of json is not allowed"). A divergência acontece dentro da mesma execução. A base 2 confirma, com mais casos.
- A consequência prática: o degrau 2 da validação passou a conferir a memória contra o que o interpretador aceita (a lista da mensagem de erro e os imports que rodam), e não contra a lista do prompt. A inconsistência entra no aviso para a plataforma (transversal #7).

**Reflexão:** A minha impressão foi de um bug do próprio framework (smolagents). O que está medido é a **divergência**: o prompt anuncia um ambiente diferente do que o interpretador aplica. A **causa** continua hipótese: o `executor=` personalizado é um recurso documentado do framework, então a divergência pode ser configuração da plataforma e não defeito do smolagents; sem o código da plataforma não dá para distinguir. Se o prompt não é descrição confiável do ambiente, toda checagem que o use como tal passa a precisar de confirmação contra o comportamento observado.

**Decisão/próximo passo:** A conferência de ambiente usa o interpretador. Levar a divergência prompt × interpretador como aviso à plataforma (transversal #7), pedindo a configuração real do executor e o código que monta o prompt.

**Tags:** sandbox, smolagents, executor, authorized-imports, prompt, interpretador, divergencia, plataforma, degrau-2, sub-2.5

## 22/10/2026

**Tipo:** decisão — **Sub-atividade:** 2.2 / 2.5 — **Canal:** pessoal

**Registro objetivo:** Continuei a construir a apresentação. Dois conjuntos de decisões conceituais:

1. **O destino das memórias depois dos degraus de validação.**
   - Algumas memórias nascem **globais**: o problema atinge todos os papéis e a memória serve como um cartão de lembrança. No sandbox, as globais são a C (esquecer o import de `json` ou `pd`) e a E (funções e atributos proibidos). A B e a D valem por papel.
   - Outras memórias não têm recorrência suficiente, ou só repetiriam o que o prompt já diz. Essas ficam **catalogadas e vigiadas, mas não injetadas**. "Monitorar" não é um terceiro tipo: é o tratamento dado às duas, que diferem no alarme:
     - **rara**: tem poucos casos (não passa na régua de ≥ 3 execuções em ≥ 2 meses). O alarme dispara quando ela passa na régua. Exemplos: B.RespostaBacen e C.CalculoTrabalhista (2 erros, 1 mês).
     - **reforço**: a memória só repetiria o que o prompt já diz. O alarme dispara quando os erros triplicam (e, nas bases com prompt, quando o prompt deixa de dizer aquilo). Exemplos: as 10 memórias D e a B.OBFCivel.
   - As memórias que seguem para injeção e para o degrau 3 ficam três: C, E e C.JoogleAnalytics.
2. **A diferença entre sinal de harness e destino harness.**
   - **Sinal de harness:** erros induzidos pelo prompt (ou pelo contrato da ferramenta). Quem corrige é o prompt ou a ferramenta, e não a memória do agente.
   - **Destino harness:** tem unidades próprias, que dependem de ajuste de infraestrutura ou de ambiente: falha do LLM (infra), protocolo e timeout de ferramenta.
   - O protocolo é a unidade com mais erros. O erro principal é o agente esquecer de abrir (e fechar) a tag `<code>`: sem ela, a regex do harness não acha o bloco e o step falha. Em alguns prompts dá para mudar essa configuração e usar uma saída em JSON estruturado com o campo `code`, o que tende a diminuir o erro. Esse problema também tem uma vertente de modelo: há evidência de que a troca de modelo vem com mais erros, mas é uma associação e não causa e efeito.

*Complemento do histórico:*
- Os dois tipos de monitoramento são o Ajuste 29 (22/10): `catalogar_memoria.py --monitorar`, aplicado às 13 memórias não injetadas do sandbox (reforço: as 10 D e a B.OBFCivel; rara: B.RespostaBacen e C.CalculoTrabalhista).
- Pelo racional do protocolo, em modo JSON estruturado a família "resposta sem bloco de código" não existe, e em modo texto ela só acontece com `<code>` mal escrito. O modo é configuração da plataforma. Na base 2, o surto coincidiu com a troca de modelo: no mesmo papel, mês e prompt, o modelo antigo teve 0 erros em 381 steps e o novo, 54 em 478. É medida observacional, sem experimento.
- Mesmo dia: gráficos de taxa de erro por papel e mês; roteiro do degrau 3 do sandbox, com decisão de ler os casos em todas as bases, com prioridade para a base 3; e `drill_down.py` da base 3.

**Reflexão:** Separar sinal de harness de destino harness importa para o projeto porque quem corrige é diferente: o sinal de harness é erro nosso de configuração do prompt ou da ferramenta, e o destino harness depende de infra, protocolo ou ambiente. Sobre o modelo, 54 erros contra 0 mostram associação forte, mas o modelo não foi variado de forma controlada, então não prova causa.

**Decisão/próximo passo:** Memórias C e E globais, B e D por papel; as não injetadas ficam monitoradas como rara ou reforço, com alarme no catálogo. Manter a distinção entre sinal de harness e destino harness nos slides.

**Tags:** apresentacao, memoria-global, memoria-rara, memoria-reforco, monitoramento, sinal-de-harness, destino-harness, protocolo, bloco-code, modelo, associacao, sub-2.2, sub-2.5

## 23/10/2026

**Tipo:** decisão — **Sub-atividade:** 2.2 / 2.5 — **Canal:** pessoal

**Registro objetivo:** Depois de validações exaustivas, entendemos que a unidade do sandbox (`U_sandbox`) se fragmentou em várias partes: A, B, C, D e E. A lição única que a unidade supunha não convergiu, divergiu: o mesmo sintoma ("o sandbox barrou") tem causas diferentes, e cada parte tem dono, conserto e escopo próprios (geral ou por papel).

*Por que a divisão ficou assim (resumo a partir do dossiê do sandbox e do racional):*

| Parte | O que reúne | Causa e dono | Destino e escopo |
|---|---|---|---|
| **A** | introspecção (`globals`, `locals`, `vars`, `eval`) no ContestacaoCivel | o prompt manda verificar se a variável existe e o ambiente não suporta as formas usadas | **harness** (a verificação de existência sai da unidade) |
| **B** | ferramenta importada como se fosse módulo (`get_document_text`, `python_interpreter`, `tools`…) | no OBFCivel, hábito do agente; no caso do `get_document_text`, o prompt cita uma ferramenta que não declara (Ajuste 26) | memória por papel (OBFCivel; reforço); a citação não declarada, harness |
| **C** | módulo usado sem import (`json`, `pd`, `re`, `datetime`) | esquecimento do agente | memória **global** para os módulos que estão em todas as listas autorizadas; **por papel** para os demais (C.JoogleAnalytics, C.CalculoTrabalhista) |
| **D** | import fora da lista autorizada (`copy`, `typing`, `ast`…) | hábito do agente; cada papel tem a sua lista | memória **por papel**, com a lista do papel (as D são de reforço: não injetadas, vigiadas) |
| **E** | funções e atributos proibidos, sobretudo depurar o retorno das ferramentas (`__name__`, `repr`, `dir`) | hábito do agente (inspecionar um valor) | memória **global** |

- A regra de divisão está no procedimento: a unidade é uma **hipótese** (as causas que se espera terem a mesma lição). A mineração confere e, se a unidade junta causas com consertos diferentes, ela se divide; dividir é "resultado normal". A checagem "uma causa só" do degrau 2 existe para isso: a memória não pode misturar sub-causas com consertos diferentes.
- A parte F recebeu os nomes `globals`, `locals`, `vars` e `eval` que saíram da E e ficou para depois, quando a maior parte das memórias estiver no degrau 3.
- Sobre o termo: "candidata" vale no degrau 1 (a mineração passou e a lição ainda é hipótese). Depois do degrau 2 a memória está "conferida", e depois do 3, "revisada"; "validada" só no 4. No catálogo, cada parte é uma memória com id `U_sandbox.<parte>[.<papel>]`, e a unidade é o conjunto delas.
- Registro de datas (dos docs): a decisão de dividir a unidade em partes é de 19/10 (piloto do sandbox, dossiê §4, decisão 2). As decisões do Rafael de que "uma causa só" passa em C, E e C.JoogleAnalytics estão datadas de 26/10.

**Reflexão:** A divergência é um resultado do método, não uma falha dele. Uma lição só pareceria mais simples, mas injetaria uma instrução errada em parte dos papéis (por exemplo, "importe `pd`" onde o ambiente não tem `pandas`) e misturaria erros induzidos pelo prompt (harness) com hábitos do agente (memória). Cada parte com o seu escopo, geral ou por papel, deixa claro o que se injeta e o que se corrige fora da memória.

**Decisão/próximo passo:** Seguir com as partes B, C, D e E como memórias (globais e por papel), A como harness e F para depois. Levar o degrau 3 (revisão de casos) para a base 3.

**Tags:** sandbox, u-sandbox, partes, divisao-da-unidade, candidata, memoria-global, memoria-por-papel, harness, uma-causa-so, degraus-validacao, sub-2.2, sub-2.5

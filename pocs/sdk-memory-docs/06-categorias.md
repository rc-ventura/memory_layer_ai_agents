# Categorias de memória

> Seção: **Conceitos** · Página original: `docs/conceitos/categorias` · [Índice](README.md) · Anterior: [Conceitos](05-conceitos.md) · Próxima: [Scoring de importância](07-scoring.md)

O motor classifica toda memória em **uma de cinco categorias fixas**. A categoria define peso de importância, comportamento de UPDATE/INSERT, decaimento temporal e exemplos esperados.

## As cinco categorias

### `fixed_profile`

Dados estáveis e permanentes sobre o cliente, raramente mudam. Inclui identidade e dados biográficos declarados pelo usuário. Só deve ser atualizado se o usuário corrigir explicitamente um valor anterior.

**Exemplos:**

- nome
- data de nascimento
- CPF
- cidade natal
- nacionalidade
- profissão declarada
- formação educacional

### `dynamic_profile`

Estado atual do cliente que muda ao longo do tempo. Representa o snapshot mais recente de fatos mutáveis. Para tópicos já presentes, o motor **prefere UPDATE sobre INSERT**.

**Exemplos:**

- cidade ou endereço atual
- estado civil
- empregador atual
- cargo atual
- número de dependentes
- faixa de renda declarada
- situação financeira declarada

### `preferences`

Preferências explícitas declaradas pelo usuário sobre como deseja interagir, ser contatado ou consumir produtos e serviços. Inclui gostos, aversões, opt-ins e opt-outs. Atualizada quando o usuário contradiz uma preferência anterior.

**Exemplos:**

- canal de comunicação preferido (app, e-mail, telefone)
- formato de cobrança (digital vs. papel)
- opt-out de chamadas promocionais
- idioma preferido
- método de pagamento preferido
- preferências de notificação
- preferências de produto (e.g. tipo de recompensa de cartão)

### `events`

Ocorrências discretas e pontuais envolvendo o cliente e o banco ou seus produtos. Cada evento é único — INSERTs separados; **nunca atualize um evento**, crie um novo se houver desdobramento.

**Exemplos:**

- contestação de cobrança
- solicitação de aumento de limite
- relato de perda/roubo de cartão
- reclamação de fraude
- bloqueio/desbloqueio de conta
- pedido de cancelamento de produto
- agendamento de retorno

### `experiences`

Experiências subjetivas ou pessoais compartilhadas pelo cliente que dão contexto sobre vida, objetivos ou estado emocional. Úteis para construir rapport e personalizar tom em interações futuras.

**Exemplos:**

- viagem internacional ou doméstica
- compra significativa (imóvel, veículo)
- marco de vida (casamento, nascimento de filho, formatura)
- experiência negativa com concorrente ou banco anterior
- meta financeira mencionada (aposentadoria, investimento)
- evento de saúde com impacto financeiro

## INSERT ou UPDATE?

A regra prática:

| Categoria | Default |
|---|---|
| `fixed_profile` | UPDATE só com correção explícita do usuário. |
| `dynamic_profile` | **UPDATE preferido** se já existe memória sobre o mesmo `subject_key`. |
| `preferences` | UPDATE quando contradiz preferência anterior. |
| `events` | **Sempre INSERT** — eventos são imutáveis. |
| `experiences` | INSERT por padrão; cada experiência é única. |

O `subject_key` (e.g. `current_city`, `marital_status`, `name`) é o que o motor usa para decidir se "é o mesmo tópico de antes". Ele é gerado em snake_case pelo judge e estabilizado entre turnos — quando o motor recupera uma memória existente com `subject_key`, o judge é instruído a reaproveitar exatamente esse identificador, não criar variantes.

## Tópicos sensíveis bloqueados

O judge é instruído a recusar (`respond_only`) memórias sobre:

- política, religião
- orientação sexual
- uso de drogas
- outros dados sensíveis/protegidos

Esses guardrails ficam no system prompt do judge — você pode estendê-los via `prompts.yaml` (ver [Configuração](03-configuracao.md#customização-de-prompts-promptsyaml)).

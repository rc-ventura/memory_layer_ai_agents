# Diário de Campo — Rafael Coelho Ventura

## Semana de 24/08 a 30/08/2026

Projeto: Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos (Inova Talentos / IPT Open, Nº 1335844346)

*Registro pessoal de pesquisa, testes, leituras e decisões. Camada episódica (entradas diárias) + camada semântica (síntese semanal ao final desta semana). Uso: memória de trabalho pessoal + acompanhamento do coordenador + rastreabilidade para os Entregáveis do Plano de Trabalho.*

---

## 24/08/2026

**Tipo:** achado — **Sub-atividade:** 1.6 — **Canal:** pessoal

**Registro objetivo:** Ao finalizar a leitura do survey "Memory in the Age of AI Agents" (Hu, Liu et al.), na p.70, seção 7.2.2, encontrei um achado relevante para o desenho do mecanismo: o survey aponta que uma direção promissora para gerenciamento de memória verdadeiramente automatizado é integrar construção, evolução e recuperação de memória diretamente no loop de decisão do agente via chamadas explícitas de tool (tool calls) — fazendo o próprio agente raciocinar sobre as operações de memória (add/update/delete/retrieval), em vez de depender de módulos externos ou workflows hand-crafted. Segundo o survey, isso leva a um comportamento de memória mais coerente, transparente e contextualmente fundamentado, comparado a desenhos que separam o raciocínio interno do agente das suas próprias ações de gerenciamento de memória.

**Reflexão:** Isso me parece reforçar que integrar a gestão de memória no próprio loop do agente (via tool calls) é mais promissor do que um módulo externo separado — e se conecta direto com a comparação já prevista no Sub 1.6 (loop de aprendizado fechado nativo vs. memória transparente com controle programático explícito). Também traz um argumento de design a favor da abordagem "nativa": o agente sabe exatamente qual operação de memória executou (add/update/delete/retrieval), o que dá mais transparência e rastreabilidade — relevante pro contexto jurídico, onde auditabilidade importa. Nota à parte: a entrada de 20/08 já tinha registrado a leitura deste survey como finalizada; esta é uma segunda passada mais detida, chegando a achados específicos que a primeira leitura não tinha capturado.

**Decisão/próximo passo:** Considerar a abordagem de memória via tool calls integrada ao loop nativo do agente como candidata prioritária para os POCs mínimos do Sub 1.6, frente a um módulo externo separado.

**Tags:** memory-in-the-age-of-ai-agents, tool-based-memory, loop-nativo, sub-1.6, arquitetura, achado

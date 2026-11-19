# Persistência

> Seção: **Documentação** · Página original: `docs/documentacao/persistencia` · [Índice](README.md) · Anterior: [Configuração](03-configuracao.md) · Próxima: [Conceitos](05-conceitos.md)

O backend de persistência é responsável por armazenar as memórias com seus embeddings e metadados (categoria, `subject_key`, `is_current`, `previous_memory_id`, `mention_count`, etc.) e por expor a busca por similaridade filtrada por categoria que alimenta o estágio de retrieve do [pipeline](09-pipeline.md). O backend é escolhido via `persistence.backend` no `config.yaml` — ver [Configuração → persistence](03-configuracao.md#persistence).

## ChromaDB

Atualmente o único backend implementado é o **ChromaDB**, que roda embutido no processo do SDK (não há servidor separado).

### Como funciona

O SDK instancia um `chromadb.PersistentClient` apontando para um diretório local em disco. Cada `user_id` recebe sua própria coleção, nomeada `customer_memories__<user_id_sanitizado>` — instâncias diferentes de `MemoryClient` no mesmo processo ficam naturalmente isoladas, cada uma operando apenas na sua coleção.

Como o cliente é `Persistent`, todos os writes (insert/update) gravam em disco no momento da chamada. Reiniciar o processo recupera o estado anterior automaticamente: basta criar um novo `MemoryClient` apontando para o mesmo `.memory/`.

### Onde os dados ficam

Por padrão, o ChromaDB cria os arquivos do banco dentro de `.memory/chroma/` — uma subpasta da `.memory/` que o SDK descobre na inicialização. Ver [Configuração → Layout do diretório `.memory/`](03-configuracao.md#layout-do-diretório-memory) para a estrutura completa do diretório.

```yaml
persistence:
  backend: chroma          # único backend implementado hoje
  chroma:
    path: chroma           # relativo ao .memory/ — vira .memory/chroma/
```

`path` aceita valores absolutos ou relativos. Relativos resolvem contra o `.memory/` descoberto, **não contra o CWD**. Em produção, prefira um caminho absoluto fora do repositório do projeto (ex.: `/var/data/memories`) — assim o estado não vai parar em commits acidentais nem é apagado por `clean` do build.

Para sobrescrever sem editar o YAML, use a variável de ambiente `MEMSDK_CHROMA_PATH`. A lista completa de envs está em [Configuração → Variáveis de ambiente](03-configuracao.md#variáveis-de-ambiente-memsdk_).

## Outros backends

Hoje, `chroma` é o único valor aceito por `persistence.backend`. A arquitetura, no entanto, foi pensada para múltiplos backends: existe uma interface `MemoryRepository` e uma factory `build_repository()` que despacha pelo nome do backend declarado na configuração.

Adicionar um novo backend — por exemplo, **PostgreSQL com pgvector** — é uma extensão natural: basta implementar a interface e registrar a nova opção na factory. O suporte a `pgvector` ainda **não está disponível**; é apenas um caminho considerado pela arquitetura para deployments que já têm Postgres como infraestrutura padrão e querem evitar um vector store extra.

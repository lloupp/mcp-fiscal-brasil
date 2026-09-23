# Integração com APURA

A separação arquitetural recomendada é deliberada:

> **mcp-fiscal-brasil = infraestrutura aberta e determinística**  
> **APURA = produto comercial, multi-tenant e orientado a workflow**

## O que permanece open source

- parsers e validadores de documentos fiscais;
- schemas tipados;
- tabelas fiscais redistribuíveis e versionadas;
- clientes para APIs públicas/oficiais;
- adapters de autenticação por interface, sem credenciais;
- tools MCP pequenas, composáveis e auditáveis;
- CLI, SDK Python e REST para integração;
- catálogo de proveniência e limitações;
- fixtures e testes de contrato.

O core não deve armazenar dados de clientes, credenciais, decisões de recuperação tributária ou estado de workflow.

## O que pertence ao APURA

- autenticação, owner e isolamento multi-tenant;
- armazenamento de documentos/evidências por cliente;
- cofre de certificados e tokens;
- conectores OAuth/ERP mantidos com SLA;
- filas, webhooks, processamento em lote e observabilidade;
- motor de teses com fundamento jurídico versionado e revisão humana;
- monitor jurídico;
- trilha de auditoria, aprovações e segregação de funções;
- geração de entregáveis comerciais;
- billing, limites, planos e suporte;
- políticas de retenção/LGPD.

## Forma de integração

O APURA deve consumir uma versão fixada do pacote Python para operações determinísticas no mesmo processo e usar MCP quando a descoberta dinâmica de tools trouxer benefício.

Fluxo recomendado:

```text
Upload/ERP -> APURA tenant boundary -> normalização segura
           -> mcp-fiscal-brasil (parse/validate/consult)
           -> evidence envelope
           -> regras/teses APURA
           -> revisão humana
           -> relatório/ação
```

O envelope persistido pelo APURA deve incluir, no mínimo:

- `tool` e versão;
- `source_id` e classe de fonte;
- data/hora da coleta;
- período de vigência da regra/tabela, quando aplicável;
- input hash/document hash;
- resultado estruturado;
- limitações e fallbacks utilizados;
- evidências e fundamento;
- status de revisão humana.

## Conectores

No open source, prefira um protocolo de adapter estável (`list_documents`, `get_document`, `get_company`, `get_ledger_period`) e exemplos. Credenciais, refresh tokens, sincronização incremental e suporte específico de Omie, Conta Azul, Bling/Olist, TOTVS, Sankhya, Domínio, Alterdata, Senior, SAP etc. devem ficar no APURA ou em plugins independentes.

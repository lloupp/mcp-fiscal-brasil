# Roadmap fiscal 2026

## Estado atual

A base cobre 45 tools após a inclusão do catálogo de fontes, com MCP, SDK Python, CLI, REST API, pacote PyPI, documentação MkDocs e publicação no MCP Registry. O upstream também já possui NF-e com assinatura/DANFE/distribuição, SPED, eSocial, Simples/MEI, tabelas fiscais, indexadores BCB, importação e simulador da transição IBS/CBS.

## P0 — confiabilidade antes de ampliar cobertura

- [x] corrigir Simples/MEI para usar os campos reais do endpoint CNPJ da BrasilAPI;
- [x] parar de tratar consulta pública NF-e com CAPTCHA como API automatizada;
- [x] expor catálogo de proveniência para agentes;
- [x] remover vulnerabilidade conhecida de GitPython no lockfile;
- [x] conectar NFS-e nacional com certificado/mTLS configurável de ponta a ponta;
- [ ] versionar tabelas locais com `valid_from`, `valid_to` e fonte legal;
- [ ] rebaixar `risk_score_supplier` para triagem assistiva e exigir evidência adicional antes de qualquer decisão;
- [ ] substituir `compare_tax_regimes` por um motor de cenários parametrizado, sem “melhor regime” automático;
- [ ] adicionar limites de tamanho/streaming para XML/SPED em todas as interfaces;
- [ ] eliminar logs de identificadores fiscais completos quando não forem necessários.

## P1 — problemas fiscais de alto valor para agentes

- validação RTC de NF-e/NFC-e/NFS-e para IBS/CBS, CST e classificação tributária;
- CT-e e MDF-e: parse, chave, eventos, distribuição e validação;
- EFD-Reinf e integração conceitual com DCTFWeb/MIT;
- diagnóstico de EFD-Contribuições e transição das obrigações relacionadas à CBS;
- conciliação XML de entrada x SPED x razão/ERP;
- validação de cadastro fiscal de produtos: NCM/CEST/CFOP/CST/CSOSN com vigência;
- GNRE como adapter autenticado, sem scraping;
- saúde das fontes e capability discovery para agentes.

## P2 — ecossistema

- protocolo de adapters de ERP;
- conformance suite para providers;
- JSON Schemas versionados para todas as tools;
- exemplos LangChain/AI SDK/OpenAI Agents e clientes MCP genéricos;
- datasets de fixtures anonimizadas e golden tests;
- política formal de compatibilidade semântica;
- telemetria opt-in sem dados fiscais.

## Workflows compostos

### Recebimento fiscal

`XML -> parse -> assinatura/chave -> emitente -> classificação -> regras RTC -> conciliação -> achados`

### Fechamento

`SPED -> versão/período -> consistência estrutural -> cruzamento com XML/ERP -> divergências -> revisão`

### Fornecedor

`CNPJ -> situação cadastral -> regime -> certidões autorizadas -> evidências -> fila de revisão`

Não deve haver aprovação/recusa automática baseada apenas no score atual.

### Reforma tributária

`cadastro de item/serviço -> classificação -> IBS/CBS -> validação do documento -> impacto por período -> evidências`

As alíquotas de referência usadas em simulações devem ser rotuladas como premissas quando não forem valores legais definitivos.

# Módulo NFS-e

O projeto trata a NFS-e como um ecossistema híbrido: **Sistema Nacional NFS-e/ADN quando disponível e autorizado**, com fallback explícito para sistemas municipais.

## Tool MCP

- `consultar_nfse(numero, municipio, uf, cnpj_prestador?)` — tenta a ADN primeiro quando há A1 configurado; caso contrário retorna orientação municipal com a causa do fallback.

## Autenticação

A API nacional autenticada exige ICP-Brasil/mTLS. Configure:

```bash
NFSE_CERTIFICADO_PATH=/secrets/certificado.pfx
NFSE_CERTIFICADO_SENHA=<secret>
```

Se essas variáveis não estiverem definidas, a implementação pode reutilizar `NFE_CERTIFICADO_PATH` / `NFE_CERTIFICADO_SENHA`.

Credenciais pertencem ao processo/secret manager e não devem ser fornecidas pelo agente como argumentos.

## Reforma tributária

Os leiautes nacionais evoluem durante 2026 para suportar IBS/CBS. O projeto deve tratar XSD, notas técnicas e anexos de domínio como artefatos versionados por vigência; parsing genérico não equivale a validação RTC.

Referências oficiais:

- Documentação técnica NFS-e: https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica
- Reforma Tributária / NFS-e: https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica/documentacao-atual/nfs-e-reforma-tributaria

## Próximos passos

- validação XSD por versão/vigência;
- extração normalizada dos grupos IBS/CBS;
- catálogo de municípios aderentes/capabilities, sem scraping;
- adapters municipais explícitos e testáveis;
- fixtures oficiais/anonimizadas para testes de contrato.

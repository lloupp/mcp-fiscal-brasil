# Módulo NF-e / NFC-e

Infraestrutura para validação, parsing, DANFE, assinatura, distribuição e eventos fiscais.

## Tools MCP

- `consultar_nfe(chave_acesso)` — usa provedor autorizado opt-in quando configurado; sem provider retorna apenas metadados determinísticos da chave.
- `consultar_nfce(chave_acesso)` — equivalente para NFC-e modelo 65.
- `validar_chave_nfe(chave_acesso)` — validação offline do DV e extração dos campos codificados na chave.
- `parse_nfe_xml(xml_content)` — parse estruturado do XML recebido pelo usuário/sistema.
- `gerar_danfe(xml_content)` — gera DANFE PDF a partir de XML modelo 55.
- `validar_assinatura_nfe(xml_content, ca_bundle?)` — valida XMLDSig; cadeia ICP-Brasil é opcional quando um bundle confiável é informado.
- `consultar_status_sefaz(uf)` — status real do webservice via mTLS/A1.
- `baixar_nfe_distribuicao(...)` — NFeDistribuicaoDFe oficial via A1 configurado no processo.
- `manifestar_nfe(...)` — manifestação do destinatário via SEFAZ.

## Fonte oficial para XML e eventos

A consulta pública do Portal Nacional por chave é destinada a uso humano e emprega CAPTCHA. O projeto **não raspa nem contorna esse mecanismo**.

Para automação de documentos oficiais use `NFeDistribuicaoDFe` com certificado A1 e autorização do ator. As credenciais ficam fora do schema MCP:

```bash
NFE_CERTIFICADO_PATH=/secrets/certificado.pfx
NFE_CERTIFICADO_SENHA=<secret>
```

A senha nunca deve ser enviada como argumento da tool.

## Parser XML

```python
from mcp_fiscal_brasil.nfe.xml_parser import parse_nfe_xml

with open("nota.xml", "rb") as f:
    nfe = parse_nfe_xml(f.read(), chave="")
print(nfe.emitente.razao_social)
print(nfe.totais.valor_nota)
```

## Tool agentic

Para validação consolidada (XML + chave + emissor), use [`validate_nfe_full`](../agentic/nfe.md).

Quando chamada via MCP por caminho de arquivo, a leitura é restrita a `MCP_FISCAL_FILE_BASE_DIR`. Para integração server-side, prefira o SDK Python com bytes/conteúdo já obtidos dentro da fronteira de segurança da aplicação.

## Compatibilidade

- Layout principal: NF-e/NFC-e 4.00;
- namespace: `http://www.portalfiscal.inf.br/nfe`;
- webservices oficiais: SEFAZ / Ambiente Nacional com mTLS;
- provider privado é sempre opt-in e não substitui a proveniência oficial.

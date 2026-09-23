# Confiabilidade e proveniência das fontes

O MCP Fiscal Brasil deve permitir que um agente diferencie **dado autoritativo**, **dado operacional derivado** e **estimativa**. Uma resposta fiscal sem origem explícita não deve ser tratada como evidência suficiente para decisão contábil ou jurídica.

## Classes de fonte

| Classe | Uso | Exemplos |
|---|---|---|
| Autoridade oficial | Evidência primária quando o endpoint e o ator estão autorizados | SEFAZ/NFeDistribuicaoDFe, SPED/RFB, Sistema Nacional NFS-e, BCB, IBGE |
| Agregador | Conveniência operacional, com confirmação oficial quando a decisão for material | BrasilAPI |
| Provedor privado | Cobertura adicional opt-in; origem deve permanecer visível | ReceitaWS, cpfcnpj.com.br |
| Tabela local | Validação determinística e offline, condicionada à versão/vigência | NCM, CFOP, CEST, CST/CSOSN, ICMS |

A tool MCP `listar_fontes_fiscais` expõe este catálogo aos agentes.

## Regras de uso por domínio

### CNPJ, Simples e MEI

A BrasilAPI é um agregador comunitário. Os indicadores de opção pelo Simples e pelo MEI são campos do endpoint `/cnpj/v1/{cnpj}`; o projeto não deve depender de um endpoint `/simples/v1` inexistente.

Para decisões materiais, o agente deve preservar a origem e encaminhar casos inconclusivos para confirmação em fonte oficial/autorizada.

### NF-e e NFC-e

A consulta pública por chave no Portal Nacional usa mecanismo anti-automação. O projeto não deve raspar CAPTCHA nem apresentar essa página como API.

- metadados codificados na chave: validação offline;
- XML/eventos oficiais: `NFeDistribuicaoDFe` com certificado A1 e autorização do ator;
- cobertura adicional: provider privado opt-in, sempre identificado.

### NFS-e

Existe padrão nacional e APIs oficiais. A automação autenticada usa ICP-Brasil/mTLS e depende da participação/permissões do município e do ator. Fallbacks municipais devem ser conectores explícitos, não scraping silencioso.

### SPED

Parsing e sumarização podem ser offline, mas layouts e regras têm vigência. O parser deve registrar tipo, versão/período e não inferir IBS/CBS como se fossem registros da EFD-ICMS/IPI quando a especificação oficial não os inclui.

## Política para agentes

1. Prefira cálculo determinístico e fonte oficial.
2. Nunca transforme ausência de resposta em fato negativo sem sinalizar incerteza.
3. Não esconda fallback de provedor.
4. Não use heurística de score como decisão automática de contratar, recusar, autuar ou recuperar crédito.
5. Mantenha data de consulta, versão da tool e limitações junto do resultado quando o dado for persistido.
6. Para alto volume, use fontes/licenças próprias; não faça crawling de APIs comunitárias.

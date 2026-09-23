"""Metadados de proveniencia e confiabilidade das fontes fiscais.

Este modulo nao consulta fontes externas. Ele fornece um catalogo deterministico para
que agentes saibam se uma resposta vem de autoridade oficial, agregador, provedor
privado ou tabela local e escolham o workflow adequado.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

TipoFonte = Literal["oficial", "agregador", "privada", "local"]
NivelConfiabilidade = Literal["autoridade", "alta", "condicional"]


class FonteFiscal(BaseModel):
    id: str
    nome: str
    tipo: TipoFonte
    confiabilidade: NivelConfiabilidade
    dominios: list[str]
    autenticacao: str
    uso_recomendado: str
    limitacoes: list[str] = Field(default_factory=list)


_FONTES: tuple[FonteFiscal, ...] = (
    FonteFiscal(
        id="sefaz_nfe",
        nome="SEFAZ / Ambiente Nacional NF-e",
        tipo="oficial",
        confiabilidade="autoridade",
        dominios=["nfe", "nfce", "distribuicao_dfe", "status_sefaz"],
        autenticacao="Certificado digital A1/mTLS para webservices automatizados.",
        uso_recomendado="Fonte primaria para XML, eventos, distribuicao e status fiscal.",
        limitacoes=[
            "Consulta publica por chave usa mecanismo anti-automacao e nao deve ser raspada.",
            "O ator consultante precisa ter autorizacao para documentos protegidos.",
        ],
    ),
    FonteFiscal(
        id="nfse_nacional",
        nome="Sistema Nacional NFS-e / ADN",
        tipo="oficial",
        confiabilidade="autoridade",
        dominios=["nfse"],
        autenticacao="ICP-Brasil/mTLS conforme o endpoint e papel do ator.",
        uso_recomendado="Fonte primaria quando o municipio/documento participa do padrao nacional.",
        limitacoes=[
            "Cobertura e permissoes dependem da adesao municipal e do papel do consultante."
        ],
    ),
    FonteFiscal(
        id="sped",
        nome="SPED / Receita Federal",
        tipo="oficial",
        confiabilidade="autoridade",
        dominios=["sped", "efd_icms_ipi", "efd_contribuicoes", "ecd", "ecf"],
        autenticacao="Nenhuma para especificacoes; arquivos do contribuinte sao fornecidos localmente.",
        uso_recomendado="Layouts e regras oficiais; parsing pode ser feito offline.",
        limitacoes=["Layouts mudam por versao e periodo de vigencia."],
    ),
    FonteFiscal(
        id="brasilapi",
        nome="BrasilAPI",
        tipo="agregador",
        confiabilidade="alta",
        dominios=["cnpj", "simples", "mei", "cep"],
        autenticacao="Nenhuma.",
        uso_recomendado="Consulta operacional de baixo volume com proveniencia explicita.",
        limitacoes=[
            "Projeto comunitario, nao e autoridade fiscal.",
            "Nao possui endpoint /simples/v1 nem /nfe/v1; Simples/MEI usam campos de /cnpj/v1.",
            "Termos desencorajam crawling e varreduras de alto volume.",
        ],
    ),
    FonteFiscal(
        id="receitaws",
        nome="ReceitaWS",
        tipo="privada",
        confiabilidade="condicional",
        dominios=["cnpj"],
        autenticacao="Conforme plano/limites do provedor.",
        uso_recomendado="Fallback cadastral, nunca como autoridade juridica.",
        limitacoes=[
            "Servico privado de terceiros; disponibilidade e atualizacao nao sao controladas pelo projeto."
        ],
    ),
    FonteFiscal(
        id="cpfcnpj",
        nome="cpfcnpj.com.br",
        tipo="privada",
        confiabilidade="condicional",
        dominios=["cnpj", "nfe", "nfce"],
        autenticacao="Token opcional.",
        uso_recomendado="Provider opt-in para cobertura adicional quando contratado.",
        limitacoes=["Servico pago/terceiro; respostas devem manter identificacao da origem."],
    ),
    FonteFiscal(
        id="bcb",
        nome="Banco Central do Brasil",
        tipo="oficial",
        confiabilidade="autoridade",
        dominios=["selic", "ipca", "ptax", "correcao_monetaria"],
        autenticacao="Nenhuma para APIs publicas usadas.",
        uso_recomendado="Fonte primaria para series economicas e cambiais.",
    ),
    FonteFiscal(
        id="ibge",
        nome="IBGE",
        tipo="oficial",
        confiabilidade="autoridade",
        dominios=["cnae", "municipios", "estados"],
        autenticacao="Nenhuma para APIs publicas usadas.",
        uso_recomendado="Fonte primaria para classificacoes e geografia oficial.",
    ),
    FonteFiscal(
        id="tabelas_locais",
        nome="Tabelas fiscais empacotadas",
        tipo="local",
        confiabilidade="condicional",
        dominios=["ncm", "cfop", "cest", "cst", "csosn", "icms"],
        autenticacao="Nenhuma.",
        uso_recomendado="Validacao deterministica/offline quando a versao da tabela e adequada ao periodo.",
        limitacoes=["Exige controle de versao, data de vigencia e rotina de atualizacao."],
    ),
)


def listar_fontes_fiscais(dominio: str | None = None) -> list[FonteFiscal]:
    """Lista fontes conhecidas, opcionalmente filtradas por dominio fiscal."""
    if dominio is None:
        return list(_FONTES)

    alvo = dominio.strip().casefold()
    return [
        fonte
        for fonte in _FONTES
        if any(alvo == item.casefold() for item in fonte.dominios)
    ]

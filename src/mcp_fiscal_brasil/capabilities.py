"""Descoberta de capacidades fiscais disponíveis no runtime.

Nenhum segredo, caminho local ou token é retornado. O objetivo é permitir que
agentes escolham um workflow compatível antes de tentar uma operação.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from . import __version__
from ._core.config import settings

CapabilityMode = Literal["offline", "public_api", "authorized_api", "provider", "hybrid"]


class FiscalCapability(BaseModel):
    id: str
    available: bool
    mode: CapabilityMode
    source_ids: list[str] = Field(default_factory=list)
    requires: list[str] = Field(default_factory=list)
    fallback: str | None = None
    notes: list[str] = Field(default_factory=list)


class FiscalCapabilitiesReport(BaseModel):
    version: str = __version__
    capabilities: list[FiscalCapability]


def _configured_file(path_value: str) -> bool:
    if not path_value.strip():
        return False
    try:
        return Path(path_value).expanduser().resolve().is_file()
    except OSError:
        return False


def listar_capacidades_fiscais() -> FiscalCapabilitiesReport:
    """Retorna capabilities sem revelar configuração sensível."""
    nfe_a1 = bool(settings.nfe_certificado_senha) and _configured_file(
        settings.nfe_certificado_path
    )
    nfse_path = settings.nfse_certificado_path or settings.nfe_certificado_path
    nfse_senha = settings.nfse_certificado_senha or settings.nfe_certificado_senha
    nfse_a1 = bool(nfse_senha) and _configured_file(nfse_path)
    provider = bool(settings.cpfcnpj_token.strip())

    capabilities = [
        FiscalCapability(
            id="cnpj_lookup",
            available=True,
            mode="hybrid" if provider else "public_api",
            source_ids=["cpfcnpj", "brasilapi", "receitaws"] if provider else ["brasilapi", "receitaws"],
            fallback="ReceitaWS após falha da BrasilAPI; provider privado somente quando configurado.",
        ),
        FiscalCapability(
            id="simples_mei",
            available=True,
            mode="public_api",
            source_ids=["brasilapi"],
            fallback="Tratar campos nulos/ausentes como não confirmados, não como evidência definitiva.",
        ),
        FiscalCapability(
            id="nfe_key_validation",
            available=True,
            mode="offline",
            source_ids=["tabelas_locais"],
            fallback="Extrai apenas metadados codificados na chave; não confirma autorização da nota.",
        ),
        FiscalCapability(
            id="nfe_full_lookup",
            available=provider,
            mode="provider",
            source_ids=["cpfcnpj"] if provider else [],
            requires=[] if provider else ["CPFCNPJ_TOKEN ou NFeDistribuicaoDFe/A1"],
            fallback="Sem provider, retornar metadados da chave ou usar distribuição oficial com A1.",
        ),
        FiscalCapability(
            id="nfe_distribution",
            available=nfe_a1,
            mode="authorized_api",
            source_ids=["sefaz_nfe"],
            requires=[] if nfe_a1 else ["NFE_CERTIFICADO_PATH", "NFE_CERTIFICADO_SENHA"],
            fallback="Sem A1, não tentar scraping do Portal Nacional.",
        ),
        FiscalCapability(
            id="nfe_status_sefaz",
            available=nfe_a1,
            mode="authorized_api",
            source_ids=["sefaz_nfe"],
            requires=[] if nfe_a1 else ["NFE_CERTIFICADO_PATH", "NFE_CERTIFICADO_SENHA"],
        ),
        FiscalCapability(
            id="nfse_nacional",
            available=nfse_a1,
            mode="authorized_api",
            source_ids=["nfse_nacional"],
            requires=[] if nfse_a1 else ["NFSE_CERTIFICADO_* ou NFE_CERTIFICADO_*"],
            fallback="Orientação municipal explícita quando a API nacional não puder ser usada.",
        ),
        FiscalCapability(
            id="sped_analysis",
            available=True,
            mode="offline",
            source_ids=["sped"],
            notes=["Arquivos por caminho via MCP ficam restritos a MCP_FISCAL_FILE_BASE_DIR."],
        ),
        FiscalCapability(
            id="reforma_tributaria_simulation",
            available=True,
            mode="offline",
            source_ids=["tabelas_locais"],
            notes=["Simulação usa premissas declaradas; não substitui cálculo jurídico/contábil."],
        ),
        FiscalCapability(
            id="import_tax_estimate",
            available=True,
            mode="offline",
            source_ids=["tabelas_locais"],
            notes=["TEC/benefícios/regimes especiais podem exigir parâmetros ou fonte externa."],
        ),
    ]
    return FiscalCapabilitiesReport(capabilities=capabilities)

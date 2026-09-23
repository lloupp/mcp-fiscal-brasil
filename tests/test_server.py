"""Testes do servidor MCP (rotas HTTP customizadas)."""

from __future__ import annotations

import inspect

import pytest
from starlette.testclient import TestClient

from mcp_fiscal_brasil._core.config import settings
from mcp_fiscal_brasil.server import (
    _nfe_credentials_from_settings,
    _validated_local_file,
    app,
    tool_baixar_nfe_distribuicao,
    tool_manifestar_nfe,
)


def test_health_route_disponivel_no_transporte_http() -> None:
    """FastMCP so expoe /mcp por padrao nos transportes http/sse.

    /health precisa estar registrada explicitamente para o healthcheck do
    Docker funcionar (ver scripts/docker_healthcheck.py) quando o container
    roda com --transport http/sse em vez do stdio padrao.
    """
    http_app = app.http_app(transport="http")
    with TestClient(http_app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_tools_sefaz_nao_expoem_segredos_no_schema_python() -> None:
    """Senha/caminho do A1 devem vir do processo, não do contexto do agente."""
    baixar = inspect.signature(tool_baixar_nfe_distribuicao)
    manifestar = inspect.signature(tool_manifestar_nfe)

    for assinatura in (baixar, manifestar):
        assert "senha" not in assinatura.parameters
        assert "caminho_certificado" not in assinatura.parameters


def test_validated_local_file_restringe_ao_diretorio_configurado(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = tmp_path / "allowed"
    base.mkdir()
    permitido = base / "nota.xml"
    permitido.write_text("<xml/>", encoding="utf-8")
    fora = tmp_path / "fora.xml"
    fora.write_text("<xml/>", encoding="utf-8")

    monkeypatch.setattr(settings, "mcp_fiscal_file_base_dir", str(base))

    assert _validated_local_file(str(permitido), label="XML") == permitido.resolve()
    with pytest.raises(ValueError, match="fora do diretório permitido"):
        _validated_local_file(str(fora), label="XML")


def test_nfe_credentials_somente_por_configuracao(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cert = tmp_path / "certificado.pfx"
    cert.write_bytes(b"fixture")

    monkeypatch.setattr(settings, "nfe_certificado_path", str(cert))
    monkeypatch.setattr(settings, "nfe_certificado_senha", "segredo-teste")

    caminho, senha = _nfe_credentials_from_settings()
    assert caminho == str(cert.resolve())
    assert senha == "segredo-teste"

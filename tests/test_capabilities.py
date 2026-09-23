import json

import pytest

from mcp_fiscal_brasil._core.config import settings
from mcp_fiscal_brasil.capabilities import listar_capacidades_fiscais


def _by_id():
    report = listar_capacidades_fiscais()
    return {item.id: item for item in report.capabilities}


def test_capabilities_basicas_disponiveis_sem_valores_secretos(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "nfe_certificado_senha", "segredo-capability-teste")
    monkeypatch.setattr(settings, "cpfcnpj_token", "token-capability-teste")

    data = listar_capacidades_fiscais().model_dump(mode="json")
    serializado = json.dumps(data)

    assert _by_id()["nfe_key_validation"].available is True
    assert _by_id()["sped_analysis"].available is True
    assert "segredo-capability-teste" not in serializado
    assert "token-capability-teste" not in serializado


def test_nfe_distribution_reflete_configuracao_a1(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cert = tmp_path / "a1.pfx"
    cert.write_bytes(b"fixture")
    monkeypatch.setattr(settings, "nfe_certificado_path", str(cert))
    monkeypatch.setattr(settings, "nfe_certificado_senha", "segredo")

    caps = _by_id()
    assert caps["nfe_distribution"].available is True
    assert caps["nfe_status_sefaz"].available is True
    assert caps["nfe_distribution"].requires == []


def test_nfe_distribution_indisponivel_sem_a1(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "nfe_certificado_path", "")
    monkeypatch.setattr(settings, "nfe_certificado_senha", "")

    cap = _by_id()["nfe_distribution"]
    assert cap.available is False
    assert "NFE_CERTIFICADO_PATH" in cap.requires


def test_provider_premium_so_aparece_quando_configurado(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "cpfcnpj_token", "")
    assert _by_id()["nfe_full_lookup"].available is False

    monkeypatch.setattr(settings, "cpfcnpj_token", "token-teste")
    assert _by_id()["nfe_full_lookup"].available is True

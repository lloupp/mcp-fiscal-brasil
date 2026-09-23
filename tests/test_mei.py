from unittest.mock import patch

import pytest

from mcp_fiscal_brasil._core.errors import FiscalHTTPError, FiscalNotFoundError
from mcp_fiscal_brasil.mei.client import MEIClient


@pytest.fixture
def client():
    return MEIClient()


@pytest.fixture
def cnpj_digits(cnpj_valido: str) -> str:
    return "".join(c for c in cnpj_valido if c.isdigit())


@pytest.mark.asyncio
async def test_get_mei_status_success(client, cnpj_digits):
    with patch("mcp_fiscal_brasil._core.http.HTTPClient.get") as mock_get:
        mock_get.return_value = {
            "opcao_pelo_simples": True,
            "opcao_pelo_mei": True,
            "data_opcao_pelo_mei": "2020-01-01",
        }
        result = await client.get_mei_status(cnpj_digits)
        assert result.mei is True
        assert result.simples_nacional is True
        assert result.data_opcao_mei is not None
        mock_get.assert_awaited_once_with(f"/cnpj/v1/{cnpj_digits}")


@pytest.mark.asyncio
async def test_get_mei_status_false(client, cnpj_digits):
    with patch("mcp_fiscal_brasil._core.http.HTTPClient.get") as mock_get:
        mock_get.return_value = {
            "opcao_pelo_mei": False,
            "opcao_pelo_simples": False,
        }
        result = await client.get_mei_status(cnpj_digits)
        assert result.mei is False
        assert result.simples_nacional is False


@pytest.mark.asyncio
async def test_get_mei_status_not_found(client, cnpj_digits):
    with patch("mcp_fiscal_brasil._core.http.HTTPClient.get") as mock_get:
        mock_get.side_effect = FiscalHTTPError("Not found", 404, "http://test")
        with pytest.raises(FiscalNotFoundError):
            await client.get_mei_status(cnpj_digits)


@pytest.mark.asyncio
async def test_get_mei_status_cnpj_invalido_nao_chama_api(client):
    with patch("mcp_fiscal_brasil._core.http.HTTPClient.get") as mock_get:
        with pytest.raises(FiscalNotFoundError):
            await client.get_mei_status("123")
        mock_get.assert_not_called()

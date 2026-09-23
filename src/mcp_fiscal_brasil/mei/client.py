from datetime import date

from mcp_fiscal_brasil._core import FiscalNotFoundError, HTTPClient, get_logger, settings
from mcp_fiscal_brasil._core.errors import FiscalHTTPError

from ..shared.validators import normalizar_cnpj, validate_cnpj_qualquer
from .schemas import MEIStatus

logger = get_logger(__name__)


class MEIClient:
    """Consulta o indicador MEI exposto no endpoint CNPJ da BrasilAPI."""

    def _http_client(self) -> HTTPClient:
        return HTTPClient(
            settings.brasilapi_base_url,
            timeout=settings.mcp_fiscal_http_timeout,
            max_retries=settings.mcp_fiscal_max_retries,
            cache_ttl=settings.mcp_fiscal_cache_ttl,
            rate_limit_per_second=settings.mcp_fiscal_rate_limit,
        )

    def _parse_date(self, date_str: str | None) -> date | None:
        if not date_str:
            return None
        try:
            return date.fromisoformat(date_str[:10])
        except ValueError:
            return None

    async def get_mei_status(self, cnpj: str) -> MEIStatus:
        """Consulta indicadores de MEI e Simples no cadastro público agregado do CNPJ."""
        cnpj_clean = normalizar_cnpj(cnpj)
        if not validate_cnpj_qualquer(cnpj_clean):
            raise FiscalNotFoundError("CNPJ inválido", "CNPJ", cnpj_clean)

        logger.info("mei_status_started", cnpj=cnpj_clean)
        async with self._http_client() as client:
            try:
                data = await client.get(f"/cnpj/v1/{cnpj_clean}")
            except FiscalHTTPError as exc:
                if exc.status_code == 404:
                    raise FiscalNotFoundError(
                        "CNPJ não encontrado na fonte cadastral", "CNPJ", cnpj_clean
                    ) from exc
                raise

        return MEIStatus(
            cnpj=cnpj_clean,
            mei=bool(data.get("opcao_pelo_mei"))
            if data.get("opcao_pelo_mei") is not None
            else False,
            data_opcao_mei=self._parse_date(data.get("data_opcao_pelo_mei")),
            data_exclusao_mei=self._parse_date(data.get("data_exclusao_do_mei")),
            simples_nacional=bool(data.get("opcao_pelo_simples"))
            if data.get("opcao_pelo_simples") is not None
            else False,
        )

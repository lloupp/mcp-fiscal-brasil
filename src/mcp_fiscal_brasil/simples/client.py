from datetime import date

from mcp_fiscal_brasil._core import (
    FiscalNotFoundError,
    HTTPClient,
    get_logger,
    settings,
)
from mcp_fiscal_brasil._core.errors import FiscalHTTPError

from ..shared.validators import normalizar_cnpj, validate_cnpj_qualquer
from .schemas import SimplesStatus

logger = get_logger(__name__)


class SimplesClient:
    """Consulta indicadores do Simples Nacional e MEI expostos no endpoint CNPJ da BrasilAPI.

    A BrasilAPI não possui um endpoint `/simples/v1`. Os campos de opção pelo
    Simples/MEI fazem parte de `/cnpj/v1/{cnpj}`, que agrega dados públicos.
    A BrasilAPI é uma fonte comunitária/derivada, não a autoridade fiscal.
    """

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

    async def get_simples_status(self, cnpj: str) -> SimplesStatus:
        """Consulta os indicadores de Simples Nacional/MEI presentes no cadastro CNPJ."""
        cnpj_clean = normalizar_cnpj(cnpj)
        if not validate_cnpj_qualquer(cnpj_clean):
            raise FiscalNotFoundError("CNPJ inválido", "CNPJ", cnpj_clean)

        logger.info("simples_status_started", cnpj=cnpj_clean)
        async with self._http_client() as client:
            try:
                data = await client.get(f"/cnpj/v1/{cnpj_clean}")
            except FiscalHTTPError as exc:
                if exc.status_code == 404:
                    raise FiscalNotFoundError(
                        "CNPJ não encontrado na fonte cadastral", "CNPJ", cnpj_clean
                    ) from exc
                raise

        simples_raw = data.get("opcao_pelo_simples")
        mei_raw = data.get("opcao_pelo_mei")
        fonte_confirmada = simples_raw is not None or mei_raw is not None

        return SimplesStatus(
            cnpj=cnpj_clean,
            simples_nacional=bool(simples_raw) if simples_raw is not None else False,
            data_opcao=self._parse_date(data.get("data_opcao_pelo_simples")),
            data_exclusao=self._parse_date(data.get("data_exclusao_do_simples")),
            mei=bool(mei_raw) if mei_raw is not None else False,
            data_opcao_mei=self._parse_date(data.get("data_opcao_pelo_mei")),
            data_exclusao_mei=self._parse_date(data.get("data_exclusao_do_mei")),
            fonte_confirmada=fonte_confirmada,
        )

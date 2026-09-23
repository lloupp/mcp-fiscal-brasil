from mcp_fiscal_brasil.fontes import listar_fontes_fiscais


def test_lista_fontes_inclui_autoridades_e_agregadores() -> None:
    fontes = listar_fontes_fiscais()
    por_id = {fonte.id: fonte for fonte in fontes}

    assert por_id["sefaz_nfe"].tipo == "oficial"
    assert por_id["sefaz_nfe"].confiabilidade == "autoridade"
    assert por_id["brasilapi"].tipo == "agregador"
    assert por_id["receitaws"].tipo == "privada"


def test_filtro_por_dominio_nfe_nao_confunde_fontes() -> None:
    fontes = listar_fontes_fiscais("nfe")
    ids = {fonte.id for fonte in fontes}

    assert "sefaz_nfe" in ids
    assert "cpfcnpj" in ids
    assert "brasilapi" not in ids


def test_filtro_desconhecido_retorna_lista_vazia() -> None:
    assert listar_fontes_fiscais("dominio-inexistente") == []

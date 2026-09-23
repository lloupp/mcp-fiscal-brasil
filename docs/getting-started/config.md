# Configuracao

## Variaveis de ambiente

Todas opcionais, com defaults razoaveis.

| Variavel | Default | Descricao |
|----------|---------|-----------|
| `MCP_FISCAL_HTTP_TIMEOUT` | `30` | Timeout HTTP em segundos |
| `MCP_FISCAL_MAX_RETRIES` | `3` | Maximo de retries por requisicao |
| `MCP_FISCAL_CACHE_TTL` | `300` | TTL do cache em segundos |
| `MCP_FISCAL_RATE_LIMIT` | `10` | Requests por segundo (por host) |
| `MCP_FISCAL_CACHE_BACKEND` | `memory` | `memory`, `sqlite` ou `redis` |
| `MCP_FISCAL_REDIS_URL` | - | URL do Redis (se `cache_backend=redis`) |
| `MCP_FISCAL_LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `MCP_FISCAL_FILE_BASE_DIR` | `~/.local/share/mcp-fiscal-brasil/files` | Diretório único que tools MCP podem ler por caminho |
| `NFE_CERTIFICADO_PATH` | - | Certificado A1 para webservices SEFAZ |
| `NFE_CERTIFICADO_SENHA` | - | Credencial do A1; use secret manager em produção |
| `NFSE_CERTIFICADO_PATH` | fallback NFe | A1 para API Nacional NFS-e (ADN) |
| `NFSE_CERTIFICADO_SENHA` | fallback NFe | Credencial do A1 usado na NFS-e |

Exemplo `.env`:

```bash
MCP_FISCAL_HTTP_TIMEOUT=60
MCP_FISCAL_CACHE_TTL=3600
MCP_FISCAL_RATE_LIMIT=5
MCP_FISCAL_LOG_LEVEL=DEBUG

# Somente quando usar webservices autenticados:
# NFE_CERTIFICADO_PATH=/secrets/certificado.pfx
# NFE_CERTIFICADO_SENHA=<secret>
# NFSE_CERTIFICADO_PATH=/secrets/certificado-nfse.pfx
# NFSE_CERTIFICADO_SENHA=<secret>
```

!!! warning "Certificados, credenciais e arquivos locais"

    Não versione arquivos A1 nem credenciais. Em produção, monte o certificado por volume
    seguro e injete a credencial pelo secret manager. As tools MCP de distribuição/manifestação
    **não recebem senha nem caminho do A1 como argumentos**: usam apenas `NFE_CERTIFICADO_*`
    do processo. Se `NFSE_CERTIFICADO_*` não estiver definido, o cliente nacional de NFS-e
    reutiliza `NFE_CERTIFICADO_*` quando disponível.

    Tools que recebem caminho de XML/SPED só podem ler arquivos sob
    `MCP_FISCAL_FILE_BASE_DIR`. Isso evita que um agente use a tool como leitor arbitrário
    do filesystem do host.

## Cliente MCP

### Claude Desktop

Adicione em `claude_desktop_config.json`:

=== "macOS / Linux"

    Arquivo: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) ou `~/.config/Claude/claude_desktop_config.json` (Linux).

    ```json
    {
      "mcpServers": {
        "fiscal-brasil": {
          "command": "mcp-fiscal-brasil",
          "args": []
        }
      }
    }
    ```

=== "Windows"

    Arquivo: `%APPDATA%\Claude\claude_desktop_config.json`.

    ```json
    {
      "mcpServers": {
        "fiscal-brasil": {
          "command": "mcp-fiscal-brasil.exe",
          "args": []
        }
      }
    }
    ```

Reinicie o Claude Desktop. O servidor aparece como `fiscal-brasil` com 45 ferramentas.

### Claude Code (CLI)

```bash
claude mcp add fiscal-brasil mcp-fiscal-brasil
```

### Cursor

Adicione em Settings -> MCP Servers:

```json
{
  "mcpServers": {
    "fiscal-brasil": {
      "command": "mcp-fiscal-brasil"
    }
  }
}
```

### Outros clientes MCP

Qualquer cliente compatível com MCP funciona. O servidor expoe via stdio por padrao. Para HTTP transport:

```bash
mcp-fiscal-brasil --transport http --port 8000
```

## Cache em produção

Em produção, prefira `sqlite` ou `redis`:

```bash
MCP_FISCAL_CACHE_BACKEND=sqlite
# armazena em ~/.cache/mcp-fiscal-brasil.db

MCP_FISCAL_CACHE_BACKEND=redis
MCP_FISCAL_REDIS_URL=redis://localhost:6379/0
```

## Logs estruturados

Em produção, logs são emitidos como JSON via `structlog`:

```json
{
  "event": "cnpj_lookup_started",
  "cnpj": "12345678000190",
  "timestamp": "2026-05-20T10:30:00Z",
  "level": "info"
}
```

Ideal para parsing em Loki, Datadog, CloudWatch, etc.

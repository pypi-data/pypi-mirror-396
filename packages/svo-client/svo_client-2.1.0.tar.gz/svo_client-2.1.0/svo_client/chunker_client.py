"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Async adapter-only client for SVO semantic chunker.
Always executes `chunk` via queue and exposes one-shot call plus
explicit queue helpers.
"""
# mypy: disable-error-code=import-untyped

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from embed_client.config_generator import (
    ClientConfigGenerator,
)  # type: ignore[import-untyped]
from mcp_proxy_adapter.client.jsonrpc_client import (
    JsonRpcClient,
)  # type: ignore[import-untyped]
from mcp_proxy_adapter.client.jsonrpc_client.transport import (
    JsonRpcTransport,
)  # type: ignore[import-untyped]
from svo_client.errors import (
    SVOConnectionError,
    SVOHTTPError,
    SVOJSONRPCError,
    SVOServerError,
    SVOTimeoutError,
)

if TYPE_CHECKING:
    from chunk_metadata_adapter import (  # type: ignore[import-untyped]
        SemanticChunk,
    )


class ChunkerClient:
    """Adapter-only client with queued chunk execution."""

    def __init__(
        self,
        *,
        config: Optional[Dict[str, Any]] = None,
        host: str = "localhost",
        port: int = 8009,
        cert: Optional[str] = None,
        key: Optional[str] = None,
        ca: Optional[str] = None,
        token: Optional[str] = None,
        token_header: str = "X-API-Key",
        check_hostname: bool = False,
        timeout: float = 30.0,
        poll_interval: float = 1.0,
    ):
        cfg = config or self._generate_config(
            host=host,
            port=port,
            cert=cert,
            key=key,
            ca=ca,
            token=token,
            token_header=token_header,
        )

        protocol, client_kwargs = self._config_to_client_kwargs(
            cfg, check_hostname=check_hostname
        )
        self.protocol = protocol
        self.host = client_kwargs["host"]
        self.port = client_kwargs["port"]
        self.timeout = timeout
        self.poll_interval = poll_interval

        self._client = JsonRpcClient(**client_kwargs)
        if isinstance(self._client, JsonRpcTransport):
            self._client.timeout = timeout

    @staticmethod
    def _generate_config(
        *,
        host: str,
        port: int,
        cert: Optional[str],
        key: Optional[str],
        ca: Optional[str],
        token: Optional[str],
        token_header: str,
    ) -> Dict[str, Any]:
        generator = ClientConfigGenerator()
        if cert or key or ca:
            cfg = generator.generate_mtls_config(
                host=host,
                port=port,
                cert_file=cert,
                key_file=key,
                ca_cert_file=ca,
            )
        else:
            cfg = generator.generate_http_config(host=host, port=port)
        if token:
            cfg = generator.generate_https_token_config(
                host=host,
                port=port,
                api_key=token,
                cert_file=cert,
                key_file=key,
                ca_cert_file=ca,
            )
            cfg["auth"]["header"] = token_header
        return cfg

    @staticmethod
    def _config_to_client_kwargs(
        cfg: Dict[str, Any], *, check_hostname: bool
    ) -> tuple[str, Dict[str, Any]]:
        server = cfg.get("server", {})
        ssl_cfg = cfg.get("ssl", {}) or {}
        auth_cfg = cfg.get("auth", {}) or {}

        protocol = "http"
        if ssl_cfg.get("enabled"):
            verify_mode = ssl_cfg.get("verify_mode")
            protocol = "mtls" if verify_mode == "CERT_REQUIRED" else "https"

        token_header = auth_cfg.get("header", "X-API-Key")
        token_value = None
        if auth_cfg.get("method") == "api_key":
            api_keys = auth_cfg.get("api_keys") or {}
            token_value = next(iter(api_keys.values()), None)

        kwargs = {
            "protocol": protocol,
            "host": server.get("host", "localhost"),
            "port": int(server.get("port", 8009)),
            "token_header": token_header if token_value else None,
            "token": token_value,
            "cert": ssl_cfg.get("cert_file"),
            "key": ssl_cfg.get("key_file"),
            "ca": ssl_cfg.get("ca_cert_file"),
            "check_hostname": ssl_cfg.get("check_hostname", check_hostname),
        }
        return protocol, kwargs

    async def close(self) -> None:
        """Close the underlying adapter client."""
        await self._client.close()

    async def __aenter__(self) -> "ChunkerClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    def _map_exception(self, exc: Exception) -> Exception:
        """Convert transport-level exceptions to domain-specific errors."""
        name = type(exc).__name__.lower()
        if isinstance(exc, asyncio.TimeoutError) or "timeout" in name:
            return SVOTimeoutError(str(exc), timeout_value=self.timeout)
        response = getattr(exc, "response", None)
        status = getattr(response, "status_code", None) if response else None
        if status:
            response_text = getattr(response, "text", "") or ""
            return SVOHTTPError(
                status_code=status,
                message=str(exc),
                response_text=str(response_text),
            )
        if isinstance(exc, RuntimeError):
            return SVOJSONRPCError(code=-32603, message=str(exc))
        return SVOConnectionError(f"Connection error: {exc}", exc)

    @staticmethod
    def parse_chunk_static(chunk: Any) -> "SemanticChunk":
        from chunk_metadata_adapter import ChunkMetadataBuilder, SemanticChunk

        if isinstance(chunk, SemanticChunk):
            return chunk
        try:
            builder = ChunkMetadataBuilder()
            return builder.json_dict_to_semantic(chunk)
        except Exception as exc:  # noqa: BLE001
            raise ValueError(
                "Failed to deserialize chunk using chunk_metadata_adapter: "
                f"{exc}\nChunk: {chunk}"
            ) from exc

    @staticmethod
    def _extract_job_id(payload: Dict[str, Any]) -> Optional[str]:
        if not isinstance(payload, dict):
            return None
        for key in ("job_id", "jobId"):
            value = payload.get(key)
            if isinstance(value, str):
                return value
        nested = payload.get("result")
        if isinstance(nested, dict):
            return ChunkerClient._extract_job_id(nested)
        return None

    @staticmethod
    def _unwrap_result(payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            raise SVOServerError(
                code="invalid_result", message="Unexpected response type"
            )

        result = payload.get("result", payload)
        if (
            isinstance(result, dict)
            and "result" in result
            and isinstance(result["result"], dict)
        ):
            result = result["result"]

        if not isinstance(result, dict):
            raise SVOServerError(
                code="invalid_result",
                message="Result is not a dict",
            )

        return result

    @staticmethod
    def _extract_chunks_or_raise(
        result: Dict[str, Any],
    ) -> List["SemanticChunk"]:
        if result.get("success") is False:
            error = result.get("error", {}) or {}
            raise SVOServerError(
                code=error.get("code", "server_error"),
                message=error.get(
                    "message",
                    "Server returned success=false",
                ),
                chunk_error=error,
            )

        chunks = result.get("chunks")
        if not isinstance(chunks, list):
            raise SVOServerError(
                code="empty_result",
                message="Empty or invalid result from server",
            )

        parsed_chunks: List["SemanticChunk"] = []
        for chunk in chunks:
            if isinstance(chunk, dict) and "error" in chunk:
                err = chunk["error"]
                raise SVOServerError(
                    code=err.get("code", "unknown"),
                    message=err.get("message", str(err)),
                    chunk_error=err,
                )
            parsed_chunks.append(ChunkerClient.parse_chunk_static(chunk))
        return parsed_chunks

    async def get_openapi_schema(self) -> Dict[str, Any]:
        """Fetch OpenAPI schema using adapter transport."""
        try:
            return await self._client.get_openapi_schema()
        except Exception as exc:  # noqa: BLE001
            mapped = self._map_exception(exc)
            raise mapped from exc

    async def submit_chunk_job(self, text: str, **params: Any) -> str:
        try:
            result = await self._client.execute_command_unified(
                "chunk",
                {"text": text, **params},
                expect_queue=True,
                auto_poll=False,
            )
        except Exception as exc:  # noqa: BLE001
            raise self._map_exception(exc) from exc

        job_id = self._extract_job_id(result)
        if not job_id:
            raise SVOServerError(
                code="no_job_id", message="Chunk command did not return job_id"
            )
        return job_id

    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Fetch job status via adapter."""
        try:
            return await self._client.queue_get_job_status(job_id)
        except Exception as exc:  # noqa: BLE001
            raise self._map_exception(exc) from exc

    async def get_job_logs(self, job_id: str) -> Dict[str, Any]:
        """Fetch job logs via adapter queue API."""
        try:
            return await self._client.queue_get_job_logs(job_id)
        except Exception as exc:  # noqa: BLE001
            raise self._map_exception(exc) from exc

    async def wait_for_result(
        self,
        job_id: str,
        *,
        poll_interval: Optional[float] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        interval = poll_interval or self.poll_interval
        deadline = time.monotonic() + timeout if timeout else None
        pending = {"queued", "pending", "running", "processing", "started"}

        while True:
            try:
                status = await self._client.queue_get_job_status(job_id)
            except Exception as exc:  # noqa: BLE001
                raise self._map_exception(exc) from exc

            if isinstance(status, dict):
                data = status.get("data", status)
            else:
                data = {}
            status_raw = data.get("status") or data.get("state") or ""
            status_value = str(status_raw).lower()
            if not status_value and isinstance(status, dict):
                status_value = str(status.get("status") or "").lower()

            if status_value in pending:
                if deadline and time.monotonic() >= deadline:
                    message = (
                        f"Job {job_id} did not finish in {timeout} seconds"
                    )
                    raise SVOTimeoutError(message, timeout)
                await asyncio.sleep(interval)
                continue

            # Final state
            if isinstance(data, dict) and data.get("success") is False:
                error = data.get("error", {}) or {}
                raise SVOServerError(
                    code=error.get("code", "job_failed"),
                    message=error.get("message", "Queued job failed"),
                    chunk_error=error,
                )

            return self._unwrap_result(data)

    async def chunk_text(
        self,
        text: str,
        **params: Any,
    ) -> List["SemanticChunk"]:
        try:
            unified = await self._client.execute_command_unified(
                "chunk",
                {"text": text, **params},
                expect_queue=True,
                auto_poll=True,
                poll_interval=self.poll_interval,
                timeout=self.timeout,
            )
        except Exception as exc:  # noqa: BLE001
            raise self._map_exception(exc) from exc

        result = self._unwrap_result(unified)
        return self._extract_chunks_or_raise(result)

    async def get_help(self, cmdname: Optional[str] = None) -> Dict[str, Any]:
        """Get help info from chunker via JSON-RPC."""
        params = {"cmdname": cmdname} if cmdname else {}
        try:
            return await self._client.execute_command(
                "help", params, use_cmd_endpoint=False
            )
        except Exception as exc:  # noqa: BLE001
            raise self._map_exception(exc) from exc

    async def health(self) -> Dict[str, Any]:
        """Health check via JSON-RPC."""
        try:
            return await self._client.execute_command(
                "health", None, use_cmd_endpoint=False
            )
        except Exception as exc:  # noqa: BLE001
            raise self._map_exception(exc) from exc

    def reconstruct_text(self, chunks: List["SemanticChunk"]) -> str:
        """Reconstruct original text from SemanticChunk list."""
        sorted_chunks = sorted(
            chunks,
            key=lambda c: (
                c.ordinal
                if getattr(c, "ordinal", None) is not None
                else chunks.index(c)
            ),
        )
        return "".join(
            chunk.text
            for chunk in sorted_chunks
            if getattr(chunk, "text", None)
        )

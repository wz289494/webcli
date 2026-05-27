"""浏览器桥接服务。

CLI 每次执行命令时会短连接到这里，浏览器扩展则保持长连接。
这个模块负责在两者之间转发命令，并通过命令 id 关联请求与响应。
"""

from __future__ import annotations

import asyncio
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from websockets.asyncio.server import ServerConnection, serve

from protocol import Command, Result


@dataclass(slots=True)
class ExtensionPeer:
    """当前连接到桥接服务的浏览器扩展实例。"""

    websocket: ServerConnection
    hello: dict[str, Any] = field(default_factory=dict)


class BridgeServer:
    """在 CLI 与扩展之间做内存级别的请求转发。"""

    def __init__(self) -> None:
        self.extension: ExtensionPeer | None = None
        self.pending: dict[str, asyncio.Future[Result]] = {}
        self.record_root = Path(__file__).resolve().parents[2] / "record"

    async def serve_forever(self, host: str, port: int) -> None:
        """启动桥接服务并持续监听。"""
        async with serve(self._handle, host, port):
            print(f"WebCLI 桥接服务已启动: ws://{host}:{port}")
            await asyncio.Future()

    def _debug_result(self, request_id: str, stage: str, err: Exception) -> dict[str, Any]:
        """生成调试期错误结果，避免未捕获异常直接打断 websocket。"""
        return {
            "type": "result",
            "result": {
                "id": request_id,
                "ok": False,
                "error": f"{type(err).__name__}: {err}",
                "errorCode": f"bridge_debug_{stage}",
                "errorHint": "bridge 调试插桩已捕获异常，请根据 errorCode 和 error 定位阶段。",
            },
        }

    def _sanitize_record_name(self, value: str) -> str:
        """把 session 或动作名规整成安全的目录/文件片段。"""
        cleaned = re.sub(r"[^\w.-]+", "_", value.strip(), flags=re.UNICODE).strip("._")
        return cleaned or "default"

    def _record_session_name(self, command: Command) -> str:
        """读取记录目录使用的 session 名称。"""
        session = (command.session or "").strip()
        return session or "default"

    def _write_record(self, command: Command, result: Result, envelope: dict[str, Any]) -> None:
        """把一次命令及其结果写入 record/session/*.md。"""
        session_name = self._record_session_name(command)
        session_dir = self.record_root / self._sanitize_record_name(session_name)
        session_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        action_name = self._sanitize_record_name(command.action)
        file_path = session_dir / f"{timestamp}-{action_name}-{command.id}.md"

        content = "\n".join([
            "# WebCLI Record",
            "",
            f"- 记录时间: {datetime.now().isoformat(timespec='seconds')}",
            f"- Session: {session_name}",
            f"- Action: {command.action}",
            f"- Command ID: {command.id}",
            f"- 成功: {'是' if result.ok else '否'}",
            "",
            "## 问题/命令",
            "",
            "```json",
            json.dumps(envelope, ensure_ascii=False, indent=2),
            "```",
            "",
            "## 结果/返回",
            "",
            "```json",
            json.dumps(asdict(result), ensure_ascii=False, indent=2),
            "```",
            "",
        ])
        file_path.write_text(content, encoding="utf-8")

    def _record_command_result(self, command: Command, result: Result, envelope: dict[str, Any]) -> None:
        """记录失败不影响主流程，避免因为写文件导致桥接命令失败。"""
        try:
            self._write_record(command, result, envelope)
        except Exception as err:
            print(f"[webcli] 写入 record 失败: {type(err).__name__}: {err}")

    async def _handle(self, websocket: ServerConnection) -> None:
        """根据第一条消息判断是扩展接入还是 CLI 调用。"""
        try:
            first_raw = await websocket.recv()
            if isinstance(first_raw, bytes):
                first_raw = first_raw.decode("utf-8")
            first = json.loads(first_raw)

            if first.get("type") == "hello":
                await self._handle_extension(websocket, first)
                return

            if first.get("type") == "command":
                await self._handle_cli_command(websocket, first)
                return

            await websocket.send(json.dumps({
                "type": "result",
                "result": {
                    "id": "invalid",
                    "ok": False,
                    "error": "Unsupported initial message. Expected hello or command.",
                    "errorCode": "invalid_message",
                },
            }, ensure_ascii=False))
        except Exception as err:
            await websocket.send(json.dumps(self._debug_result("invalid", "entry", err), ensure_ascii=False))

    async def _handle_extension(self, websocket: ServerConnection, hello: dict[str, Any]) -> None:
        """注册扩展连接，并把它后续返回的数据分发给等待中的命令。"""
        self.extension = ExtensionPeer(websocket=websocket, hello=hello)
        try:
            async for raw in websocket:
                if isinstance(raw, bytes):
                    raw = raw.decode("utf-8")
                payload = json.loads(raw)
                result = Result.from_payload(payload)
                future = self.pending.get(result.id)
                if future and not future.done():
                    future.set_result(result)
        except Exception as err:
            for request_id, future in list(self.pending.items()):
                if not future.done():
                    future.set_result(Result(
                        id=request_id,
                        ok=False,
                        error=f"{type(err).__name__}: {err}",
                        errorCode="bridge_debug_extension",
                        errorHint="扩展回包通道出现异常，请检查扩展 background console。",
                    ))
        finally:
            if self.extension and self.extension.websocket is websocket:
                self.extension = None

    async def _handle_cli_command(self, websocket: ServerConnection, envelope: dict[str, Any]) -> None:
        """转发一条 CLI 命令到扩展，并把结果回写给当前调用方。"""
        command_payload = envelope.get("command") or {}
        command = Command(**command_payload)
        result: Result

        if self.extension is None:
            result = Result(
                id=command.id,
                ok=False,
                error="No extension connected to bridge server",
                errorCode="extension_offline",
                errorHint="启动浏览器扩展并连接到当前桥接服务。",
            )
            self._record_command_result(command, result, envelope)
            await websocket.send(json.dumps({"type": "result", "result": asdict(result)}, ensure_ascii=False))
            return

        # 用 future 暂存等待中的命令，等扩展回包时再根据 id 唤醒。
        future: asyncio.Future[Result] = asyncio.get_running_loop().create_future()
        self.pending[command.id] = future
        try:
            await self.extension.websocket.send(json.dumps(command.to_payload(), ensure_ascii=False))
            result = await asyncio.wait_for(future, timeout=float(envelope.get("timeout", 30.0)))
        except TimeoutError:
            result = Result(
                id=command.id,
                ok=False,
                error="Timed out waiting for extension result",
                errorCode="timeout",
            )
        except Exception as err:
            result = Result.from_payload(self._debug_result(command.id, "cli_command", err)["result"])
        finally:
            self.pending.pop(command.id, None)

        self._record_command_result(command, result, envelope)
        await websocket.send(json.dumps({"type": "result", "result": asdict(result)}, ensure_ascii=False))

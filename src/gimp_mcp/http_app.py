"""
ASGI app for uvicorn (webapp/start.ps1).

Uses: uvicorn gimp_mcp.http_app:app --host 127.0.0.1 --port <BackendPort>

Registers FastMCP 3.2 surface (prompts, resources, skills, prefab) via
:class:`~gimp_mcp.server.GimpMcpServer`, then exposes custom /api/* routes.
"""

from __future__ import annotations

from pathlib import Path

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from .config import GimpConfig
from .server import GimpMcpServer
from .sota_registration import get_sota_feature_manifest

try:
    from .ai_image import get_available_providers, get_settings_status, update_settings
    _AI_AVAILABLE = True
except ImportError:
    _AI_AVAILABLE = False

try:
    from .local_llm import detect as _llm_detect, chat as _llm_chat, update_settings as _llm_update_settings, understand_image, suggest_gimp_ops
    _LLM_AVAILABLE = True
except ImportError:
    _LLM_AVAILABLE = False

_config = GimpConfig()
_mcp = FastMCP(
    name="gimp-mcp",
    version="4.0.0",
    instructions=(
        "GIMP MCP — FastMCP 3.2 SOTA. Portmanteau tools + sampling + prompts + resources + "
        "skill://gimp-expert/SKILL.md. Prefer allowed_directories-safe paths."
    ),
    strict_input_validation=True,
    mask_error_details=True,
    client_log_level="info",
)
_gimp_server = GimpMcpServer(_config)
_gimp_server.register_tools(_mcp)

_SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"


@_mcp.custom_route("/api/health", methods=["GET"])
async def _api_health(_request: Request) -> Response:
    return JSONResponse(
        {
            "status": "healthy",
            "server_name": "gimp-mcp",
            "version": "4.0.0",
            "fastmcp": "3.2",
            "sota": get_sota_feature_manifest(),
            "stack": "GimpMcpServer (plugin tools); use `gimp-mcp` CLI for portmanteau + agentic",
        }
    )


@_mcp.custom_route("/api/status", methods=["GET"])
async def _api_status(request: Request) -> Response:
    return await _api_health(request)


@_mcp.custom_route("/api/sota", methods=["GET"])
async def _api_sota(_request: Request) -> Response:
    return JSONResponse(get_sota_feature_manifest())


@_mcp.custom_route("/api/skills", methods=["GET"])
async def _api_skills_list(_request: Request) -> Response:
    skills = []
    if _SKILLS_DIR.is_dir():
        for skill_dir in _SKILLS_DIR.iterdir():
            if skill_dir.is_dir():
                skill_md = skill_dir / "SKILL.md"
                skills.append({
                    "name": skill_dir.name,
                    "uri": f"skill://{skill_dir.name}/SKILL.md",
                    "has_content": skill_md.is_file(),
                })
    return JSONResponse({"skills": skills})


@_mcp.custom_route("/api/skills/{skill_name:str}", methods=["GET"])
async def _api_skill_content(request: Request) -> Response:
    skill_name = request.path_params["skill_name"]
    skill_md = _SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_md.is_file():
        return Response(status_code=404)
    content = skill_md.read_text(encoding="utf-8")
    return JSONResponse({
        "name": skill_name,
        "uri": f"skill://{skill_name}/SKILL.md",
        "content": content,
    })


@_mcp.custom_route("/api/tools", methods=["GET"])
async def _api_tools_list(_request: Request) -> Response:
    tools = []
    exec_layer = _gimp_server.interaction_manager or _gimp_server.cli_wrapper
    if hasattr(exec_layer, "list_operations"):
        tools = await exec_layer.list_operations() if callable(exec_layer.list_operations) else exec_layer.list_operations
    return JSONResponse({"tools": tools if isinstance(tools, list) else [], "count": len(tools) if isinstance(tools, list) else 0})


@_mcp.custom_route("/api/settings", methods=["GET"])
async def _api_settings_get(_request: Request) -> Response:
    if not _AI_AVAILABLE:
        return JSONResponse({"providers": {}, "available": False})
    return JSONResponse({
        "providers": get_settings_status(),
        "available": get_available_providers(),
    })


@_mcp.custom_route("/api/settings", methods=["POST"])
async def _api_settings_set(request: Request) -> Response:
    body = await request.json()
    provider = body.get("provider")
    api_key = body.get("api_key")
    scope = body.get("scope", "ai")

    if scope == "local_llm":
        if not _LLM_AVAILABLE:
            return JSONResponse({"error": "Local LLM module not available"}, status_code=500)
        _llm_update_settings(provider or "disabled", body.get("model", ""))
        detect_result = await _llm_detect()
        return JSONResponse({"success": True, "local_llm": {"provider": provider, "model": body.get("model", "")}, "detected": detect_result})

    if not _AI_AVAILABLE:
        return JSONResponse({"error": "AI module not available"}, status_code=500)
    if not provider or not api_key:
        return JSONResponse({"error": "provider and api_key required"}, status_code=400)
    update_settings(provider, api_key)
    return JSONResponse({"success": True, "providers": get_settings_status(), "available": get_available_providers()})


@_mcp.custom_route("/api/llm/detect", methods=["GET"])
async def _api_llm_detect(_request: Request) -> Response:
    if not _LLM_AVAILABLE:
        return JSONResponse({"error": "Local LLM module not available"}, status_code=500)
    result = await _llm_detect()
    return JSONResponse(result)


@_mcp.custom_route("/api/llm/chat", methods=["POST"])
async def _api_llm_chat(request: Request) -> Response:
    if not _LLM_AVAILABLE:
        return JSONResponse({"error": "Local LLM module not available"}, status_code=500)
    body = await request.json()
    messages = body.get("messages", [])
    image_path = body.get("image_path")
    provider = body.get("provider")
    model = body.get("model")
    result = await _llm_chat(messages, image_path=image_path, provider=provider, model=model)
    return JSONResponse({"reply": result})


@_mcp.custom_route("/api/llm/understand", methods=["POST"])
async def _api_llm_understand(request: Request) -> Response:
    if not _LLM_AVAILABLE:
        return JSONResponse({"error": "Local LLM module not available"}, status_code=500)
    body = await request.json()
    image_path = body.get("image_path", "")
    instruction = body.get("instruction", "Describe this image in detail.")
    result = await understand_image(image_path, instruction)
    return JSONResponse({"description": result})


@_mcp.custom_route("/api/llm/suggest", methods=["POST"])
async def _api_llm_suggest(request: Request) -> Response:
    if not _LLM_AVAILABLE:
        return JSONResponse({"error": "Local LLM module not available"}, status_code=500)
    body = await request.json()
    image_path = body.get("image_path", "")
    request_text = body.get("request", "")
    ops = await suggest_gimp_ops(image_path, request_text)
    return JSONResponse({"operations": ops})


@_mcp.custom_route("/api/generate", methods=["POST"])
async def _api_generate(request: Request) -> Response:
    if not _AI_AVAILABLE:
        return JSONResponse({"error": "AI module not available", "success": False}, status_code=500)
    from .ai_image import generate as ai_generate
    body = await request.json()
    provider = body.get("provider", "gemini")
    prompt = body.get("prompt", "")
    if not prompt:
        return JSONResponse({"success": False, "error": "prompt is required"})
    result = await ai_generate(
        provider=provider,
        prompt=prompt,
        width=body.get("width", 1024),
        height=body.get("height", 1024),
        quality=body.get("quality", "standard"),
        style=body.get("style", "photorealistic"),
    )
    return JSONResponse(result)


app = _mcp.http_app()

# SPDX-License-Identifier: MIT
"""Domain helpers for initialization operations."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from fenix_mcp.infrastructure.fenix_api.client import FenixApiClient


@dataclass(slots=True)
class InitializationData:
    profile: Optional[Dict[str, Any]]
    core_documents: List[Dict[str, Any]]
    user_documents: List[Dict[str, Any]]
    recent_memories: List[Dict[str, Any]]


class InitializationService:
    """Fetch and format initialization data from the Fênix API."""

    def __init__(self, api_client: FenixApiClient, logger):
        self._api = api_client
        self._logger = logger

    async def gather_data(
        self, *, include_user_docs: bool, limit: int
    ) -> InitializationData:
        profile = await self._safe_call(self._api.get_profile)
        core_docs = await self._safe_call(
            self._api.list_core_documents,
            return_content=True,
        )
        if self._logger:
            self._logger.debug("Core docs response", extra={"core_docs": core_docs})
        user_docs: List[Dict[str, Any]] = []
        if include_user_docs:
            user_docs = (
                await self._safe_call(
                    self._api.list_user_core_documents,
                    return_content=True,
                )
                or []
            )
            if self._logger:
                self._logger.debug("User docs response", extra={"user_docs": user_docs})
        return InitializationData(
            profile=profile,
            core_documents=self._extract_items(core_docs, "coreDocuments"),
            user_documents=self._extract_items(user_docs, "userCoreDocuments"),
            recent_memories=[],
        )

    async def _safe_call(self, func, *args, **kwargs):
        try:
            return await asyncio.to_thread(func, *args, **kwargs)
        except Exception as exc:  # pragma: no cover - defensive logging path
            self._logger.warning("Initialization API call failed: %s", exc)
            return None

    @staticmethod
    def _extract_items(payload: Any, key: str) -> List[Dict[str, Any]]:
        if payload is None:
            return []
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            value = payload.get(key) or payload.get("data")
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        return []

    @staticmethod
    def build_existing_user_summary(
        data: InitializationData, include_user_docs: bool
    ) -> str:
        profile = data.profile or {}
        user_info = profile.get("user") or {}
        tenant_info = profile.get("tenant") or {}
        core_count = len(data.core_documents)
        user_count = len(data.user_documents)
        memories_count = len(data.recent_memories)

        lines = [
            "✅ **Fênix Cloud inicializado com sucesso!**",
        ]

        if user_info:
            lines.append(
                f"- Usuário: {user_info.get('name') or 'Desconhecido'} "
                f"(ID: {user_info.get('id', 'N/A')})"
            )
        if tenant_info:
            lines.append(f"- Organização: {tenant_info.get('name', 'N/A')}")

        lines.append(f"- Documentos principais carregados: {core_count}")

        if include_user_docs:
            lines.append(f"- Documentos pessoais carregados: {user_count}")

        lines.append(f"- Memórias recentes disponíveis: {memories_count}")

        if core_count:
            preview = ", ".join(
                doc.get("name", doc.get("title", "sem título"))
                for doc in data.core_documents[:5]
            )
            lines.append(f"- Exemplos de documentos principais: {preview}")

        if include_user_docs and user_count:
            preview = ", ".join(
                doc.get("name", "sem título") for doc in data.user_documents[:5]
            )
            lines.append(f"- Exemplos de documentos pessoais: {preview}")

        if memories_count:
            preview = ", ".join(
                mem.get("title", "sem título") for mem in data.recent_memories[:3]
            )
            lines.append(f"- Memórias recentes: {preview}")

        lines.append("")
        lines.append(
            "Agora você pode usar as ferramentas de produtividade, conhecimento e inteligência para continuar."
        )
        return "\n".join(lines)

    @staticmethod
    def build_new_user_prompt(data: InitializationData) -> str:
        profile = data.profile or {}
        user_name = (profile.get("user") or {}).get("name") or "Bem-vindo(a)"

        questions = [
            "Qual é o foco principal do seu trabalho atualmente?",
            "Quais são seus objetivos para as próximas semanas?",
            "Existem tarefas ou projetos que gostaria de priorizar?",
            "Como você prefere organizar suas rotinas ou checklists?",
            "Quais são os principais blocos de conhecimento que precisa acessar rapidamente?",
            "Há regras ou procedimentos que precisam ser seguidos com frequência?",
            "Que tipo de memória ou registro você consulta com frequência?",
            "Quais ferramentas ou integrações externas são essenciais no seu dia a dia?",
            "O que significaria sucesso para você utilizando o Fênix?",
        ]

        body = [
            f"👋 **{user_name}, bem-vindo(a) ao Fênix Cloud!**",
            "",
            "Notamos que você ainda não tem documentos pessoais configurados. "
            "Vamos criar uma experiência personalizada para você.",
            "",
            "Responda às perguntas abaixo para que possamos preparar modos, regras e documentos alinhados às suas necessidades:",
            "",
        ]

        body.extend(f"{idx + 1}. {question}" for idx, question in enumerate(questions))
        body.extend(
            [
                "",
                "Envie as respostas no formato:",
                "```",
                'initialize action=setup answers=["resposta 1", "resposta 2", ..., "resposta 9"]',
                "```",
                "",
                "Com base nisso, sugerirei documentos, regras e rotinas para você utilizar.",
            ]
        )

        return "\n".join(body)

    @staticmethod
    def validate_setup_answers(answers: List[str]) -> Optional[str]:
        if not answers:
            return "Envie uma lista com 9 respostas para processarmos o setup."
        if len(answers) != 9:
            return f"Esperado receber 9 respostas, mas recebi {len(answers)}."
        if not all(isinstance(answer, str) and answer.strip() for answer in answers):
            return "Todas as respostas devem ser textos preenchidos."
        return None

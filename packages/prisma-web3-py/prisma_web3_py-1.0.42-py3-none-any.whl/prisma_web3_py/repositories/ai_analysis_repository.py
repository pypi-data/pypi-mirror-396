"""
AI Analysis Repository - Unified repository for all AI analysis results.

中文说明：
该仓储作为 AIAnalysisResult 的唯一写入口，负责从各 Agent 的 analysis_state
提取规范字段（LLM 主观 recommendation + 客观 impact/filter 决策），并持久化到数据库。
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from sqlalchemy import select, and_, func, text, cast, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import JSONB
import logging
from prisma_web3_py.utils.datetime import utc_now_naive

from ..models.ai_analysis_result import AIAnalysisResult
from .base_repository import BaseRepository

logger = logging.getLogger(__name__)


@dataclass
class AnalysisFields:
    """Normalized AI analysis payload used by News/Twitter storage."""

    summary: Optional[str] = None
    sentiment: Optional[str] = None
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    key_points: List[str] = field(default_factory=list)
    importance_score: Optional[float] = None
    decision_score: Optional[float] = None
    market_impact_label: Optional[str] = None
    market_impact_score: Optional[float] = None
    event_type: Optional[str] = None


def _safe_float(value: Any) -> Optional[float]:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _safe_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [
            str(item).strip()
            for item in value
            if isinstance(item, (str, int, float)) and str(item).strip()
        ]
    if isinstance(value, str):
        return [part.strip() for part in value.splitlines() if part.strip()]
    return []


def _extract_decision_score(state: Dict[str, Any]) -> Optional[float]:
    """
    从 agent 的 analysis_state 中提取统一的决策分数（combined_score）。

    decision_score 用于对齐线上过滤/推送口径，优先读取：
    - state.filter_context.combined_score
    - state.final_signal.filter_context.combined_score

    Args:
        state: News/Twitter/OI 等 Agent 的输出状态。

    Returns:
        0–1 区间的决策分数；缺失时返回 None。
    """
    raw_ctx = state.get("filter_context") or {}
    if isinstance(raw_ctx, dict):
        val = raw_ctx.get("combined_score") or raw_ctx.get("decision_score")
    else:
        val = None

    if val is None:
        final_signal = state.get("final_signal") or {}
        if isinstance(final_signal, dict):
            fs_ctx = final_signal.get("filter_context") or {}
            if isinstance(fs_ctx, dict):
                val = fs_ctx.get("combined_score") or fs_ctx.get("decision_score")

    return _safe_float(val)


def _normalize_analysis_payload(payload: Optional[Dict[str, Any]]) -> AnalysisFields:
    """
    Normalize any inbound dict (e.g., from the Twitter handler) into AnalysisFields.
    """
    payload = payload or {}
    key_points = (
        payload.get("key_points")
        or payload.get("key_catalysts")
        or []
    )
    importance_score = _safe_float(payload.get("importance_score"))
    decision_score = _safe_float(payload.get("decision_score") or payload.get("combined_score"))
    return AnalysisFields(
        summary=payload.get("summary"),
        sentiment=payload.get("sentiment"),
        confidence=_safe_float(payload.get("confidence")),
        reasoning=payload.get("reasoning") or payload.get("reason"),
        key_points=_safe_list(key_points),
        importance_score=importance_score,
        decision_score=decision_score,
        market_impact_label=payload.get("market_impact") or payload.get("market_impact_label"),
        market_impact_score=_safe_float(payload.get("market_impact_score")),
        event_type=payload.get("event_type"),
    )


def _extract_analysis_from_state(state: Dict[str, Any]) -> AnalysisFields:
    """
    Build AnalysisFields directly from a News/Twitter agent state.
    Prefers trading_recommendation outputs and only falls back to legacy fields.
    """
    trading_rec = state.get("trading_recommendation") or {}
    event_factors = state.get("event_factors") or {}
    legacy_analysis = state.get("analysis") or {}
    final_signal = state.get("final_signal") or {}

    summary = (
        trading_rec.get("summary")
        or event_factors.get("summary")
        or legacy_analysis.get("summary")
    )

    sentiment = (
        trading_rec.get("sentiment")
        or event_factors.get("sentiment")
        or legacy_analysis.get("sentiment")
    )

    confidence = (
        _safe_float(trading_rec.get("confidence"))
        or _safe_float(legacy_analysis.get("confidence"))
    )

    key_points = (
        trading_rec.get("key_catalysts")
        or legacy_analysis.get("key_points")
        or event_factors.get("key_points")
        or []
    )

    reasoning = (
        trading_rec.get("reasoning")
        or final_signal.get("reasoning")
        or legacy_analysis.get("reasoning")
        or state.get("macro_reason")
    )

    importance_score = _safe_float(trading_rec.get("importance_score"))
    decision_score = _extract_decision_score(state)
    market_impact_label = (
        trading_rec.get("market_impact")
        or event_factors.get("market_impact")
        or state.get("market_impact")
    )
    market_impact_score = (
        _safe_float(trading_rec.get("market_impact_score"))
        or _safe_float(final_signal.get("market_impact_score"))
        or _safe_float(state.get("market_impact_score"))
    )

    return AnalysisFields(
        summary=summary,
        sentiment=sentiment,
        confidence=confidence,
        reasoning=reasoning,
        key_points=_safe_list(key_points),
        importance_score=importance_score,
        decision_score=decision_score,
        market_impact_label=market_impact_label,
        market_impact_score=market_impact_score,
        event_type=event_factors.get("event_type") or state.get("event_type"),
    )


def _extract_duplicate_meta(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    提取重复打标与 coverage 聚合字段，兼容 analysis_state 包装。
    """
    payload = payload or {}
    state = payload.get("analysis_state") or payload
    return {
        "duplicate_type": state.get("duplicate_type"),
        "canonical_event_id": state.get("canonical_event_id"),
        "coverage_count": state.get("coverage_count"),
        "coverage_sources": state.get("coverage_sources"),
    }


def _canonical_id_to_str(value: Any) -> Optional[str]:
    """
    将 canonical_event_id 统一转换为字符串，避免写库时类型不一致。

    Args:
        value: 可能为 str/int/None 的 canonical_event_id 值。

    Returns:
        转换后的字符串或 None。
    """
    if value is None:
        return None
    try:
        return str(value)
    except Exception:
        return None


def _normalize_tokens_payload(raw: Optional[List[Any]]) -> Optional[List[Dict[str, Any]]]:
    """
    Normalize heterogeneous token representations (dicts, Pydantic models, dataclasses).
    """
    if not raw:
        return None
    normalized: List[Dict[str, Any]] = []
    for token in raw:
        data: Optional[Dict[str, Any]] = None
        if isinstance(token, dict):
            data = token
        elif hasattr(token, "model_dump"):
            try:
                data = token.model_dump()
            except Exception:
                data = None
        if data is None:
            symbol = getattr(token, "symbol", None) or getattr(token, "canonical_symbol", None)
            if not symbol:
                continue
            metadata = getattr(token, "metadata", None)
            if hasattr(metadata, "model_dump"):
                try:
                    metadata = metadata.model_dump()
                except Exception:
                    metadata = None
            data = {
                "symbol": symbol,
                "name": getattr(token, "name", None),
                "chain": getattr(token, "chain", None),
                "coingecko_id": getattr(token, "coingecko_id", None),
                "token_address": getattr(token, "token_address", None),
                "source": getattr(token, "source", None),
                "linked": getattr(token, "linked", None),
                "confidence": getattr(token, "confidence", None),
                "match_type": getattr(token, "match_type", None),
                "metadata": metadata,
            }
        sym = data.get("symbol") or data.get("canonical_symbol")
        if not sym:
            continue
        normalized.append(
            {
                "symbol": str(sym).upper(),
                "name": data.get("name"),
                "chain": data.get("chain"),
                "coingecko_id": data.get("coingecko_id"),
                "token_address": data.get("token_address"),
                "source": data.get("source") or "unknown",
                "linked": bool(data.get("linked", False)),
                "confidence": data.get("confidence"),
                "match_type": data.get("match_type"),
                "metadata": data.get("metadata") or {},
            }
        )
    return normalized or None


def _extract_event_enrichment(analysis_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract structured event/thread enrichment fields from agent state.
    """
    event_struct = analysis_state.get("event_struct") or {}
    event_key = analysis_state.get("event_key")
    thread_id = analysis_state.get("thread_id")
    event_factors = analysis_state.get("event_factors") or {}
    scenario = event_factors.get("scenario") or event_struct.get("scenario")
    actor = event_factors.get("actor") or (event_struct.get("actor") or {}).get("name") if isinstance(event_struct, dict) else None
    actor_type = event_factors.get("actor_type") or (event_struct.get("actor") or {}).get("role") if isinstance(event_struct, dict) else None
    action_type = event_factors.get("action_type") or (event_struct.get("action") or {}).get("type") if isinstance(event_struct, dict) else None

    magnitude_value = None
    magnitude_unit = None
    if isinstance(event_struct, dict):
        action = event_struct.get("action") or {}
        magnitude = action.get("magnitude") or {}
        magnitude_value = magnitude.get("value")
        magnitude_unit = magnitude.get("unit")

    return {
        "event_struct": event_struct or None,
        "event_key": event_key,
        "thread_id": thread_id,
        "scenario": scenario,
        "actor": actor,
        "actor_type": actor_type,
        "action_type": action_type,
        "magnitude_value": magnitude_value,
        "magnitude_unit": magnitude_unit,
    }


class AIAnalysisRepository(BaseRepository[AIAnalysisResult]):
    """
    AI Analysis Result Repository

    Provides unified interface for querying, creating, and updating AI analysis results
    from all sources (Twitter, News, Telegram, etc.)
    """

    def __init__(self):
        super().__init__(AIAnalysisResult)

    # ========== CREATE METHODS ==========

    async def increment_coverage(
        self,
        session: AsyncSession,
        canonical_event_id: str,
        source: Optional[str],
        source_type: str = "news",
        source_id: Optional[str] = None,
        source_link: Optional[str] = None,
    ) -> bool:
        """
        Increment coverage sources for a canonical event (cross-source unique).

        语义调整（2025-12）：coverage_count 表示「跨源唯一来源数」，
        仅在发现新的来源条目时递增/重算；同源重复不会增加 coverage。

        兼容旧数据：coverage_sources 既可能是字符串列表，也可能包含带有
        ``source/source_id/source_link`` 等字段的字典。此方法会把历史数据规整为
        统一的字典列表并去重。

        Args:
            session: Async database session.
            canonical_event_id: Canonical event identifier used for coverage aggregation.
            source: Human-readable source label (e.g., news source name or Twitter handle).
            source_type: Source type, such as ``\"news\"`` 或 ``\"twitter\"``。
            source_id: 可选的底层来源 ID（如 CryptoNews ID、tweet_id）。
            source_link: 可选的原文链接 URL。

        Returns:
            True if an existing record was updated, False if no matching row was found.
        """

        def _normalize_entry(item: Any) -> Dict[str, Any]:
            """将 coverage_sources 元素规整为字典，兼容字符串与旧格式。

            Args:
                item: 原始 coverage_sources 元素。

            Returns:
                统一包含 ``source/source_id/source_link`` 键的字典（缺失字段可为空）。
            """

            if isinstance(item, dict):
                return {
                    "source": item.get("source") or item.get("label"),
                    "source_id": item.get("source_id"),
                    "source_type": item.get("source_type"),
                    "source_link": item.get("source_link") or item.get("url"),
                }
            # 旧数据：直接用字符串作为来源名
            return {
                "source": str(item),
                "source_id": None,
                "source_type": None,
                "source_link": None,
            }

        def _equals(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
            """判定两个 coverage 条目是否视为同一来源。

            优先比较 source_id，其次比较 (source, source_link)。
            """

            if a.get("source_id") and b.get("source_id"):
                return str(a["source_id"]) == str(b["source_id"])
            if a.get("source") and b.get("source"):
                if a.get("source_link") and b.get("source_link"):
                    return (
                        str(a["source"]) == str(b["source"])
                        and str(a["source_link"]) == str(b["source_link"])
                    )
                return str(a["source"]) == str(b["source"])
            return False

        try:
            stmt = (
                select(AIAnalysisResult)
                .where(
                    AIAnalysisResult.canonical_event_id == canonical_event_id,
                    AIAnalysisResult.source_type == source_type,
                )
                .limit(1)
            )
            result = await session.execute(stmt)
            record = result.scalar_one_or_none()
            if record is None:
                return False

            current_count = int(record.coverage_count or 0)

            existing_raw = record.coverage_sources or []
            merged: list[Dict[str, Any]] = []
            for item in existing_raw:
                try:
                    norm = _normalize_entry(item)
                except Exception:
                    # 保底：无法解析时直接跳过该元素
                    continue
                # 去重：避免同一来源被重复写入
                if not any(_equals(norm, old) for old in merged):
                    merged.append(norm)

            # 构造新的 coverage 条目
            new_entry: Optional[Dict[str, Any]] = None
            if source or source_id or source_link:
                new_entry = {
                    "source": source,
                    "source_id": str(source_id) if source_id is not None else None,
                    "source_type": source_type,
                    "source_link": source_link,
                }

            if new_entry is not None and not any(_equals(new_entry, old) for old in merged):
                merged.append(new_entry)

            # coverage_count 代表唯一来源数量；merged 为空时回退为旧值。
            if merged:
                record.coverage_count = len(merged)
            else:
                record.coverage_count = current_count

            # 最终写回统一为字典列表，避免后续再产生不一致形态。
            record.coverage_sources = merged
            await session.flush()
            return True
        except SQLAlchemyError as e:
            logger.error("Error incrementing coverage for %s: %s", canonical_event_id, e)
            raise

    async def create_twitter_analysis(
        self,
        session: AsyncSession,
        tweet_id: str,
        tweet_text: str,
        user_name: str,
        user_group: Optional[str] = None,
        tweet_link: Optional[str] = None,
        tokens: Optional[List[Dict]] = None,
        analysis: Optional[Dict] = None,
        should_notify: bool = False,
        model_name: str = 'deepseek/deepseek-v3.2-exp',
        analysis_version: str = 'v1.0'
    ) -> Optional[AIAnalysisResult]:
        """
        Create or update Twitter analysis result.

        Args:
            session: Database session
            tweet_id: Unique tweet ID
            tweet_text: Tweet text
            user_name: Username
            user_group: User group (e.g., 'KOL', 'exchange')
            tweet_link: Tweet URL
            tokens: Identified tokens list
            analysis: Analysis result dict {sentiment, confidence, summary, reason}
            should_notify: Whether to send notification
            model_name: AI model name
            analysis_version: Analysis version

        Returns:
            Created or updated AIAnalysisResult object or None
        """
        try:
            normalized = _normalize_analysis_payload(analysis)
            analysis = analysis or {}
            final_signal = analysis.get("final_signal") or {}
            score_breakdown = analysis.get("score_breakdown") or {}
            filter_context = analysis.get("filter_context") or final_signal.get("filter_context") or {}
            decision_score = normalized.decision_score
            if decision_score is None and isinstance(filter_context, dict):
                decision_score = _safe_float(
                    filter_context.get("combined_score") or filter_context.get("decision_score")
                )
            trading_recommendation = (
                analysis.get("analysis_state", {}).get("trading_recommendation")
                or analysis.get("trading_recommendation")
                or analysis
            )
            event_factors = (
                analysis.get("analysis_state", {}).get("event_factors")
                or analysis.get("event_factors")
                or {}
            )
            macro_implied_tokens = (
                analysis.get("analysis_state", {}).get("macro_implied_tokens")
                or analysis.get("macro_implied_tokens")
                or []
            )
            notification_priority = analysis.get("notification_priority") or final_signal.get("notification_priority")
            duplicate_meta = _extract_duplicate_meta(analysis)

            normalized_tokens = (
                _normalize_tokens_payload(tokens)
                or _normalize_tokens_payload(analysis.get("matched_candidates"))
            )

            # Check if analysis already exists
            existing = await self.get_by_source(session, 'twitter', tweet_id)

            if existing:
                new_tokens = normalized_tokens if normalized_tokens is not None else (existing.tokens or [])
                # Update existing record
                existing.content_text = tweet_text
                existing.author = user_name
                existing.author_group = user_group
                existing.source_link = tweet_link
                existing.tokens = new_tokens
                existing.sentiment = normalized.sentiment
                existing.confidence = normalized.confidence
                existing.summary = normalized.summary
                existing.reasoning = normalized.reasoning
                existing.key_points = normalized.key_points
                existing.importance_score = normalized.importance_score
                existing.decision_score = decision_score
                existing.market_impact_label = normalized.market_impact_label
                existing.market_impact_score = normalized.market_impact_score
                existing.event_type = normalized.event_type
                existing.should_notify = should_notify
                existing.score_breakdown = score_breakdown
                existing.filter_context = filter_context
                existing.final_signal = final_signal
                existing.trading_recommendation = trading_recommendation
                existing.event_factors = event_factors
                existing.macro_implied_tokens = macro_implied_tokens
                existing.notification_priority = notification_priority
                existing.model_name = model_name
                existing.analysis_version = analysis_version
                if existing.canonical_event_id is None:
                    default_canonical = analysis.get("canonical_event_id") or analysis.get("event_signature") or tweet_id
                    existing.canonical_event_id = default_canonical
                if existing.coverage_count is None:
                    existing.coverage_count = 1
                if not existing.coverage_sources:
                    if user_name or tweet_link or tweet_id:
                        existing.coverage_sources = [
                            {
                                "source": user_name,
                                "source_id": str(tweet_id) if tweet_id is not None else None,
                                "source_type": "twitter",
                                "source_link": tweet_link,
                            }
                        ]
                    else:
                        existing.coverage_sources = []
                if duplicate_meta.get("duplicate_type") is not None:
                    existing.duplicate_type = duplicate_meta["duplicate_type"]
                if duplicate_meta.get("canonical_event_id") is not None:
                    existing.canonical_event_id = _canonical_id_to_str(duplicate_meta["canonical_event_id"])
                if duplicate_meta.get("coverage_count") is not None:
                    existing.coverage_count = duplicate_meta["coverage_count"]
                if duplicate_meta.get("coverage_sources") is not None:
                    existing.coverage_sources = duplicate_meta["coverage_sources"]
                existing.updated_at = utc_now_naive()

                await session.flush()
                await session.refresh(existing)
                logger.debug(f"Updated Twitter analysis: ID={existing.id}, sentiment={existing.sentiment}")
                return existing
            else:
                # Create new record
                result = AIAnalysisResult(
                    source_type='twitter',
                    source_id=tweet_id,
                    source_link=tweet_link,
                    content_type='tweet',
                    content_text=tweet_text,
                    author=user_name,
                    author_group=user_group,

                    # Tokens and analysis
                    tokens=normalized_tokens or [],
                    sentiment=normalized.sentiment,
                    confidence=normalized.confidence,
                    summary=normalized.summary,
                    reasoning=normalized.reasoning,
                    key_points=normalized.key_points,
                    importance_score=normalized.importance_score,
                    decision_score=decision_score,
                    market_impact_label=normalized.market_impact_label,
                    event_type=normalized.event_type,
                    market_impact_score=normalized.market_impact_score,
                    score_breakdown=score_breakdown,
                    filter_context=filter_context,
                    final_signal=final_signal,
                    trading_recommendation=trading_recommendation,
                    event_factors=event_factors,
                    macro_implied_tokens=macro_implied_tokens,
                    notification_priority=notification_priority,
                    duplicate_type=duplicate_meta.get("duplicate_type"),
                    canonical_event_id=duplicate_meta.get("canonical_event_id")
                    or analysis.get("event_signature")
                    or tweet_id,
                    coverage_count=duplicate_meta.get("coverage_count") or 1,
                    coverage_sources=duplicate_meta.get("coverage_sources")
                    or (
                        [
                            {
                                "source": user_name,
                                "source_id": str(tweet_id) if tweet_id is not None else None,
                                "source_type": "twitter",
                                "source_link": tweet_link,
                            }
                        ]
                        if user_name or tweet_link or tweet_id
                        else []
                    ),

                    # Notification
                    should_notify=should_notify,

                    # Metadata
                    model_name=model_name,
                    analysis_version=analysis_version
                )

                session.add(result)
                await session.flush()
                await session.refresh(result)
                logger.debug(f"Created Twitter analysis: ID={result.id}, sentiment={result.sentiment}")
                return result

        except SQLAlchemyError as e:
            logger.error(f"Error creating/updating Twitter analysis: {e}")
            raise

    async def create_news_analysis(
        self,
        session: AsyncSession,
        news_id: int,
        news_title: str,
        news_content: str,
        source: str,
        source_link: Optional[str] = None,
        matched_currencies: Optional[List[str]] = None,
            analysis_state: Optional[Dict] = None,
            model_name: str = 'deepseek/deepseek-v3.2-exp',
            analysis_version: str = 'v1.0'
        ) -> Optional[AIAnalysisResult]:
        """
        Create or update news analysis result.

        Args:
            session: Database session
            news_id: News ID
            news_title: News title
            news_content: News content
            source: News source
            source_link: News URL
            matched_currencies: Matched currency list
            analysis_state: NewsAnalysisState dict
            model_name: AI model name
            analysis_version: Analysis version

        Returns:
            Created or updated AIAnalysisResult object or None
        """
        try:
            analysis_state = analysis_state or {}
            normalized = _extract_analysis_from_state(analysis_state)
            trading_rec = analysis_state.get("trading_recommendation") or {}
            final_signal = analysis_state.get("final_signal") or {}
            score_breakdown = trading_rec.get("score_breakdown") or {}
            filter_context = analysis_state.get("filter_context") or final_signal.get("filter_context") or {}
            decision_score = normalized.decision_score
            if decision_score is None and isinstance(filter_context, dict):
                decision_score = _safe_float(
                    filter_context.get("combined_score") or filter_context.get("decision_score")
                )
            event_factors = analysis_state.get("event_factors") or {}
            macro_implied_tokens = analysis_state.get("macro_implied_tokens") or []
            notification_priority = (
                analysis_state.get("notification_priority")
                or final_signal.get("notification_priority")
            )
            event_fields = _extract_event_enrichment(analysis_state)
            duplicate_meta = _extract_duplicate_meta(analysis_state)

            tokens = _normalize_tokens_payload(analysis_state.get("matched_candidates"))
            if tokens is None and matched_currencies:
                tokens = [{"symbol": c.upper()} for c in matched_currencies]
            # Ensure tokens is always an array (or empty) at write time
            tokens = tokens or []

            # Check if analysis already exists
            existing = await self.get_by_source(session, 'news', str(news_id))

            if existing:
                # Update existing record
                existing.content_text = f"{news_title}\n\n{news_content[:500]}"
                existing.author = source
                existing.source_link = source_link
                existing.tokens = tokens
                existing.importance_score = normalized.importance_score
                existing.decision_score = decision_score
                existing.sentiment = normalized.sentiment
                existing.confidence = normalized.confidence
                existing.summary = normalized.summary
                existing.reasoning = normalized.reasoning
                existing.key_points = normalized.key_points
                existing.market_impact_label = normalized.market_impact_label
                existing.market_impact_score = normalized.market_impact_score
                existing.event_type = normalized.event_type or event_fields.get("scenario")
                existing.should_notify = analysis_state.get('should_notify', False)
                existing.score_breakdown = score_breakdown
                existing.filter_context = filter_context
                existing.final_signal = final_signal
                existing.trading_recommendation = trading_rec
                existing.event_factors = event_factors
                existing.macro_implied_tokens = macro_implied_tokens
                existing.notification_priority = notification_priority
                existing.model_name = model_name
                existing.analysis_version = analysis_version
                existing.event_struct = event_fields.get("event_struct")
                existing.event_key = event_fields.get("event_key")
                existing.thread_id = event_fields.get("thread_id")
                existing.scenario = event_fields.get("scenario")
                existing.actor = event_fields.get("actor")
                existing.actor_type = event_fields.get("actor_type")
                existing.action_type = event_fields.get("action_type")
                existing.magnitude_value = event_fields.get("magnitude_value")
                existing.magnitude_unit = event_fields.get("magnitude_unit")
                if existing.canonical_event_id is None:
                    default_canonical = (
                        _canonical_id_to_str(
                            duplicate_meta.get("canonical_event_id")
                            or analysis_state.get("event_signature")
                            or event_fields.get("event_key")
                            or news_id
                        )
                    )
                    existing.canonical_event_id = default_canonical
                if existing.coverage_count is None:
                    existing.coverage_count = 1
                if not existing.coverage_sources:
                    # 初始化为统一字典结构，便于前端展示/跳转。
                    if source or source_link or news_id is not None:
                        existing.coverage_sources = [
                            {
                                "source": source,
                                "source_id": str(news_id) if news_id is not None else None,
                                "source_type": "news",
                                "source_link": source_link,
                            }
                        ]
                    else:
                        existing.coverage_sources = []
                if duplicate_meta.get("duplicate_type") is not None:
                    existing.duplicate_type = duplicate_meta["duplicate_type"]
                if duplicate_meta.get("canonical_event_id") is not None:
                    existing.canonical_event_id = duplicate_meta["canonical_event_id"]
                if duplicate_meta.get("coverage_count") is not None:
                    existing.coverage_count = duplicate_meta["coverage_count"]
                if duplicate_meta.get("coverage_sources") is not None:
                    existing.coverage_sources = duplicate_meta["coverage_sources"]
                existing.updated_at = utc_now_naive()

                await session.flush()
                await session.refresh(existing)
                logger.debug(
                    f"Updated news analysis: ID={existing.id}, importance_score={existing.importance_score}"
                )
                return existing
            else:
                # Create new record
                result = AIAnalysisResult(
                    source_type='news',
                    source_id=str(news_id),
                    source_link=source_link,
                    content_type='news_article',
                    content_text=f"{news_title}\n\n{news_content[:500]}",
                    author=source,

                    # Tokens
                    tokens=tokens,

                    # Classification / Impact
                    importance_score=normalized.importance_score,
                    decision_score=decision_score,

                    # Sentiment analysis
                    sentiment=normalized.sentiment,
                    confidence=normalized.confidence,
                    summary=normalized.summary,
                    reasoning=normalized.reasoning,
                    key_points=normalized.key_points,

                    # Market impact (News-specific)
                    market_impact_label=normalized.market_impact_label,
                    event_type=normalized.event_type or event_fields.get("scenario"),
                    market_impact_score=normalized.market_impact_score,
                    score_breakdown=score_breakdown,
                    filter_context=filter_context,
                    final_signal=final_signal,
                    trading_recommendation=trading_rec,
                    event_factors=event_factors,
                    macro_implied_tokens=macro_implied_tokens,
                    notification_priority=notification_priority,
                    event_struct=event_fields.get("event_struct"),
                    event_key=event_fields.get("event_key"),
                    thread_id=event_fields.get("thread_id"),
                    scenario=event_fields.get("scenario"),
                    actor=event_fields.get("actor"),
                    actor_type=event_fields.get("actor_type"),
                    action_type=event_fields.get("action_type"),
                    magnitude_value=event_fields.get("magnitude_value"),
                    magnitude_unit=event_fields.get("magnitude_unit"),
                    duplicate_type=duplicate_meta.get("duplicate_type"),
                    canonical_event_id=_canonical_id_to_str(
                        duplicate_meta.get("canonical_event_id")
                        or analysis_state.get("event_signature")
                        or event_fields.get("event_key")
                        or news_id
                    ),
                    coverage_count=duplicate_meta.get("coverage_count") or 1,
                    coverage_sources=duplicate_meta.get("coverage_sources")
                    or (
                        [
                            {
                                "source": source,
                                "source_id": str(news_id) if news_id is not None else None,
                                "source_type": "news",
                                "source_link": source_link,
                            }
                        ]
                        if source or source_link or news_id is not None
                        else []
                    ),

                    # Notification
                    should_notify=analysis_state.get('should_notify', False),

                    # Metadata
                    model_name=model_name,
                    analysis_version=analysis_version
                )

                session.add(result)
                await session.flush()
                await session.refresh(result)
                logger.debug(
                    f"Created news analysis: ID={result.id}, importance_score={result.importance_score}"
                )
                return result

        except SQLAlchemyError as e:
            logger.error(f"Error creating/updating news analysis: {e}")
            raise

    async def create_oi_signal_analysis(
        self,
        session: AsyncSession,
        source_id: str,
        raw_text: str,
        oi_event: Dict[str, Any],
        analysis_state: Optional[Dict[str, Any]] = None,
        tokens: Optional[List[Dict[str, Any]]] = None,
        should_notify: bool = False,
        model_name: str = "oi_heuristic_v1",
        analysis_version: str = "v1.0",
    ) -> Optional[AIAnalysisResult]:
        """创建或更新 OI 异动的 AI 分析结果。

        Args:
            session: 数据库会话。
            source_id: 唯一来源标识（如 ``telegram://channel/message_id``）。
            raw_text: 原始 OI 消息文本。
            oi_event: 结构化 OI 指标字典。
            analysis_state: Agent 产出的分析状态（含 trading_recommendation 等）。
            tokens: 识别到的代币列表。
            should_notify: 是否需要通知。
            model_name: 使用的模型名称。
            analysis_version: 分析版本号。

        Returns:
            创建或更新后的 ``AIAnalysisResult``。
        """
        try:
            analysis_state = analysis_state or {}
            normalized = _extract_analysis_from_state(analysis_state)
            trading_rec = analysis_state.get("trading_recommendation") or {}
            final_signal = analysis_state.get("final_signal") or {}
            score_breakdown = trading_rec.get("score_breakdown") or {}
            filter_context = analysis_state.get("filter_context") or final_signal.get("filter_context") or {}
            decision_score = normalized.decision_score
            if decision_score is None and isinstance(filter_context, dict):
                decision_score = _safe_float(
                    filter_context.get("combined_score") or filter_context.get("decision_score")
                )
            event_fields = _extract_event_enrichment(analysis_state)
            duplicate_meta = _extract_duplicate_meta(analysis_state)

            normalized_tokens = _normalize_tokens_payload(tokens) or []
            event_struct = event_fields.get("event_struct") or {}
            if isinstance(event_struct, dict):
                event_struct.setdefault("oi_event", oi_event)

            existing = await self.get_by_source(session, "oi_signal", source_id)
            if existing:
                existing.content_text = raw_text
                existing.tokens = normalized_tokens
                existing.summary = normalized.summary
                existing.sentiment = normalized.sentiment
                existing.confidence = normalized.confidence
                existing.reasoning = normalized.reasoning
                existing.key_points = normalized.key_points
                existing.importance_score = normalized.importance_score
                existing.decision_score = decision_score
                existing.market_impact_label = normalized.market_impact_label
                existing.market_impact_score = normalized.market_impact_score
                existing.event_type = normalized.event_type or "oi_spike"
                existing.score_breakdown = score_breakdown
                existing.filter_context = filter_context
                existing.final_signal = final_signal
                existing.trading_recommendation = trading_rec
                existing.event_factors = analysis_state.get("event_factors") or {"oi_event": oi_event}
                existing.event_struct = event_struct
                existing.notification_priority = (
                    analysis_state.get("notification_priority")
                    or final_signal.get("notification_priority")
                )
                existing.should_notify = should_notify
                existing.model_name = model_name
                existing.analysis_version = analysis_version
                existing.duplicate_type = duplicate_meta.get("duplicate_type")
                existing.canonical_event_id = duplicate_meta.get("canonical_event_id") or source_id
                await session.flush()
                await session.refresh(existing)
                return existing

            result = AIAnalysisResult(
                source_type="oi_signal",
                source_id=str(source_id),
                source_link=analysis_state.get("source_link") or source_id,
                content_type="telegram_message",
                content_text=raw_text,
                author=analysis_state.get("channel_title"),
                author_group=analysis_state.get("exchange"),
                tokens=normalized_tokens,
                sentiment=normalized.sentiment,
                confidence=normalized.confidence,
                summary=normalized.summary,
                reasoning=normalized.reasoning,
                key_points=normalized.key_points,
                importance_score=normalized.importance_score,
                decision_score=decision_score,
                market_impact_label=normalized.market_impact_label,
                market_impact_score=normalized.market_impact_score,
                event_type=normalized.event_type or "oi_spike",
                score_breakdown=score_breakdown,
                filter_context=filter_context,
                final_signal=final_signal,
                trading_recommendation=trading_rec,
                event_factors=analysis_state.get("event_factors") or {"oi_event": oi_event},
                event_struct=event_struct or {},
                notification_priority=analysis_state.get("notification_priority") or final_signal.get("notification_priority"),
                should_notify=should_notify,
                model_name=model_name,
                analysis_version=analysis_version,
                duplicate_type=duplicate_meta.get("duplicate_type"),
                canonical_event_id=duplicate_meta.get("canonical_event_id") or source_id,
                coverage_count=duplicate_meta.get("coverage_count") or 1,
                coverage_sources=duplicate_meta.get("coverage_sources") or [],
            )
            session.add(result)
            await session.flush()
            await session.refresh(result)
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error creating/updating OI analysis: {e}")
            raise

    # ========== QUERY METHODS ==========

    async def get_by_source(
        self,
        session: AsyncSession,
        source_type: str,
        source_id: str
    ) -> Optional[AIAnalysisResult]:
        """
        Query analysis result by source.

        Args:
            session: Database session
            source_type: Source type 'twitter' | 'news'
            source_id: Source ID

        Returns:
            AIAnalysisResult or None
        """
        try:
            stmt = select(AIAnalysisResult).where(
                and_(
                    AIAnalysisResult.source_type == source_type,
                    AIAnalysisResult.source_id == source_id
                )
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error querying analysis by source: {e}")
            raise

    async def get_recent_analyses(
        self,
        session: AsyncSession,
        source_type: Optional[str] = None,
        hours: int = 24,
        limit: int = 100
    ) -> List[AIAnalysisResult]:
        """
        Get recent analysis results.

        Args:
            session: Database session
            source_type: Optional, filter by source type
            hours: Time range in hours
            limit: Result limit

        Returns:
            List of AIAnalysisResult
        """
        try:
            since = utc_now_naive() - timedelta(hours=hours)

            stmt = select(AIAnalysisResult).where(
                AIAnalysisResult.created_at >= since
            )

            if source_type:
                stmt = stmt.where(AIAnalysisResult.source_type == source_type)

            stmt = stmt.order_by(AIAnalysisResult.created_at.desc()).limit(limit)

            result = await session.execute(stmt)
            return list(result.scalars().all())

        except SQLAlchemyError as e:
            logger.error(f"Error getting recent analyses: {e}")
            raise

    async def get_pending_notifications(
        self,
        session: AsyncSession,
        source_type: Optional[str] = None
    ) -> List[AIAnalysisResult]:
        """
        Get pending notification analysis results.

        Args:
            session: Database session
            source_type: Optional, filter by source type

        Returns:
            List of pending AIAnalysisResult
        """
        try:
            stmt = select(AIAnalysisResult).where(
                and_(
                    AIAnalysisResult.should_notify == True,
                    AIAnalysisResult.notified_at.is_(None)
                )
            )

            if source_type:
                stmt = stmt.where(AIAnalysisResult.source_type == source_type)

            stmt = stmt.order_by(AIAnalysisResult.created_at.asc())

            result = await session.execute(stmt)
            return list(result.scalars().all())

        except SQLAlchemyError as e:
            logger.error(f"Error getting pending notifications: {e}")
            raise

    async def mark_as_notified(
        self,
        session: AsyncSession,
        analysis_id: int
    ) -> bool:
        """
        Mark analysis as notified.

        Args:
            session: Database session
            analysis_id: Analysis result ID

        Returns:
            Success status
        """
        try:
            stmt = select(AIAnalysisResult).where(AIAnalysisResult.id == analysis_id)
            result = await session.execute(stmt)
            analysis = result.scalar_one_or_none()

            if analysis:
                analysis.notified_at = utc_now_naive()
                analysis.notification_sent = True
                await session.flush()
                logger.debug(f"Marked analysis {analysis_id} as notified")
                return True
            return False

        except SQLAlchemyError as e:
            logger.error(f"Error marking as notified: {e}")
            raise

    # ========== STATISTICS METHODS ==========

    async def get_sentiment_stats(
        self,
        session: AsyncSession,
        source_type: Optional[str] = None,
        hours: int = 24
    ) -> Dict[str, int]:
        """
        Get sentiment statistics.

        Args:
            session: Database session
            source_type: Optional, filter by source type
            hours: Time range in hours

        Returns:
            {'positive': 45, 'neutral': 120, 'negative': 35}
        """
        try:
            since = utc_now_naive() - timedelta(hours=hours)

            stmt = select(
                AIAnalysisResult.sentiment,
                func.count(AIAnalysisResult.id).label('count')
            ).where(
                AIAnalysisResult.created_at >= since
            )

            if source_type:
                stmt = stmt.where(AIAnalysisResult.source_type == source_type)

            stmt = stmt.group_by(AIAnalysisResult.sentiment)

            result = await session.execute(stmt)
            return {row.sentiment: row.count for row in result if row.sentiment}

        except SQLAlchemyError as e:
            logger.error(f"Error getting sentiment stats: {e}")
            raise

    async def get_token_mentions(
        self,
        session: AsyncSession,
        hours: int = 24,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get token mention counts using JSONB query.

        Uses PostgreSQL jsonb_array_elements to expand tokens array.

        Args:
            session: Database session
            hours: Time range in hours
            limit: Result limit

        Returns:
            [{'symbol': 'BTC', 'mentions': 45}, ...]
        """
        try:
            since = utc_now_naive() - timedelta(hours=hours)

            # PostgreSQL JSONB array query
            # Note:
            #   We order primarily by recency (latest_created_at) so that
            #   freshly inserted symbols are always visible in the first `limit`
            #   rows, even on a populated database.
            sql = text("""
                SELECT
                    token->>'symbol' AS symbol,
                    COUNT(*) AS mentions,
                    MAX(created_at) AS latest_created_at
                FROM "AIAnalysisResult",
                     jsonb_array_elements(tokens::jsonb) AS token
                WHERE created_at >= :since
                  AND tokens IS NOT NULL
                  AND jsonb_typeof(tokens::jsonb) = 'array'
                  AND tokens::jsonb != '[]'::jsonb
                GROUP BY token->>'symbol'
                ORDER BY latest_created_at DESC
                LIMIT :limit
            """)

            result = await session.execute(
                sql,
                {'since': since, 'limit': limit}
            )

            return [
                {'symbol': row.symbol, 'mentions': row.mentions}
                for row in result
                if row.symbol
            ]

        except SQLAlchemyError as e:
            logger.error(f"Error getting token mentions: {e}")
            raise

    async def get_recent_symbol_events(
        self,
        session: AsyncSession,
        symbol: str,
        hours: int = 24,
        limit: int = 10,
        source_type: str = "news",
    ) -> List[AIAnalysisResult]:
        """
        Get recent AIAnalysisResult entries that mention a given token symbol.

        说明：
            为了简化依赖，这里复用 get_recent_analyses，再在 Python 层过滤 tokens。
            由于窗口和 limit 都较小，该方法适合作为 Agent 的短期叙事上下文查询使用。
        """
        try:
            analyses = await self.get_recent_analyses(
                session=session,
                source_type=source_type,
                hours=hours,
                limit=200,
            )
            sym_upper = symbol.upper()
            results: List[AIAnalysisResult] = []
            for a in analyses:
                tokens = a.tokens or []
                for t in tokens:
                    try:
                        if isinstance(t, dict) and str(t.get("symbol", "")).upper() == sym_upper:
                            results.append(a)
                            break
                    except Exception:
                        continue
                if len(results) >= limit:
                    break
            # 新 → 旧 的顺序由调用方控制，这里默认返回按 created_at 降序的结果列表
            return results
        except SQLAlchemyError as e:
            logger.error(f"Error getting recent symbol events for {symbol}: {e}")
            raise

    async def get_recent_symbol_threads(
        self,
        session: AsyncSession,
        symbol: str,
        hours: int = 24,
        limit_threads: int = 10,
        source_type: str = "news",
    ) -> List[Dict[str, Any]]:
        """
        Group recent analyses mentioning a symbol into threads (thread_id/event_key).
        """
        try:
            analyses = await self.get_recent_symbol_events(
                session=session,
                symbol=symbol,
                hours=hours,
                limit=200,
                source_type=source_type,
            )
            threads: Dict[str, Dict[str, Any]] = {}
            for a in analyses:
                # determine grouping key
                key = getattr(a, "thread_id", None) or getattr(a, "event_key", None) or getattr(a, "source_id", None)
                if not key:
                    continue
                bucket = threads.setdefault(
                    key,
                    {
                        "thread_id": getattr(a, "thread_id", None) or key,
                        "event_key": getattr(a, "event_key", None),
                        "actor": getattr(a, "actor", None),
                        "actor_type": getattr(a, "actor_type", None),
                        "scenario": getattr(a, "scenario", None),
                        "symbol": symbol.upper(),
                        "events": [],
                        "aggregate_magnitude": 0.0,
                        "aggregate_magnitude_unit": getattr(a, "magnitude_unit", None),
                        "aggregate_direction": getattr(a, "market_impact_label", None),
                        "latest_created_at": getattr(a, "created_at", None),
                    },
                )
                bucket["events"].append(
                    {
                        "id": a.id,
                        "created_at": getattr(a, "created_at", None),
                        "summary": getattr(a, "summary", None),
                        "importance_score": getattr(a, "importance_score", None),
                        "market_impact_label": getattr(a, "market_impact_label", None),
                        "sentiment": getattr(a, "sentiment", None),
                    }
                )
                mag_val = getattr(a, "magnitude_value", None)
                if isinstance(mag_val, (int, float)):
                    bucket["aggregate_magnitude"] = (bucket.get("aggregate_magnitude") or 0.0) + float(mag_val)
                bucket["aggregate_magnitude_unit"] = bucket.get("aggregate_magnitude_unit") or getattr(a, "magnitude_unit", None)
                created_at = getattr(a, "created_at", None)
                if created_at and (bucket.get("latest_created_at") is None or created_at > bucket["latest_created_at"]):
                    bucket["latest_created_at"] = created_at
                bucket["aggregate_direction"] = bucket.get("aggregate_direction") or getattr(a, "market_impact_label", None)

            threads_list = list(threads.values())
            threads_list.sort(key=lambda t: t.get("latest_created_at") or datetime.min, reverse=True)
            return threads_list[:limit_threads]
        except SQLAlchemyError as e:
            logger.error(f"Error getting recent symbol threads for {symbol}: {e}")
            raise

    async def get_author_stats(
        self,
        session: AsyncSession,
        source_type: str = 'twitter',
        hours: int = 24,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get author posting statistics.

        Args:
            session: Database session
            source_type: Source type
            hours: Time range in hours
            limit: Result limit

        Returns:
            [{'author': 'CZ', 'total': 15, 'positive': 10, 'negative': 2, 'neutral': 3}, ...]
        """
        try:
            since = utc_now_naive() - timedelta(hours=hours)

            stmt = select(
                AIAnalysisResult.author,
                func.count(AIAnalysisResult.id).label('total'),
                func.sum(
                    cast(AIAnalysisResult.sentiment == 'positive', Integer)
                ).label('positive'),
                func.sum(
                    cast(AIAnalysisResult.sentiment == 'negative', Integer)
                ).label('negative'),
                func.sum(
                    cast(AIAnalysisResult.sentiment == 'neutral', Integer)
                ).label('neutral')
            ).where(
                and_(
                    AIAnalysisResult.source_type == source_type,
                    AIAnalysisResult.created_at >= since,
                    AIAnalysisResult.author.isnot(None)
                )
            ).group_by(
                AIAnalysisResult.author
            ).order_by(
                func.count(AIAnalysisResult.id).desc()
            ).limit(limit)

            result = await session.execute(stmt)

            return [
                {
                    'author': row.author,
                    'total': row.total,
                    'positive': row.positive or 0,
                    'negative': row.negative or 0,
                    'neutral': row.neutral or 0
                }
                for row in result
            ]

        except SQLAlchemyError as e:
            logger.error(f"Error getting author stats: {e}")
            raise

    async def get_analysis_stats(
        self,
        session: AsyncSession,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get comprehensive statistics.

        Args:
            session: Database session
            hours: Time range in hours

        Returns:
            Comprehensive statistics dict
        """
        try:
            since = utc_now_naive() - timedelta(hours=hours)

            # Total count
            total_stmt = select(func.count(AIAnalysisResult.id)).where(
                AIAnalysisResult.created_at >= since
            )
            total_result = await session.execute(total_stmt)
            total = total_result.scalar()

            # By source type
            source_stmt = select(
                AIAnalysisResult.source_type,
                func.count(AIAnalysisResult.id).label('count')
            ).where(
                AIAnalysisResult.created_at >= since
            ).group_by(AIAnalysisResult.source_type)

            source_result = await session.execute(source_stmt)
            by_source = {row.source_type: row.count for row in source_result}

            # Notification stats
            notify_stmt = select(
                func.count(AIAnalysisResult.id)
            ).where(
                and_(
                    AIAnalysisResult.created_at >= since,
                    AIAnalysisResult.should_notify == True
                )
            )
            notify_result = await session.execute(notify_stmt)
            should_notify_count = notify_result.scalar()

            notified_stmt = select(
                func.count(AIAnalysisResult.id)
            ).where(
                and_(
                    AIAnalysisResult.created_at >= since,
                    AIAnalysisResult.notified_at.isnot(None)
                )
            )
            notified_result = await session.execute(notified_stmt)
            notified_count = notified_result.scalar()

            return {
                'total_analyses': total,
                'by_source': by_source,
                'should_notify': should_notify_count,
                'notified': notified_count,
                'pending_notifications': should_notify_count - notified_count,
                'hours': hours,
                'since': since.isoformat()
            }

        except SQLAlchemyError as e:
            logger.error(f"Error getting analysis stats: {e}")
            raise

    async def search_by_token(
        self,
        session: AsyncSession,
        token_symbol: str,
        hours: Optional[int] = None,
        limit: int = 50
    ) -> List[AIAnalysisResult]:
        """
        Search analyses mentioning a specific token using JSONB @> operator.

        Args:
            session: Database session
            token_symbol: Token symbol to search
            hours: Optional time range
            limit: Result limit

        Returns:
            List of AIAnalysisResult
        """
        try:
            normalized_symbol = token_symbol.strip().upper()

            # Use PostgreSQL @> operator for JSONB containment
            query = select(AIAnalysisResult).where(
                AIAnalysisResult.tokens.op('@>')(
                    cast([{"symbol": normalized_symbol}], JSONB)
                )
            )

            if hours is not None:
                time_threshold = utc_now_naive() - timedelta(hours=hours)
                query = query.where(AIAnalysisResult.created_at >= time_threshold)

            query = query.order_by(AIAnalysisResult.created_at.desc()).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())

        except SQLAlchemyError as e:
            logger.error(f"Error searching by token '{token_symbol}': {e}")
            raise

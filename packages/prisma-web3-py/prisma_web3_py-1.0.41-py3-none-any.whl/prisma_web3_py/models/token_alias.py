# -*- coding: utf-8 -*-
"""
代币别名模型。

该模型将别名与 Token 本体解耦，便于管理多语言/多来源的别名词典。
"""

from typing import Optional

from sqlalchemy import Boolean, Float, Integer, String, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base


class TokenAlias(Base):
    """Token 别名表，存储规范化 key 与元数据。"""

    __tablename__ = "TokenAlias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    token_id: Mapped[int] = mapped_column(Integer, ForeignKey("public.Token.id"), nullable=False)
    alias: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    alias_type: Mapped[str] = mapped_column(String(50), nullable=False)
    lang: Mapped[Optional[str]] = mapped_column(String(10))
    source: Mapped[Optional[str]] = mapped_column(String(50))
    is_preferred: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deprecated: Mapped[bool] = mapped_column(Boolean, default=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0)

    token: Mapped["Token"] = relationship("Token", back_populates="aliases_rel")

    __table_args__ = (
        Index("idx_token_alias_normalized_lang", "normalized_key", "lang"),
        UniqueConstraint("token_id", "normalized_key", "alias_type", name="uq_token_alias_token_key_type"),
        {"schema": "public"},
    )

    def __repr__(self) -> str:
        return f"<TokenAlias(id={self.id}, alias={self.alias}, token_id={self.token_id})>"

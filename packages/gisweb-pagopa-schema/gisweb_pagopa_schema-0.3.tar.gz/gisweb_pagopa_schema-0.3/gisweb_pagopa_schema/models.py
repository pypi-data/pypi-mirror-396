from __future__ import annotations

from typing import Literal
from uuid import UUID, uuid4
from datetime import date, datetime, timezone
from pydantic import BaseModel
from sqlalchemy import (
    ARRAY, DateTime, String, Float, Integer, Boolean, Text, ForeignKey
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.mutable import MutableList



class Base(DeclarativeBase):
    pass


class BaseUUIDModel(Base):
    __abstract__ = True
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False,
        index=True
    )


class PagopaClientAuth(Base):
    __tablename__ = "client_auth"
    __table_args__ = {"schema": "pagopa"}
    username: Mapped[str] = mapped_column(String, primary_key=True)
    pwd: Mapped[str] = mapped_column(String, nullable=False)
    print_pwd: Mapped[str] = mapped_column(String, nullable=False)

    ip_whitelist: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        nullable=True
    )


class PagamentoTipo(Base):
    __tablename__ = "pagamento_tipo"
    __table_args__ = {"schema": "pagopa"}

    id: Mapped[str] = mapped_column(String, primary_key=True)
    descrizione: Mapped[str | None]

    importi: Mapped[list[ImportoTipo]] = relationship(
        back_populates="pagamento_tipo",
        cascade="all, delete-orphan"
    )
    
class ImportoTipo(Base):
    __tablename__ = "importo_tipo"
    __table_args__ = {"schema": "pagopa"}

    id: Mapped[str] = mapped_column(String, primary_key=True)
    descrizione: Mapped[str | None]

    pagamento_tipo_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("pagopa.pagamento_tipo.id")
    )

    pagamento_tipo: Mapped[PagamentoTipo | None] = relationship(
        back_populates="importi"
    )

    configs: Mapped[list[ConfigPagamenti]] = relationship(
        back_populates="importo_ref"
    )

class ConfigPagamenti(BaseUUIDModel):
    __tablename__ = "config"
    __table_args__ = {"schema": "pagopa"}

    modulo: Mapped[str] = mapped_column(String, nullable=False)

    importo_tipo: Mapped[str] = mapped_column(
        ForeignKey("pagopa.importo_tipo.id"),
        nullable=False
    )

    capitolo: Mapped[str | None]
    descrizione: Mapped[str | None]
    importo: Mapped[float | None]
    azione: Mapped[str | None]
    attivo: Mapped[bool] = mapped_column(Boolean, default=True)
    ordine: Mapped[int | None]
    gg_scadenza: Mapped[int | None]

    importo_ref: Mapped[ImportoTipo] = relationship(
        back_populates="configs",
        lazy="joined"
    )

class Importo(BaseUUIDModel):
    __tablename__ = "importo"
    __table_args__ = {"schema": "pagopa"}

    tipo_id: Mapped[str] = mapped_column(
        ForeignKey("pagopa.importo_tipo.id"),
        nullable=False
    )

    prog: Mapped[int]
    importo: Mapped[float]
    causale: Mapped[str | None]
    capitolo: Mapped[str | None]

    pagamento_id: Mapped[UUID] = mapped_column(
        ForeignKey("pagopa.pagamento.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False
    )

    pagamento: Mapped[Pagamento] = relationship(
        back_populates="importi",
        lazy="selectin"
    )

    tipo_importo: Mapped[ImportoTipo] = relationship(
        lazy="joined"
    )


class Pagamento(BaseUUIDModel):
    __tablename__ = "pagamento"
    __table_args__ = {"schema": "pagopa"}

    document_id: Mapped[UUID | None]
    app_id: Mapped[str | None]
    parent_id: Mapped[UUID | None]

    tipo_id: Mapped[str] = mapped_column(
        ForeignKey("pagopa.pagamento_tipo.id"),
        default="VARIE",
        nullable=False
    )

    idpos: Mapped[str | None]
    iddeb: Mapped[str] = mapped_column(String, nullable=False, index=True, unique=True)
    iuv: Mapped[str | None]
    modello: Mapped[str | None]
    servizio: Mapped[str | None]

    importo: Mapped[float | None]
    pagato: Mapped[float | None]

    causale: Mapped[str | None]

    data_inizio: Mapped[date | None]
    data_scadenza: Mapped[date | None]
    data_scadenza_avviso: Mapped[date | None]
    tipo_scadenza: Mapped[str | None]
    gg_scadenza: Mapped[int | None]
    oltre_scadenza: Mapped[bool | None] = mapped_column(Boolean, default=False, nullable=True)

    data_pagamento: Mapped[date | None]
    ora_pagamento: Mapped[str | None]
    attestante: Mapped[str | None]

    data_inserimento: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    stato: Mapped[str | None]
    esito: Mapped[str | None]

    accertamento: Mapped[str | None]
    gruppo: Mapped[str | None]
    ordinamento: Mapped[int | None]
    rata: Mapped[int | None]
    tassonomia: Mapped[str | None]

    sog_tipo: Mapped[str | None]
    cf_piva: Mapped[str | None]
    nome: Mapped[str | None]
    cognome: Mapped[str | None]
    ragione_sociale: Mapped[str | None]
    indirizzo: Mapped[str | None]
    civico: Mapped[str | None]
    cap: Mapped[str | None]
    localita: Mapped[str | None]
    provincia: Mapped[str | None]
    nazione: Mapped[str | None]
    email: Mapped[str | None]

    azione: Mapped[str | None]
    info: Mapped[str | None]

    readers: Mapped[list[str] | None] = mapped_column(
        MutableList.as_mutable(ARRAY(String)), nullable=True
    )

    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_by_id: Mapped[str | None]

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc)
    )
    created_by_id: Mapped[str | None]
    
    removed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc)
    )
    removed_by_id: Mapped[str | None]

    tipo_pagamento: Mapped[PagamentoTipo] = relationship(
        lazy="joined"
    )

    importi: Mapped[list[Importo]] = relationship(
        back_populates="pagamento",
        cascade="all",
        lazy="selectin",
        order_by="Importo.prog"
    )



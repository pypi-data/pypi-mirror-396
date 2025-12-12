from __future__ import annotations
from typing import List, Literal
from uuid import UUID
from pydantic import BaseModel
from datetime import date, datetime

class ISettingsPagoPa(BaseModel):
    wsUrl: str
    wsUser: str
    wsPassword: str
    wsPrintUrl: str
    logoUrl: str
    codiceIpa: str
    codiceServizio: str
    notificaOK: str | None = None
    notificaKO: str | None = None
    notificaPagamento: str


class PagamentoTipoBase(BaseModel):
    id: str
    descrizione: str | None = None

    model_config = {
        "from_attributes": True
    }


class PagamentoTipoRead(PagamentoTipoBase):
    pass

class ImportoTipoBase(BaseModel):
    id: str
    descrizione: str | None = None

    model_config = {
        "from_attributes": True
    }


class ImportoTipoRead(ImportoTipoBase):
    pass


class ImportoBase(BaseModel):
    tipo_id: str
    prog: int
    importo: float
    causale: str | None = None
    capitolo: str | None = None

    model_config = {
        "from_attributes": True
    }


class ImportoCreate(ImportoBase):
    pagamento_id: UUID


class ImportoUpdate(BaseModel):
    importo: float | None = None
    causale: str | None = None
    capitolo: str | None = None


class ImportoRead(ImportoBase):
    id: UUID
    pagamento_id: UUID
    tipo_importo: ImportoTipoRead | None = None


class ConfigPagamentiBase(BaseModel):
    modulo: str
    pagamento_tipo: str
    importo_tipo: str

    capitolo: str | None = None
    descrizione: str | None = None
    importo: float | None = None
    azione: str | None = None
    attivo: bool = False
    ordine: int | None = None
    gg_scadenza: int | None = None

    model_config = {
        "from_attributes": True
    }


class ConfigPagamentiCreate(ConfigPagamentiBase):
    pass


class ConfigPagamentiUpdate(BaseModel):
    descrizione: str | None = None
    importo: float | None = None
    azione: str | None = None
    attivo: bool | None = None
    ordine: int | None = None
    gg_scadenza: int | None = None


class ConfigPagamentiRead(ConfigPagamentiBase):
    id: UUID
    pagamento: PagamentoTipoRead | None = None
    importo_def: ImportoTipoRead | None = None




class PagamentoBase(BaseModel):
    document_id: UUID
    parent_id: UUID | None = None
    tipo_id: str

    idpos: str | None = None
    iddeb: str | None = None
    iuv: str | None = None
    modello: str | None = None
    servizio: str | None = None

    importo: float | None = None
    pagato: float | None = None
    causale: str | None = None

    data_inizio: date | None = None
    data_scadenza: date | None = None
    data_scadenza_avviso: date | None = None

    tipo_scadenza: str | None = None
    testo_scadenza: str | None = None
    gg_scadenza: int | None = None

    data_pagamento: date | None = None
    ora_pagamento: str | None = None
    attestante: str | None = None

    data_inserimento: datetime | None = None

    stato: str | None = None
    esito: str | None = None
    accertamento: str | None = None
    gruppo: str | None = None
    ordinamento: int | None = None
    rata: int | None = None
    tassonomia: str | None = None

    soggetto: str | None = None
    cf_piva: str | None = None
    nome: str | None = None
    cognome: str | None = None
    denominazione: str | None = None
    indirizzo: str | None = None
    civico: str | None = None
    cap: str | None = None
    loc: str | None = None
    prov: str | None = None
    nazione: str | None = None
    email: str | None = None
    azione: str | None = None
    info: str | None = None

    readers: list[str] | None = None

    updated_at: datetime | None = None
    updated_by_id: str | None = None

    created_at: datetime | None = None
    created_by_id: str | None = None
    removed: bool = False

    model_config = {
        "from_attributes": True
    }


class PagamentoCreate(PagamentoBase):
    pass


class PagamentoUpdate(BaseModel):
    stato: str | None = None
    esito: str | None = None
    pagato: float | None = None
    readers: list[str] | None = None
    removed: bool | None = None


class PagamentoRead(PagamentoBase):
    id: UUID
    tipo_pagamento: PagamentoTipoRead | None = None
    importi: list[ImportoRead] = []
















class IPagamentoAzione(BaseModel):
    id: UUID
    tipo_id: str | None = None
    descrizione: str | None = None
    idpos: str | None = None
    importo: float  | None = None   
    causale: str | None = None
    gg_scadenza: int | None = None
    importi: list[ImportoRead]

class IPagamentoImportiCreate(PagamentoBase):
    id: UUID
    readers: list[str] | None = None
    importi: list[ImportoRead]
    
class IPagamentoImportiRead(PagamentoBase):
    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None
    readers: List[str] | None = None
    importi: list[ImportoRead]
    
class IEsito(BaseModel):
    esito: Literal["OK", "ERROR"]
    messaggio: str | None = None
    
    
class IChiaveDebito(BaseModel):
    idpos: str | None = None
    iddeb: str | None = None
    codice: str | None = None #codice servizio (tipo pagamento)
    
class IDebito(IChiaveDebito):
    iuv: str | None = None
    dettaglio: str | None = None
    gruppo: str | None = None
    ordinamento: int | None = None
    data_inizio: date
    data_scadenza: date | None = None
    data_scadenza_avviso: date | None = None
    testo_scadenza: str | None = None
    importo: float
    causale: str | None = None
    importi: list[ImportoRead]
    
class ISoggetto(BaseModel):
    tipo: Literal["F", "G"]
    codice: str
    nome: str | None
    cognome: str | None
    denominazione: str | None = None
    indirizzo: str | None = None
    civico: str | None = None
    cap: str | None = None
    loc: str | None = None
    prov: str | None = None
    nazione: str | None = None
    email: str | None

from datetime import datetime, timedelta
import json
import uuid
import httpx
import jwt
from typing import Any, Optional
from gisweb_pagopaschema.schemas import ISettingsPagoPa, IChiaveDebito, PagamentoCreate, PagamentoUpdate
from pydantic import BaseModel, Field

class JppaLoginResponse(BaseModel):
    descrizione_errore: str | None = Field(None, alias="descrizioneErrore")
    esito: str | None = None
    token: str | None = None

class PagoPaClient:
    
    _config:ISettingsPagoPa
    _token: str

    def __init__(self, config:ISettingsPagoPa):
        self._config = config
        self._token = ""
        self._client = httpx.AsyncClient()
        
    async def _ensure_token(self):
        tk = None
        try:
            tk = jwt.decode(self._token, options={"verify_signature": False})
        except :
            pass
        
        if not tk:
            await self._login()
            
    async def _login(self):
        config = self._config
        req = dict(
            idMessaggio=str(uuid.uuid4()),
            identificativoEnte=config.codiceIpa,
            username=config.wsUser,
            password=config.wsPassword,
        )
        
        data = await self._post(
            "/login",
            req,
            auth=False,  # niente token durante il login
        )

        res = JppaLoginResponse.model_validate(data)
        if not res.token:
            raise Exception(f"Login fallita: {res.descrizione_errore}")

        print (res.token)
        self._token = res.token


    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        if self._token:
            h["Authorization"] = f"Bearer {self._token}"
        return h
    
    async def _request(self, method, path, json=None, auth=True):
        url = f"{self._config.wsUrl}{path}"

        # 1) se l'endpoint richiede auth e abbiamo un token → prova la request
        headers = {}
        if auth and self._token:
            headers["Authorization"] = f"Bearer {self._token}"
            
        resp = await self._client.request(method, url, json=json, headers=headers)

        # 2) se ottieni 401 e hai provato solo "una" volta → rifai login e ritenta
        if resp.status_code == 401 and auth:
            # rifai login
            await self._login()

            # aggiorna header
            headers = {"Authorization": f"Bearer {self._token}"}

            # secondo e ultimo tentativo
            resp = await self._client.request(method, url, json=json, headers=headers)

            # 3) se ancora 401 → ERRORE
            if resp.status_code == 401:
                raise Exception("Autenticazione Maggioli fallita anche dopo il login.")

        resp.raise_for_status()
        return resp.json() if resp.content else None

    
    async def _post(self, path: str, json=None, auth=True):
        return await self._request("POST", path, json=json, auth=auth)

    async def _patch(self, path: str, json=None, auth=True):
        return await self._request("PATCH", path, json=json, auth=auth)

    async def aclose(self):
        await self._client.aclose()
        
 
    #async def creaAvvisoPagamento(self, soggetto: ISoggetto, debito: IDebito, testXml:bool=True):
 
 
    async def infoPagamento(self, deb:IChiaveDebito):
        
        config = self._config
        payload=dict(
            chiaveDebitoDto=dict(
                codiceTipoDebito=deb.codice,
                iDeb=deb.iddeb,
                iPos=deb.idpos
            ),
            codIpaRichiedente= config.codiceIpa,
            codiceServizio= config.codiceServizio
        ) 
        
        data = await self._post(path="/pagamenti/v2/infoPerDovuto", json=payload)

        return data
 
  
    async def notificaPagamento(self, data: Any) -> PagamentoUpdate | None:
        """
        Faccio solo il parser della notifica per trasformarla in un oggetto che rispetta l'iterfaccia del pagamento
        
        :param self: Description
        :param payload: Description
        :type payload: dict[str, Any]
        """
        
        if data.get("listaInfoPagamentoTelematicoDto") and len(data.get("listaInfoPagamentoTelematicoDto"))>0:
            res = data.get("listaInfoPagamentoTelematicoDto")[0]
            return PagamentoUpdate(
                iddeb=data.get("chiaveDebitoDto").get("iDeb"),
                idpos=data.get("chiaveDebitoDto").get("iPos"),
                stato=res.get("statoTecnicoPagamento"),
                esito=res.get("esitoRichiestaPagamento"),
                pagato=res.get("importoTotalePagato"),
                data_pagamento=datetime.strptime(str(res.get("dataPagamento")) , '%Y-%m-%d').date(),
            )
        
        
    
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
    # ------------------------------
    # AvvisiPagamento: infoPerNumeroAvviso
    # ------------------------------
    async def info_per_numero_avviso(
        self,
        cod_ipa: str,
        codice_servizio: str,
        numero_avviso: str,
    ):
        req = dict(
            cod_ipa_richiedente=cod_ipa,
            codice_servizio=codice_servizio,
            numero_avviso_dto={"numeroAvviso": numero_avviso},
        )

        data = await self._post(
            "/avvisiPagamento/v2/infoPerNumeroAvviso",
            req,
        )

        return data
    
    
    
    
    
    





    
    
    async def info_per_iuv(
        self,
        numero_avviso: str,
        cod_ipa: str="c_e463",
        codice_servizio: str="GISWEB",
    ):
        payload  = {
            "codIpaRichiedente": cod_ipa,
            "codiceIpaCreditore": cod_ipa,
            "codiceServizio": codice_servizio,
            "iuv": numero_avviso
        }
        data = await self._post("/pagamenti/v2/infoPerIuv", payload)
        return data
    

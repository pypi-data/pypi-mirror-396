
# type: ignore
from calendar import c
from typing import Any
import logging
import base64
import json
from datetime import datetime, date
from pydantic import BaseModel, HttpUrl
from jinja2 import Environment, PackageLoader, select_autoescape
import httpx
from .schema import IConfigPagoPa, IChiaveDebito, ISoggetto, IDebito, IEsito

_logger = logging.getLogger('gisweb-jppa')

env = Environment(
    loader=PackageLoader("gisweb_jppa"),
    autoescape=select_autoescape()
)

class JppaClient:
    
    config:IConfigPagoPa
  
    def __init__(self, config:IConfigPagoPa):
        self.config = config
        
    async def pagamentoOnline(self, soggetto: ISoggetto, debito: IDebito, notificaOK: str, notificaKO: str, testXml:bool=True):
        
        config  = self.config
        
        template = env.get_template("Soggetto.xml")
        xml_soggetto = template.render(soggetto)
                
        template = env.get_template("Debito.xml")
        context = debito.model_copy(update=dict(soggetto=xml_soggetto))
        xml_debito = template.render(context)
        
        template = env.get_template("PagaDebiti.xml")
        context = dict(
            idPagamento=debito.iddeb,
            soggetto=xml_soggetto,
            debito=xml_debito,
            notifica_ok=notificaOK, 
            notifica_ko=notificaKO, 
            notifica_pagamento=config.notificaPagamento,
        )
        
        xml_paga_debiti = template.render(context)
        
        if testXml:
            return xml_paga_debiti
        
        return await self.__serviceCall(Operazione="PagaDebiti", xml = xml_paga_debiti)
        
            
    async def PagamentoAvviso(self, soggetto: ISoggetto, debito: IDebito, testXml:bool=True):
        
        template = env.get_template("Soggetto.xml")
        xml_soggetto = template.render(soggetto)
                
        template = env.get_template("Debito.xml")
        context = debito.model_copy(update=dict(soggetto=xml_soggetto))
        xml_debito = template.render(context)
        
        template = env.get_template("CreaAvvisoPagamento.xml")
        xml_avviso = template.render(dict(debito = xml_debito))
        
        if testXml:
            return xml_avviso
        
        return await self.__serviceCall(Operazione="CreaAvvisoPagamento", xml = xml_avviso)
        
    
    async def eliminaAvvisoPagamento(self, numero_avviso:str):
        template = env.get_template("EliminaAvvisoPagamento.xml")
        xml = template.render(dict(numero_avviso = numero_avviso))
        return await self.__serviceCall(Operazione="EliminaAvvisoPagamento", xml = xml)


    async def getChiaveDebito(self, xml_response: str):
        soup = BeautifulSoup(xml_response, 'xml')
        ret = await self.parseResponse(soup.find('DatiDettaglioRichiesta').string)
        return IChiaveDebito(idpos=ret.get('IDPos'), iddeb=ret.get('IDDeb'), codice=ret.get('CodiceTipoDebito'))
        
    async def infoPagamento(self, deb:IChiaveDebito):
        template = env.get_template("InfoPagamentoDebito.xml")
        xml = template.render(deb)
        return await self.__serviceCall(Operazione='InfoPagamentoDebito',xml=xml)

    async def infoAvvisoPagamento(self, deb:IChiaveDebito):
        template = env.get_template("InfoAvvisoPagamentoPerChiaveDebito.xml")
        xml = template.render(deb)
        return await self.__serviceCall(Operazione='InfoAvvisoPagamentoPerChiaveDebito',xml=xml)

    async def ricevutaPagamento(self, deb:IChiaveDebito):
        template = env.get_template("InfoPagamentoDebito.xml")
        xml = template.render(deb)
        xml_ret = await self.__serviceCall(Operazione='InfoPagamentoDebito',xml=xml, raw=True)
        soup = BeautifulSoup(xml_ret, 'xml')
        return soup.find('FlussoRicevuta').string
    
    
    async def wsdlNotifica(self):
        template = env.get_template("wsdl_notifica.xml")
        return template.render(dict(url=self.config.notificaPagamento))

    async def rispostaNotificaPagamento(self, esito:IEsito):
        
        template = env.get_template("SoapResponse.xml")
        context = dict(
            codice_ipa = self.config.codiceIpa, 
            today = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            esito = esito.esito,
            messaggio = esito.messaggio
        )
        return template.render(context)

    
    async def stampaAvvisoPagamento(self, deb:IChiaveDebito, numero_avviso:str):
        
        logo = await self.file_to_base64_async(self.config.logoUrl)
        if not logo:
            return {"esito":"ERROR","message":"Stampa avvisatura fallita, manca il logo"}
            
        chiaviDebito = dict(
            codiceIpaEnte=self.config.codiceIpa,
            codiceServizio=self.config.codiceServizio,
            codiceTipoDebito=deb.codice,
            idDebito=deb.iddeb,
            idPosizione=deb.idpos,
        )
        
        data = dict(
            authKeyDto = dict(username=self.config.wsUser,password=self.config.wsPassword),
            base64FileLogoEnte = logo,
            numeroAvviso = numero_avviso,
            testoInformativaCanaliDigitali = "ff sf asdf asdf asd fasdf asd f",
            chiaviDebito = chiaviDebito
        )

        async with httpx.AsyncClient() as client:
            response =  await client.post(self.config.wsPrintUrl, data = json.dumps(data), headers = {'Content-type': 'application/json; charset=utf-8'})
            if response.status_code == httpx.codes.OK:
                try:
                    return response.json()
                except:
                    return {"errore":"SSSSSSSSSSSS"}
            else:
                return {"errore":"SSSSSSSSSSSS"}
        

    
    
    async def file_to_base64_async(self, url:HttpUrl):
        try:
            async with httpx.AsyncClient() as client:
                # Scarica il file in modalità asincrona
                response = await client.get(url)
                response.raise_for_status()  # Solleva un'eccezione per errori HTTP

                # Converte il contenuto in Base64
                file_content = response.content
                encoded_base64 = base64.b64encode(file_content).decode('utf-8')

                return encoded_base64
            
        except httpx.RequestError as e:
            print(f"Errore durante il download del file: {e}")
            return None
            
    
    
    
    
    
    
    
    
    
    async def __serviceCall(self, Operazione:str, xml:str, raw:bool = False):# -> IEsito:
        """
        chiamata base al servizio JPPA
        """

        config = self.config
        data_richiesta =  datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') 

        template = env.get_template("serviceCall.xml")
        xml = template.render(
            operazione=Operazione, 
            content=xml, 
            data=data_richiesta, 
            codice_ipa=config.codiceIpa, 
            codice_servizio=config.codiceServizio
        )
        
        print (xml)
        
        
        headers={'Content-type': 'text/plain; charset=utf-8'}
                
        async with httpx.AsyncClient() as client:
            
            response = await client.post(config.wsUrl, content=xml, headers=headers)
            soup = BeautifulSoup(response.text, 'xml')
                     
            if soup.find('EsitoOperazione').string == "ERROR":
                try:
                    return {"esito":soup.find('EsitoOperazione').string, "errore":soup.find('Codice').string, "descrizione":soup.find('Descrizione').string}
                except:
                    print(response.text)
                    return {"esito":f"ERRORE NON GESTITO: {response.text}"}
                    #with open("./jppa_resp.xml", "a") as f:
                    #    f.write(response.text)
             
            elif soup.find('EsitoOperazione') and soup.find('DatiDettaglioRisposta'):
                if soup.find('EsitoOperazione').string == "OK":
                    if raw:
                        return soup.find('DatiDettaglioRisposta').string
                    else:
                        return await self.parseResponse(soup.find('DatiDettaglioRisposta').string)

     
            else:
                print(response.text)
                #with open("./jppa_resp.xml", "a") as f:
                #    f.write(response.text)
   
                return {"esito":"ERRORE NON GESTITO"}

                        
                
    async def parseResponse(self, xml:str):
        soup = BeautifulSoup(xml, 'xml') # memo xml tiene conto delle maiuscole lxml tutto minuscolo
        keys = ["IDPos","IDDeb","CodiceTipoDebito","Url","IdentificativoUnivocoVersamento","NumeroAvviso","TipoVersamento","StatoTecnicoPagamento",
                "CodiceParametro","ValoreParametro",
                "EsitoRichiestaPagamento","ImportoTotaleRichiesta","ImportoTotalePagato","DataPagamento","DataAccredito","tipoIdentificativoUnivoco",
                "codiceIdentificativoUnivoco","Nome","Cognome","RagioneSociale","Localita","Provincia","Nazione","Email"]
        dz=dict()
        for key in keys:
            if soup.find(key) and soup.find(key).string:
                dz[key] = soup.find(key).string

        return dz
    
    
 
    
    
    
  
     

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    async def provaXML(self):
        respOK='''
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <PagaDebitiResponse xmlns="http://schemi.informatica.maggioli.it/ws/pagopa/ServiziInterni">
            <CodiceIPA>c_h183</CodiceIPA>
            <IDOperazione>PagaDebiti</IDOperazione>
            <DataRisposta>2024-04-03T12:52:27.499+02:00</DataRisposta>
            <EsitoOperazionedd>OK</EsitoOperazione>
            <DatiDettaglioRisposta>&lt;RispostaPagaDebiti xmlns="http://schemi.informatica.maggioli.it/operations/jcgpagopa/1_2">
    &lt;Url>https://pspagopa.comune-online.it/jcitygov-pagopa/web/webpagopa/pagaCarrello?identTransazione=9c03ce84-c46b-4771-a763-f6298093100e&amp;amp;token=427212cb-671b-4b37-8529-318e6503facd&lt;/Url>
    &lt;IdentTransazione>9c03ce84-c46b-4771-a763-f6298093100e&lt;/IdentTransazione>
    &lt;Esito>
        &lt;Esito>OK&lt;/Esito>
    &lt;/Esito>
&lt;/RispostaPagaDebiti></DatiDettaglioRisposta>
        </PagaDebitiResponse>
    </soap:Body>
</soap:Envelope>
        '''
        
        respERRORE='''
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <PagaDebitiResponse xmlns="http://schemi.informatica.maggioli.it/ws/pagopa/ServiziInterni">
            <CodiceIPA>c_h183</CodiceIPA>
            <IDOperazione>PagaDebiti</IDOperazione>
            <DataRisposta>2024-04-03T13:29:30.775+02:00</DataRisposta>
            <EsitoOperazione>OK</EsitoOperazione>
            <DatiDettaglioRisposta>&lt;RispostaPagaDebiti xmlns="http://schemi.informatica.maggioli.it/operations/jcgpagopa/1_2">
    &lt;Url>https://pspagopa.comune-online.it/jcitygov-pagopa/web/webpagopa/pagaCarrello?identTransazione=ND&amp;amp;token=e83df496-7752-4ba6-a594-3a0e3fbb471e&lt;/Url>
    &lt;IdentTransazione>ND&lt;/IdentTransazione>
    &lt;Esito>
        &lt;Esito>Error&lt;/Esito>
        &lt;Messaggio>[I193_ERR_DATI_ACCERTAMENTO_INCONSISTENTI] I dati di accertamento non sono coerenti. Verificare che la somma degli importi specificati nell'oggetto &amp;lt;DettagliImporto&amp;gt; coincida con il valore dell'importo specificato nell'oggetto &amp;lt;DettaglioDebito&amp;gt;.&lt;/Messaggio>
    &lt;/Esito>
&lt;/RispostaPagaDebiti></DatiDettaglioRisposta>
        </PagaDebitiResponse>
    </soap:Body>
</soap:Envelope>
        '''
        
        Operazione = "PagaDebiti"
        soup = BeautifulSoup(respOK, 'xml')
        esito = soup.find("EsitoOperazione") and soup.find("EsitoOperazione").string
        if esito == 'OK':
            respXml = soup.find('DatiDettaglioRisposta').string
            soupresp = BeautifulSoup(respXml, 'xml')
            print(soupresp)
        elif esito == 'ERROR':
            print('ddddddd')
            
        
           

                
        
                


        
         
  





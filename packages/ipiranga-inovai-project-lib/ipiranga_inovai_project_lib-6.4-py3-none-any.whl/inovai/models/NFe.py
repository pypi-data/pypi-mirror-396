from inovai.models.NFeBoleto import NFeBoleto
from inovai.models.NFeDocRef import NFeDocRef
from inovai.models.NFeDuplicata import NFeDuplicata
from inovai.models.NFeEnvioXML import NFeEnvioXML
from inovai.models.NFeEnvolvido import NFeEnvolvido
from inovai.models.NFeExportacao import NFeExportacao
from inovai.models.NFeFatura import NFeFatura
from inovai.models.NFeImpostoRetido import NFeImpostoRetido
from inovai.models.NFeIntermediadorTransacao import NFeIntermediadorTransacao
from inovai.models.NFeItem import NFeItem
from inovai.models.NFeObservacao import NFeObservacao
from inovai.models.NFePagamento import NFePagamento
from inovai.models.NFeProcReferenciado import NFeProcReferenciado
from inovai.models.NFeTransporte import NFeTransporte

from inovai.utils.util import format_date


class NFe:
    boletos: [NFeBoleto]
    chaveAcesso: str
    cnpjMovimentacao: str
    codFilial: str
    codHolding: str
    codMatriz: str
    compraContrato: str
    compraEmpenho: str
    compraPedido: str
    contingenciaDataHora: str
    contingenciaJustificativa: str
    dadosAdicionais: str
    dadosAdicionaisFisco: str
    dadosObservacao: [NFeObservacao]
    dataFechadia: str
    dataFiscal: str
    destinatario: NFeEnvolvido
    destino: int
    docNum: str
    documentosRef: [NFeDocRef]
    dthEmissao: str
    dthSaiEnt: str
    duplicatas: [NFeDuplicata]
    eConsumidor: bool
    emitente: NFeEnvolvido
    enviosXML: [NFeEnvioXML]
    exportacao: NFeExportacao
    fatura: NFeFatura
    finalidade: str
    idNfEntrada: str
    impostosRetidos: [NFeImpostoRetido]
    intermediadorTransacao: NFeIntermediadorTransacao
    itens: [NFeItem]
    localEntrega: NFeEnvolvido
    localRetirada: NFeEnvolvido
    modelo: str
    municipioCodigoIBGEISS: str
    natopCodigo: str
    natopDescricao: str
    numero: int
    numeroAleatorio: str
    pagamento: NFePagamento
    possuiIntermediario: bool
    prerecebimentoDtHrSinc: str
    processoReferenciado: NFeProcReferenciado
    protocoloDataHora: str
    protocoloNumero: str
    serie: str
    situacaoNF: str
    statusTransmissao: str
    tentativaTransmissao: float
    tipoDoc: str
    tipoEmissao: str
    tipoNota: str
    tipoPresOperador: str
    transporte: NFeTransporte
    transporteModFrete: str
    ultimaAtualizacaoStatus: str
    valorBCICMS: float
    valorBCICMSMonoRetencao: float
    valorBCICMSMonoRetido: float
    valorBCICMSMonofasico: float
    valorBCICMSST: float
    valorBaseCOFINS: float
    valorBaseINSS: float
    valorBaseISSRet: float
    valorBasePIS: float
    valorBaseReduICMS: float
    valorBaseTributIPI: float
    valorBaseTributISS: float
    valorCOFINS: float
    valorDesconto: float
    valorFCP: float
    valorFCPST: float
    valorFCPSTRet: float
    valorFCPUFDest: float
    valorFrete: float
    valorICMS: float
    valorICMSDeson: float
    valorICMSMonoRetencao: float
    valorICMSMonoRetido: float
    valorICMSMonofasico: float
    valorICMSST: float
    valorII: float
    valorIPI: float
    valorIPIDevol: float
    valorISS: float
    valorISSRet: float
    valorMercadoria: float
    valorNotaFiscal: float
    valorOutros: float
    valorPIS: float
    valorRetBCIRRF: float
    valorRetBCPrev: float
    valorRetCOFINS: float
    valorRetCSLL: float
    valorRetIRRF: float
    valorRetPIS: float
    valorRetPrev: float
    valorSeguro: float
    valorTotalTrib: float
    categoriaEstab: str

    def __init__(self, **json):
        if json:
            for key, typeProp in self.__class__.__dict__['__annotations__'].items():
                # str, float, bool, int
                class_name = str(typeProp).split("'")[1].split(".")[-1]

                if key in json:
                    if isinstance(typeProp, list):
                        cls = globals()[class_name]
                        items = []
                        for item_data in json[key]:
                            item = cls(**item_data)
                            items.append(item)
                        setattr(self, key, items)
                    elif class_name not in ('str', 'int', 'float', 'bool'):
                        cls = globals()[class_name]
                        instance = cls(**json[key])
                        setattr(self, key, instance)
                    else:
                        setattr(self, key, str(json[key]))
                else:
                    if isinstance(typeProp, list):
                        # cls = globals()[class_name]
                        items = []
                        setattr(self, key, items)
                    elif class_name not in ('str', 'int', 'float', 'bool'):
                        cls = globals()[class_name]
                        instance = cls()
                        setattr(self, key, instance)
                    else:
                        setattr(self, key, '')
        else:
            for key, typeProp in self.__class__.__dict__['__annotations__'].items():
                class_name = str(typeProp).split("'")[1].split(".")[-1]
                if isinstance(typeProp, list):
                    # cls = globals()[class_name]
                    items = []
                    setattr(self, key, items)
                elif class_name not in ('str', 'int', 'float', 'bool'):
                    cls = globals()[class_name]
                    instance = cls()
                    setattr(self, key, instance)
                else:
                    setattr(self, key, '')

    def get_boletos(self):
        return self.boletos

    def get_chaveAcesso(self):
        return self.chaveAcesso

    def get_cnpjMovimentacao(self):
        return self.cnpjMovimentacao

    def get_codFilial(self):
        return self.codFilial

    def get_codHolding(self):
        return self.codHolding

    def get_codMatriz(self):
        return self.codMatriz

    def get_compraContrato(self):
        return self.compraContrato

    def get_compraEmpenho(self):
        return self.compraEmpenho

    def get_compraPedido(self):
        return self.compraPedido

    def get_contingenciaDataHora(self):
        return self.contingenciaDataHora

    def get_contingenciaJustificativa(self):
        return self.contingenciaJustificativa

    def get_dadosAdicionais(self):
        return self.dadosAdicionais

    def get_dadosAdicionaisFisco(self):
        return self.dadosAdicionaisFisco

    def get_dadosObservacao(self):
        return self.dadosObservacao

    def get_dataFechadia(self):
        return self.dataFechadia

    def get_dataFiscal(self):
        return self.dataFiscal

    def get_destinatario(self):
        return self.destinatario

    def get_destino(self):
        return self.destino

    def get_docNum(self):
        return self.docNum

    def get_documentosRef(self):
        return self.documentosRef

    def get_dthEmissao(self):
        return format_date(self.dthEmissao)

    def get_dthSaiEnt(self):
        return format_date(self.dthSaiEnt)

    def get_duplicatas(self):
        return self.duplicatas

    def get_eConsumidor(self):
        return self.eConsumidor

    def get_emitente(self):
        return self.emitente

    def get_enviosXML(self):
        return self.enviosXML

    def get_exportacao(self):
        return self.exportacao

    def get_fatura(self):
        return self.fatura

    def get_finalidade(self):
        return self.finalidade

    def get_idNfEntrada(self):
        return self.idNfEntrada

    def get_impostosRetidos(self):
        return self.impostosRetidos

    def get_intermediadorTransacao(self):
        return self.intermediadorTransacao

    def get_itens(self):
        return self.itens

    def get_localEntrega(self):
        return self.localEntrega

    def get_localRetirada(self):
        return self.localRetirada

    def get_modelo(self):
        return self.modelo

    def get_natopCodigo(self):
        return self.natopCodigo

    def get_natopDescricao(self):
        return self.natopDescricao

    def get_numero(self):
        return self.numero

    def get_numeroAleatorio(self):
        return self.numeroAleatorio

    def get_pagamento(self):
        return self.pagamento

    def get_possuiIntermediario(self):
        return self.possuiIntermediario

    def get_prerecebimentoDtHrSinc(self):
        return self.prerecebimentoDtHrSinc

    def get_processoReferenciado(self):
        return self.processoReferenciado

    def get_protocoloDataHora(self):
        return self.protocoloDataHora

    def get_protocoloNumero(self):
        return self.protocoloNumero

    def get_serie(self):
        return self.serie

    def get_situacaoNF(self):
        return self.situacaoNF

    def get_statusTransmissao(self):
        return self.statusTransmissao

    def get_tentativaTransmissao(self):
        return self.tentativaTransmissao

    def get_tipoDoc(self):
        return self.tipoDoc

    def get_tipoEmissao(self):
        return self.tipoEmissao

    def get_tipoNota(self):
        return self.tipoNota

    def get_tipoPresOperador(self):
        return self.tipoPresOperador

    def get_transporte(self):
        return self.transporte

    def get_transporteModFrete(self):
        return self.transporteModFrete

    def get_ultimaAtualizacaoStatus(self):
        return self.ultimaAtualizacaoStatus

    def get_valorBCICMS(self):
        return self.valorBCICMS

    def get_valorBCICMSMonoRetencao(self):
        return self.valorBCICMSMonoRetencao

    def get_valorBCICMSMonoRetido(self):
        return self.valorBCICMSMonoRetido

    def get_valorBCICMSMonofasico(self):
        return self.valorBCICMSMonofasico

    def get_valorBCICMSST(self):
        return self.valorBCICMSST

    def get_valorBaseCOFINS(self):
        return self.valorBaseCOFINS

    def get_valorBaseINSS(self):
        return self.valorBaseINSS

    def get_valorBaseISSRet(self):
        return self.valorBaseISSRet

    def get_valorBasePIS(self):
        return self.valorBasePIS

    def get_valorBaseReduICMS(self):
        return self.valorBaseReduICMS

    def get_valorBaseTributIPI(self):
        return self.valorBaseTributIPI

    def get_valorBaseTributISS(self):
        return self.valorBaseTributISS

    def get_valorCOFINS(self):
        return self.valorCOFINS

    def get_valorDesconto(self):
        return self.valorDesconto

    def get_valorFCP(self):
        return self.valorFCP

    def get_valorFCPST(self):
        return self.valorFCPST

    def get_valorFCPSTRet(self):
        return self.valorFCPSTRet

    def get_valorFCPUFDest(self):
        return self.valorFCPUFDest

    def get_valorFrete(self):
        return self.valorFrete

    def get_valorICMS(self):
        return self.valorICMS

    def get_valorICMSDeson(self):
        return self.valorICMSDeson

    def get_valorICMSMonoRetencao(self):
        return self.valorICMSMonoRetencao

    def get_valorICMSMonoRetido(self):
        return self.valorICMSMonoRetido

    def get_valorICMSMonofasico(self):
        return self.valorICMSMonofasico

    def get_valorICMSST(self):
        return self.valorICMSST

    def get_valorII(self):
        return self.valorII

    def get_valorIPI(self):
        return self.valorIPI

    def get_valorIPIDevol(self):
        return self.valorIPIDevol

    def get_valorISS(self):
        return self.valorISS

    def get_valorISSRet(self):
        return self.valorISSRet

    def get_valorMercadoria(self):
        return self.valorMercadoria

    def get_valorNotaFiscal(self):
        return self.valorNotaFiscal

    def get_valorOutros(self):
        return self.valorOutros

    def get_valorPIS(self):
        return self.valorPIS

    def get_valorRetBCIRRF(self):
        return self.valorRetBCIRRF

    def get_valorRetBCPrev(self):
        return self.valorRetBCPrev

    def get_valorRetCOFINS(self):
        return self.valorRetCOFINS

    def get_valorRetCSLL(self):
        return self.valorRetCSLL

    def get_valorRetIRRF(self):
        return self.valorRetIRRF

    def get_valorRetPIS(self):
        return self.valorRetPIS

    def get_valorRetPrev(self):
        return self.valorRetPrev

    def get_valorSeguro(self):
        return self.valorSeguro

    def get_valorTotalTrib(self):
        return self.valorTotalTrib

    def get_categoriaEstab(self):
        return self.categoriaEstab

    def get_municipioCodigoIBGEISS(self):
        return self.municipioCodigoIBGEISS

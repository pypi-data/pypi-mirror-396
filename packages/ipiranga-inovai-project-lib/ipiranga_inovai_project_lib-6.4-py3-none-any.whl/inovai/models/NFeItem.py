from inovai.models.NFeDadosAtivos import NFeDadosAtivos
from inovai.models.NFeDocImportacao import NFeDocImportacao
from inovai.models.NFeImposto import NFeImposto
from inovai.models.NFeItemDadosCombustivel import NFeItemDadosCombustivel
from inovai.models.NFeItemExportacao import NFeItemExportacao
from inovai.models.NFeObservacaoItem import NFeObservacaoItem
import xml.etree.ElementTree as ET


class NFeItem:
    DIs: [NFeDocImportacao]
    cBarra: str
    cBarraTrib: str
    cEAN: str
    cEANTrib: str
    cest: str
    cfop: str
    codBeneficioFiscal: str
    codConta: str
    codFisJuridicaRef: str
    codigoServLei116: str
    descricaoLei116: str
    dadosCombustivel: NFeItemDadosCombustivel
    dadosExportacao: [NFeItemExportacao]
    dadosObservacaoItem: [NFeObservacaoItem]
    exTIPI: str
    impostos: [NFeImposto]
    impostosDevolvidos: [NFeImposto]
    indFisJuridicaRef: int
    indProduto: str
    indTipoReferencia: str
    item: int
    nbm: str
    ncm: str
    numItemRef: int
    numeroFCI: str
    nve: str
    pedidoExternoItem: int
    pedidoExternoNumero: str
    percentualDevolvido: float
    produtoCodigo: str
    produtoInfo: str
    produtoNome: str
    qtdDevolucaoRef: float
    quantidade: float
    quantidadeTrib: float
    unidadeMedida: str
    unidadeMedidaTrib: str
    valorDesconto: float
    valorDespAduaneira: float
    valorFrete: float
    valorIOF: float
    valorOutros: float
    valorSeguro: float
    valorTotal: float
    valorTotalTrib: float
    valorUnitario: float
    valorUnitarioTrib: float
    dadosAtivos: [NFeDadosAtivos]
    indNaturezaFrete: str
    codNaturezaReceita: str
    indNaturezaBaseCredito: str
    indLocalExecucaoServ: str

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

    def get_dadosAtivos(self):
        return self.dadosAtivos

    def get_DIs(self):
        return self.DIs

    def get_cBarra(self):
        return self.cBarra

    def get_cBarraTrib(self):
        return self.cBarraTrib

    def get_cEAN(self):
        return self.cEAN

    def get_cEANTrib(self):
        return self.cEANTrib

    def get_cest(self):
        return self.cest

    def get_cfop(self):
        return self.cfop

    def get_codBeneficioFiscal(self):
        return self.codBeneficioFiscal

    def get_codConta(self):
        return self.codConta

    def get_codFisJuridicaRef(self):
        return self.codFisJuridicaRef

    def get_codigoServLei116(self):
        return self.codigoServLei116

    def get_dadosCombustivel(self):
        return self.dadosCombustivel

    def get_dadosExportacao(self):
        return self.dadosExportacao

    def get_dadosObservacaoItem(self):
        return self.dadosObservacaoItem

    def get_exTIPI(self):
        return self.exTIPI

    def get_impostos(self):
        return self.impostos

    def get_impostosDevolvidos(self):
        return self.impostosDevolvidos

    def get_indFisJuridicaRef(self):
        return self.indFisJuridicaRef

    def get_indProduto(self):
        return self.indProduto

    def get_indTipoReferencia(self):
        return self.indTipoReferencia

    def get_item(self):
        return self.item

    def get_nbm(self):
        return self.nbm

    def get_ncm(self):
        return self.ncm

    def get_numItemRef(self):
        return self.numItemRef

    def get_numeroFCI(self):
        return self.numeroFCI

    def get_nve(self):
        return self.nve

    def get_pedidoExternoItem(self):
        return self.pedidoExternoItem

    def get_pedidoExternoNumero(self):
        return self.pedidoExternoNumero

    def get_percentualDevolvido(self):
        return self.percentualDevolvido

    def get_produtoCodigo(self):
        return self.produtoCodigo

    def get_produtoInfo(self):
        return self.produtoInfo

    def get_produtoNome(self):
        return self.produtoNome

    def get_qtdDevolucaoRef(self):
        return self.qtdDevolucaoRef

    def get_quantidade(self):
        return self.quantidade

    def get_quantidadeTrib(self):
        return self.quantidadeTrib

    def get_unidadeMedida(self):
        return self.unidadeMedida

    def get_unidadeMedidaTrib(self):
        return self.unidadeMedidaTrib

    def get_valorDesconto(self):
        return self.valorDesconto

    def get_valorDespAduaneira(self):
        return self.valorDespAduaneira

    def get_valorFrete(self):
        return self.valorFrete

    def get_valorIOF(self):
        return self.valorIOF

    def get_valorOutros(self):
        return self.valorOutros

    def get_valorSeguro(self):
        return self.valorSeguro

    def get_valorTotal(self):
        return self.valorTotal

    def get_valorTotalTrib(self):
        return self.valorTotalTrib

    def get_valorUnitario(self):
        return self.valorUnitario

    def get_valorUnitarioTrib(self):
        return self.valorUnitarioTrib

    def get_descricaoLei116(self):
        return self.descricaoLei116

    def to_xml(self, template):
        element = ET.Element(template.get('root', 'DET_NITEM'))

        for attr, tag in template.get('fields', {}).items():
            value = getattr(self, attr, None)
            if value is not None:
                child = ET.SubElement(element, tag)
                child.text = str(value)

        return element

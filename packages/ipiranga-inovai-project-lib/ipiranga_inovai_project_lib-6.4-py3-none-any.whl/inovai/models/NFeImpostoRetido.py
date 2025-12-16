class NFeImpostoRetido:
    tipo: str
    aliquota: float
    anoCompetencia: float
    codDarf: str
    codReceita: str
    codTributo: str
    dataFatoGerador: str
    dataFimCompetencia: str
    dataIniCompetencia: str
    dataPagamento: str
    dataVencto: str
    espTributo: str
    mesCompetencia: float
    numAp: str
    observacao: str
    valorBruto: float
    valorBase: float
    valorDedINSSTerceiro: float
    valorIRRetido: float
    codOperacao: str
    vlrDeducao: float
    indTipoQuitacao: str
    vlrPrevPrivada: str
    item: int
    vlrPensAliment: float
    vlrSalarioFam: float
    vlrAposentIsenta: float
    vlrAjudaCusto: float
    vlrPensInvalid: float
    vlrLucroPj: float
    vlrOutrosSocio: float
    vlrOutrosDirf: float
    vlrDedDepTerc: float
    vlrOutrosTribExcl: float
    vlrSalario13: float
    vlrTributo13: float
    vlrVoluntarioCopa: float
    vlrVoluntarioCopa13: float
    vlrBolsaMedicoResid: float
    vlrBolsaMedicoResid13: float
    vlrDepJud: float
    vlrPgTitular: float
    vlrFapi: float
    vlrFunpresp: float
    vlrContrib: float
    valorDeducaoIrExigSuspenso: float
    percentualScp: float
    vlrAposentIsenta13: float
    indNatRec: str
    indFisJur: str
    indCondPjDecl: str
    vlrJurosMora: float
    vlrResgPrevCompl: float
    vlrRendSRetIr: float
    codServicoNatRend: str
    dataEscrituracaoContabil: str

    # campos para as taxas específicas (CSLL, PIS, COFINS, IRRF)
    valorTributo: float
    valorBaseExigSuspenso: float
    valorRetencaoNefeIrrf: float
    valorDepositoJudicial: float

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

    def get_aliquota(self):
        return self.aliquota

    def get_anoCompetencia(self):
        return self.anoCompetencia

    def get_codDarf(self):
        return self.codDarf

    def get_codReceita(self):
        return self.codReceita

    def get_codTributo(self):
        return self.codTributo

    def get_dataFatoGerador(self):
        return self.dataFatoGerador

    def get_dataFimCompetencia(self):
        return self.dataFimCompetencia

    def get_dataIniCompetencia(self):
        return self.dataIniCompetencia

    def get_dataPagamento(self):
        return self.dataPagamento

    def get_dataVencto(self):
        return self.dataVencto

    def get_espTributo(self):
        return self.espTributo

    def get_mesCompetencia(self):
        return self.mesCompetencia

    def get_numAp(self):
        return self.numAp

    def get_observacao(self):
        return self.observacao

    def get_valorBruto(self):
        return self.valorBruto

    def get_valorBase(self):
        return self.valorBase

    def get_valorDedINSSTerceiro(self):
        return self.valorDedINSSTerceiro

    def get_valorIRRetido(self):
        return self.valorIRRetido

    def get_codOperacao(self):
        return self.codOperacao

    def get_vlrDeducao(self):
        return self.vlrDeducao

    def get_indTipoQuitacao(self):
        return self.indTipoQuitacao
    def get_tipo(self):
        return self.tipo

    def get_vlrPrevPrivada(self):
        return self.vlrPrevPrivada

    def get_item(self) -> int:
        return self.item

    def get_vlrPensAliment(self) -> float:
        return self.vlrPensAliment

    def get_vlrSalarioFam(self) -> float:
        return self.vlrSalarioFam

    def get_vlrAposentIsenta(self) -> float:
        return self.vlrAposentIsenta

    def get_vlrAjudaCusto(self) -> float:
        return self.vlrAjudaCusto

    def get_vlrPensInvalid(self) -> float:
        return self.vlrPensInvalid

    def get_vlrLucroPj(self) -> float:
        return self.vlrLucroPj

    def get_vlrOutrosSocio(self) -> float:
        return self.vlrOutrosSocio

    def get_vlrOutrosDirf(self) -> float:
        return self.vlrOutrosDirf

    def get_vlrDedDepTerc(self) -> float:
        return self.vlrDedDepTerc

    def get_vlrOutrosTribExcl(self) -> float:
        return self.vlrOutrosTribExcl

    def get_vlrSalario13(self) -> float:
        return self.vlrSalario13

    def get_vlrTributo13(self) -> float:
        return self.vlrTributo13

    def get_vlrVoluntarioCopa(self) -> float:
        return self.vlrVoluntarioCopa

    def get_vlrVoluntarioCopa13(self) -> float:
        return self.vlrVoluntarioCopa13

    def get_vlrBolsaMedicoResid(self) -> float:
        return self.vlrBolsaMedicoResid

    def get_vlrBolsaMedicoResid13(self) -> float:
        return self.vlrBolsaMedicoResid13

    def get_vlrDepJud(self) -> float:
        return self.vlrDepJud

    def get_vlrPgTitular(self) -> float:
        return self.vlrPgTitular

    def get_vlrFapi(self) -> float:
        return self.vlrFapi

    def get_vlrFunpresp(self) -> float:
        return self.vlrFunpresp

    def get_vlrContrib(self) -> float:
        return self.vlrContrib

    def get_valorDeducaoIrExigSuspenso(self) -> float:
        return self.valorDeducaoIrExigSuspenso

    def get_percentualScp(self) -> float:
        return self.percentualScp

    def get_vlrAposentIsenta13(self) -> float:
        return self.vlrAposentIsenta13

    def get_indNatRec(self) -> str:
        return self.indNatRec

    def get_indFisJur(self) -> str:
        return self.indFisJur

    def get_indCondPjDecl(self) -> str:
        return self.indCondPjDecl

    def get_vlrJurosMora(self) -> float:
        return self.vlrJurosMora

    def get_vlrResgPrevCompl(self) -> float:
        return self.vlrResgPrevCompl

    def get_vlrRendSRetIr(self) -> float:
        return self.vlrRendSRetIr

    def get_codServicoNatRend(self) -> str:
        return self.codServicoNatRend

    def get_dataEscrituracaoContabil(self) -> str:
        return self.dataEscrituracaoContabil

    # getters para taxas específicas
    def get_valorTributo(self) -> float:
        return self.valorTributo

    def get_valorBaseExigSuspenso(self) -> float:
        return self.valorBaseExigSuspenso

    def get_valorRetencaoNefeIrrf(self) -> float:
        return self.valorRetencaoNefeIrrf

    def get_valorDepositoJudicial(self) -> float:
        return self.valorDepositoJudicial
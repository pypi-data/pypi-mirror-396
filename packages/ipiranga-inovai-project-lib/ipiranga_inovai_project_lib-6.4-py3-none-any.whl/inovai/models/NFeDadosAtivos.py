class NFeDadosAtivos:
    codBem: str
    dataOperacao: str
    anoRegistroOperacao: str
    descricao: str
    valorCreditoICMS: str
    valorCredDifAliq: str
    tipoBem: str
    vidaUtil: str
    descricaoFuncao: str
    indUtilizacaoBem: str
    indNaturezaBem: str
    numMesesEstorno: str
    codContaAnaliticaBem: str
    identSituacaoBem: str
    indOpGeradoraCredito: str
    codGrupoBem: str
    descGrupoBem: str
    dataLancamento: str
    indOrigemCredito: str
    indUtilizacaoBem: str
    valorDepreciAmortiza: str
    valorBaseCreditoPisPasep: str
    indNumeroParcela: str
    codSituacaoPis: str
    valorBasePis: str
    aliquotaPis: str
    valorPis: str
    codSituacaoCofins: str
    valorBaseCofins: str
    aliquotaCofins: str
    valorCofins: str

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_codBem(self):
        return self.codBem

    def get_dataOperacao(self):
        return self.dataOperacao

    def get_anoRegistroOperacao(self):
        return self.anoRegistroOperacao

    def get_descricao(self):
        return self.descricao

    def get_valorCreditoICMS(self):
        return self.valorCreditoICMS

    def get_valorCredDifAliq(self):
        return self.valorCredDifAliq

    def get_tipoBem(self):
        return self.tipoBem

    def get_vidaUtil(self):
        return self.vidaUtil

    def get_descricaoFuncao(self):
        return self.descricaoFuncao

    def get_indUtilizacaoBem(self):
        return self.indUtilizacaoBem

    def get_indNaturezaBem(self):
        return self.indNaturezaBem

    def get_numMesesEstorno(self):
        return self.numMesesEstorno

    def get_codContaAnaliticaBem(self):
        return self.codContaAnaliticaBem

    def get_identSituacaoBem(self):
        return self.identSituacaoBem

    def set_indOpGeradoraCredito(self):
        self.indOpGeradoraCredito

    def set_codGrupoBem(self):
        self.codGrupoBem

    def set_descGrupoBem(self):
        self.descGrupoBem

    def set_dataLancamento(self):
        self.dataLancamento

    def set_indOrigemCredito(self):
        self.indOrigemCredito

    def set_indUtilizacaoBem(self):
        self.indUtilizacaoBem

    def set_valorDepreciAmortiza(self):
        self.valorDepreciAmortiza

    def set_valorBaseCreditoPisPasep(self):
        self.valorBaseCreditoPisPasep

    def set_indNumeroParcela(self):
        self.indNumeroParcela

    def set_codSituacaoPis(self):
        self.codSituacaoPis

    def set_valorBasePis(self):
        self.valorBasePis

    def set_aliquotaPis(self):
        self.aliquotaPis

    def set_valorPis(self):
        self.valorPis

    def set_codSituacaoCofins(self):
        self.codSituacaoCofins

    def set_valorBaseCofins(self):
        self.valorBaseCofins

    def set_aliquotaCofins(self):
        self.aliquotaCofins

    def set_valorCofins(self):
        self.valorCofins

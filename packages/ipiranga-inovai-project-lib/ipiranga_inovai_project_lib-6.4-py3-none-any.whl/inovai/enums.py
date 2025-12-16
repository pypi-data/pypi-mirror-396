from enum import Enum, IntEnum


class DocumentStatus(Enum):
    INTEGRATED = 'INTEGRADO'
    PENDING_INTEGRATION = 'PENDENTE_INTEGRACAO'
    CONVERTER_ERROR = 'ERRO_CONVERSAO'


class DataIntegrationStatus(Enum):
    PENDING_INTEGRATION = 'PENDENTE_INTEGRACAO'
    PROCESSING = 'PROCESSANDO'
    SENT = 'ENVIADO'
    CONVERTER_ERROR = 'ERRO_CONVERSAO'
    VALIDATION_ERROR = 'ERRO_VALIDACAO'
    ERROR = "ERRO"
    INTEGRATED = 'INTEGRADO'


class BatchStatus(Enum):
    CREATED = 'CRIADO'
    SENT = 'ENVIADO'
    INTEGRATED = 'INTEGRADO'
    ERROR = 'ERRO'
    SENT_ERROR = 'ERRO_ENVIO'


class DocumentMovementType(Enum):
    INPUT = 'E',
    OUTPUT = 'S'


class ResponsibleMovement(Enum):
    ISSUER = 'EMITENTE'
    RECIPIENT = 'DESTINATARIO'


class Origin(Enum):
    JDE = "JDE"
    ABADI = "ABADI"


class DocumentType(Enum):
    SERVICE = 'SERV'
    PRODUCT = 'PROD'
    ISS_SERVICE = "SERV_ISS"


class IntegrationType(IntEnum):
    SERV = 1
    SERV_ISS = 2
    PROD = 3
    MOVIMENTACAO_ESTOQUE = 4
    PRODUTO_ACABADO_SEM_EMBALAGEM = 5
    PRODUTO_ACABADO_COM_EMBALAGEM = 6
    ORDEM_PRODUCAO_PROPRIA = 7
    ORDEM_PRODUCAO_TERCEIROS = 9
    CORRECAO_APONTAMENTO = 8
    DEFAULT = 999

    @classmethod
    def get_by_kit_id(cls, kit_id):
        if kit_id == KitId.ONE.value:
            return [cls.SERV, cls.SERV_ISS, cls.PROD]
        elif kit_id == KitId.THREE.value:
            return [
                cls.MOVIMENTACAO_ESTOQUE,
                cls.PRODUTO_ACABADO_SEM_EMBALAGEM,
                cls.PRODUTO_ACABADO_COM_EMBALAGEM,
                cls.ORDEM_PRODUCAO_PROPRIA,
                cls.ORDEM_PRODUCAO_TERCEIROS,
                cls.CORRECAO_APONTAMENTO
            ]
        else:
            return [cls.DEFAULT]


class TaxType(Enum):
    PIS = "PIS"
    IPI = "IPI"
    ISS = "ISS"
    INSS = "INSSRet"
    COFINS = "COFINS"
    ISSRET = "ISSRet"
    ICMS = "ICMS"
    ICMSST = "ICMSST"
    ICMSFCP = "ICMSFCP"
    ICMSFCPST = "ICMSFCPST"
    ICMSMONORETEN = "ICMSMONORETEN"
    ICMSMONOPROP = "ICMSMONOPROP"
    ICMSMONODIFER = "ICMSMONODIFER"
    ICMSMONORET = "ICMSMONORET"
    ICSL = "ICSL"
    IRRF = "IRRF"
    IPIS = 'IPIS'
    ICOF = 'ICOF'


class KitId(IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    SEVEN = 7
    EIGHT = 8
    NINE = 9

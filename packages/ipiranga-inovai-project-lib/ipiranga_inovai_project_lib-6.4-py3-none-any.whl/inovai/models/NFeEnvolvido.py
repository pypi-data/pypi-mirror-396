from inovai.models.Endereco import Endereco


class NFeEnvolvido:
    cnae: str
    cpfCNPJ: str
    email: str
    endereco: Endereco
    indContribuinte: int
    inscricaoEstadual: str
    inscricaoEstadualST: str
    inscricaoMunicipal: str
    nome: str
    pontoEntrega: str
    simplesNacional: str
    suframa: str
    tipoEnvolvido: str
    tipoInscricaoEstadual: str
    codInstalAnp: str

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

    def get_cnae(self):
        return self.cnae

    def get_cpfCNPJ(self):
        return self.cpfCNPJ

    def get_email(self):
        return self.email

    def get_endereco(self):
        return self.endereco

    def get_indContribuinte(self):
        return self.indContribuinte

    def get_inscricaoEstadual(self):
        return self.inscricaoEstadual

    def get_inscricaoEstadualST(self):
        return self.inscricaoEstadualST

    def get_inscricaoMunicipal(self):
        return self.inscricaoMunicipal

    def get_nome(self):
        return self.nome

    def get_pontoEntrega(self):
        return self.pontoEntrega

    def get_simplesNacional(self):
        return self.simplesNacional

    def get_suframa(self):
        return self.suframa

    def get_tipoEnvolvido(self):
        return self.tipoEnvolvido

    def get_tipoInscricaoEstadual(self):
        return self.tipoInscricaoEstadual

    def get_codInstalAnp(self):
        return self.codInstalAnp

    def to_xml(self, root_element):
        self.get_endereco().to_xml(root_element)

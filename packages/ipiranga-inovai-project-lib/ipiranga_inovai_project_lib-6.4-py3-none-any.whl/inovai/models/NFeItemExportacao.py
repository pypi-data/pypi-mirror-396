class NFeItemExportacao:
    codTipoConhecimentoTransp: str
    dataAverbacao: str
    dataDespacho: str
    dataEmbarque: str
    dataEmissaoNf: str
    dataRegistro: str
    expIndChave: str
    expIndNumReg: str
    expIndQtdEfet: float
    numeroDeclaracao: str
    numeroDrawback: str
    numeroRegistro: str
    paisDestino: str

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

    def get_codTipoConhecimentoTransp(self):
        return self.codTipoConhecimentoTransp

    def get_dataAverbacao(self):
        return self.dataAverbacao

    def get_dataDespacho(self):
        return self.dataDespacho

    def get_dataEmbarque(self):
        return self.dataEmbarque

    def get_dataEmissaoNf(self):
        return self.dataEmissaoNf

    def get_dataRegistro(self):
        return self.dataRegistro

    def get_expIndChave(self):
        return self.expIndChave

    def get_expIndNumReg(self):
        return self.expIndNumReg

    def get_expIndQtdEfet(self):
        return self.expIndQtdEfet

    def get_numeroDeclaracao(self):
        return self.numeroDeclaracao

    def get_numeroDrawback(self):
        return self.numeroDrawback

    def get_numeroRegistro(self):
        return self.numeroRegistro

    def get_paisDestino(self):
        return self.paisDestino

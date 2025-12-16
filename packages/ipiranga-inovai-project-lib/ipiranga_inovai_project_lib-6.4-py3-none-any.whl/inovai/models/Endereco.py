import xml.etree.ElementTree as ET


class Endereco:
    bairro: str
    cep: str
    complemento: str
    logradouro: str
    municipioCodigoIBGE: str
    municipioNome: str
    numero: str
    paisCodigoIBGE: str
    paisNome: str
    telefone: str
    uf: str

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
    def __repr__(self):
        return f'Enderço ({", ".join(f"{key}={value}" for key, value in self.__dict__.items())})'

    def get_bairro(self):
        return self.bairro

    def get_cep(self):
        return self.cep

    def get_complemento(self):
        return self.complemento

    def get_logradouro(self):
        return self.logradouro

    def get_municipioCodigoIBGE(self):
        if len(str(self.municipioCodigoIBGE)) > 5: # TODO tirar isso dps de alinhamento com tributos
            return str(self.municipioCodigoIBGE)[2:7]
        return str(self.municipioCodigoIBGE)

    def get_municipioNome(self):
        return self.municipioNome

    def get_numero(self):
        return self.numero

    def get_paisCodigoIBGE(self):
        return self.paisCodigoIBGE

    def get_paisNome(self):
        return self.paisNome

    def get_telefone(self):
        return self.telefone

    def get_uf(self):
        return self.uf

    def to_xml(self, root_element):
        modelo_element = ET.SubElement(root_element, 'UF_ORIG_DEST')
        modelo_element.text = self.get_uf()

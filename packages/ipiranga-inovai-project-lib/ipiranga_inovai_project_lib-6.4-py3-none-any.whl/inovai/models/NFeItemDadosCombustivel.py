from inovai.models.NFeItemOrigemCombustivel import NFeItemOrigemCombustivel
class NFeItemDadosCombustivel:
	cProdANP: str
	codif: str
	descANP: str
	origemCombustivel: [NFeItemOrigemCombustivel]
	percentualBioDiesel: float
	percentualGLP: float
	qtdAmbiente: float
	ufConsumo: str

	def __init__(self, **json):
		if json:
			for key, typeProp in self.__class__.__dict__['__annotations__'].items():
				class_name = str(typeProp).split("'")[1].split(".")[-1]

				if key in json:
					if isinstance(typeProp, list):
						cls = globals()[class_name]
						items = []
						initial_value = json[key]
						if isinstance(initial_value, dict):
							initial_value = [initial_value]
						for item_data in initial_value:
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
					items = []
					setattr(self, key, items)
				elif class_name not in ('str', 'int', 'float', 'bool'):
					cls = globals()[class_name]
					instance = cls()
					setattr(self, key, instance)
				else:
					setattr(self, key, '')

	def get_cProdANP(self):
		return self.cProdANP

	def get_codif(self):
		return self.codif

	def get_descANP(self):
		return self.descANP

	def get_origemCombustivel(self):
		return self.origemCombustivel

	def get_percentualBioDiesel(self):
		return self.percentualBioDiesel

	def get_percentualGLP(self):
		return self.percentualGLP

	def get_qtdAmbiente(self):
		return self.qtdAmbiente

	def get_ufConsumo(self):
		return self.ufConsumo

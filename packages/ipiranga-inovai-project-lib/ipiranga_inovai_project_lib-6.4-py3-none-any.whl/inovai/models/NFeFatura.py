class NFeFatura:
	numero: str
	valorDesconto: float
	valorLiquido: float
	valorOriginal: float
	indFatura: str

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

	def get_numero(self):
		return self.numero

	def get_valorDesconto(self):
		return self.valorDesconto

	def get_valorLiquido(self):
		return self.valorLiquido

	def get_valorOriginal(self):
		return self.valorOriginal

	def get_indFatura(self):
		return self.indFatura

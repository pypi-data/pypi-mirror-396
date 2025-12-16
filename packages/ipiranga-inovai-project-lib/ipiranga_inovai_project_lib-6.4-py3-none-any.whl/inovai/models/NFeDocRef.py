class NFeDocRef:
	anoMes: str
	chaveAcesso: str
	dataFiscal: str
	emitenteCPFCNPJ: str
	emitenteIE: str
	numero: int
	serie: int
	tipo: str
	ufCodIBGE: str

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

	def get_anoMes(self):
		return self.anoMes

	def get_chaveAcesso(self):
		return self.chaveAcesso

	def get_dataFiscal(self):
		return self.dataFiscal

	def get_emitenteCPFCNPJ(self):
		return self.emitenteCPFCNPJ

	def get_emitenteIE(self):
		return self.emitenteIE

	def get_numero(self):
		return self.numero

	def get_serie(self):
		return self.serie

	def get_tipo(self):
		return self.tipo

	def get_ufCodIBGE(self):
		return self.ufCodIBGE

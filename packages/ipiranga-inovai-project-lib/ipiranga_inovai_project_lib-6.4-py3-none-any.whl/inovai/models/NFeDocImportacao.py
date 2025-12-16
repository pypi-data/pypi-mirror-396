from inovai.models.NFeDocImportacaoAdicao import NFeDocImportacaoAdicao
from inovai.models.NFeEnvolvido import NFeEnvolvido
from inovai.models.NFeOrigem import NFeOrigem
class NFeDocImportacao:
	adicoes: [NFeDocImportacaoAdicao]
	codigoExportador: str
	dataRegistro: str
	desembaracoData: str
	desembaracoLocal: str
	desembaracoUF: str
	intermediario: NFeEnvolvido
	numero: str
	origem: NFeOrigem
	quantidadeUnidadeComercializacao: int
	quantidadeUnidadeMedida: int
	tipoDocumentoImportacao: int
	tipoIntermediario: int
	valorDespesasAcrescidas: float
	valorDespesasAduaneiras: float
	valorMarinhaMercante: float
	viaTransporte: int

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

	def get_adicoes(self):
		return self.adicoes

	def get_codigoExportador(self):
		return self.codigoExportador

	def get_dataRegistro(self):
		return self.dataRegistro

	def get_desembaracoData(self):
		return self.desembaracoData

	def get_desembaracoLocal(self):
		return self.desembaracoLocal

	def get_desembaracoUF(self):
		return self.desembaracoUF

	def get_intermediario(self):
		return self.intermediario

	def get_numero(self):
		return self.numero

	def get_origem(self):
		return self.origem

	def get_quantidadeUnidadeComercializacao(self):
		return self.quantidadeUnidadeComercializacao

	def get_quantidadeUnidadeMedida(self):
		return self.quantidadeUnidadeMedida

	def get_tipoDocumentoImportacao(self):
		return self.tipoDocumentoImportacao

	def get_tipoIntermediario(self):
		return self.tipoIntermediario

	def get_valorDespesasAcrescidas(self):
		return self.valorDespesasAcrescidas

	def get_valorDespesasAduaneiras(self):
		return self.valorDespesasAduaneiras

	def get_valorMarinhaMercante(self):
		return self.valorMarinhaMercante

	def get_viaTransporte(self):
		return self.viaTransporte

class NFeImposto:
	aliquota: str
	aliquotaConsumidorFinal: float
	aliquotaICMSEfetivo: float
	aliquotaICMSMonoRetencao: str
	cfop: int
	cst: str
	enquadramento: str
	indIcmsST: str
	indVlrIcmsCobrancaAnteriorST: str
	modalidadeBaseCalc: int
	motivoDesoneracao: int
	motivoReducaoADRem: int
	municipioCodigoIBGE: str
	origem: str
	percentualDifer: float
	percentualFCPDifer: float
	percentualMVAST: float
	percentualPartilha: float
	percentualReducaoADRem: float
	percentualReducaoBC: float
	percentualReducaoBCEfetivo: float
	somaCOFINSST: bool
	somaPISST: bool
	tipo: str
	tipoRegimeImposto: int
	valor: float
	valorAliqICMSSubstituto: float
	valorBC: float
	valorBCDest: float
	valorBCEfetivo: float
	valorBCICMSMonoRetencao: float
	valorBaseICMSReducao: float
	valorBaseICMSSubstituto: float
	valorDesoneracao: float
	valorDest: float
	valorFCPICMSDiferido: float
	valorFCPICMSEfetivo: float
	valorICMSDiferido: float
	valorICMSEfetivo: float
	valorICMSMonoRetencao: float
	valorICMSSubstituto: float
	valorSemDifer: float
	valorUnitario: float
	valorDifAliquota: str = ''
	vlrIcmsNaoDestacado: str = ''

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
		return f'NFe({", ".join(f"{key}={value}" for key, value in self.__dict__.items())})'

	def get_aliquota(self):
		return self.aliquota

	def get_aliquotaConsumidorFinal(self):
		return self.aliquotaConsumidorFinal

	def get_aliquotaICMSEfetivo(self):
		return self.aliquotaICMSEfetivo

	def get_aliquotaICMSMonoRetencao(self):
		return self.aliquotaICMSMonoRetencao

	def get_cfop(self):
		return self.cfop

	def get_cst(self):
		return self.cst

	def get_enquadramento(self):
		return self.enquadramento

	def get_indIcmsST(self):
		return self.indIcmsST

	def get_indVlrIcmsCobrancaAnteriorST(self):
		return self.indVlrIcmsCobrancaAnteriorST

	def get_modalidadeBaseCalc(self):
		return self.modalidadeBaseCalc

	def get_motivoDesoneracao(self):
		return self.motivoDesoneracao

	def get_motivoReducaoADRem(self):
		return self.motivoReducaoADRem

	def get_municipioCodigoIBGE(self):
		return self.municipioCodigoIBGE

	def get_origem(self):
		return self.origem

	def get_percentualDifer(self):
		return self.percentualDifer

	def get_percentualFCPDifer(self):
		return self.percentualFCPDifer

	def get_percentualMVAST(self):
		return self.percentualMVAST

	def get_percentualPartilha(self):
		return self.percentualPartilha

	def get_percentualReducaoADRem(self):
		return self.percentualReducaoADRem

	def get_percentualReducaoBC(self):
		return self.percentualReducaoBC

	def get_percentualReducaoBCEfetivo(self):
		return self.percentualReducaoBCEfetivo

	def get_somaCOFINSST(self):
		return self.somaCOFINSST

	def get_somaPISST(self):
		return self.somaPISST

	def get_tipo(self):
		return self.tipo

	def get_tipoRegimeImposto(self):
		return self.tipoRegimeImposto

	def get_valor(self):
		return self.valor

	def get_valorAliqICMSSubstituto(self):
		return self.valorAliqICMSSubstituto

	def get_valorBC(self):
		return self.valorBC

	def get_valorBCDest(self):
		return self.valorBCDest

	def get_valorBCEfetivo(self):
		return self.valorBCEfetivo

	def get_valorBCICMSMonoRetencao(self):
		return self.valorBCICMSMonoRetencao

	def get_valorBaseICMSReducao(self):
		return self.valorBaseICMSReducao

	def get_valorBaseICMSSubstituto(self):
		return self.valorBaseICMSSubstituto

	def get_valorDesoneracao(self):
		return self.valorDesoneracao

	def get_valorDest(self):
		return self.valorDest

	def get_valorFCPICMSDiferido(self):
		return self.valorFCPICMSDiferido

	def get_valorFCPICMSEfetivo(self):
		return self.valorFCPICMSEfetivo

	def get_valorICMSDiferido(self):
		return self.valorICMSDiferido

	def get_valorICMSEfetivo(self):
		return self.valorICMSEfetivo

	def get_valorICMSMonoRetencao(self):
		return self.valorICMSMonoRetencao

	def get_valorICMSSubstituto(self):
		return self.valorICMSSubstituto

	def get_valorSemDifer(self):
		return self.valorSemDifer

	def get_valorUnitario(self):
		return self.valorUnitario

	def get_valorDifAliquota(self):
		return self.valorDifAliquota
	def get_vlrIcmsNaoDestacado(self):
		return self.vlrIcmsNaoDestacado

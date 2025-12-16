class NFeBoleto:
	agenciaDepositaria: str
	bairro: str
	cep: str
	cnpj: str
	codDepNumDoc: str
	codDepNumDocParc: str
	codigoEmpresa: str
	codigoEmpresaReduzido: str
	codigoLocalCobranca: str
	conteudoCampoAceite: str
	controleAtualizRegTX: str
	data: str
	dataVencimento: str
	enderecoCobr: str
	especieNotaFiscal: str
	linhaDigitavelBoleto: str
	linhaFormatadaBoleto: str
	localPagamento: str
	mensagem1: str
	mensagem2: str
	mensagem3: str
	mensagem4: str
	mensagem5: str
	mensagem6: str
	mensagem7: str
	mensagem8: str
	msg: str
	municipio: str
	nomeCliente: str
	nomeLocalCobranca: str
	numeroBoleto: str
	parametroMascara: str
	quantidadeURV: float
	tipoMoeda: str
	uf: str
	usoBancario: str
	valorAbatimentoTitulo: float
	valorCobranca: float
	valorDocumento: float
	valorMoraMulta: float
	valorOutrasDeducoes: float
	valorOutrosAcrescimos: float
	valorURV: float

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

	def get_agenciaDepositaria(self):
		return self.agenciaDepositaria

	def get_bairro(self):
		return self.bairro

	def get_cep(self):
		return self.cep

	def get_cnpj(self):
		return self.cnpj

	def get_codDepNumDoc(self):
		return self.codDepNumDoc

	def get_codDepNumDocParc(self):
		return self.codDepNumDocParc

	def get_codigoEmpresa(self):
		return self.codigoEmpresa

	def get_codigoEmpresaReduzido(self):
		return self.codigoEmpresaReduzido

	def get_codigoLocalCobranca(self):
		return self.codigoLocalCobranca

	def get_conteudoCampoAceite(self):
		return self.conteudoCampoAceite

	def get_controleAtualizRegTX(self):
		return self.controleAtualizRegTX

	def get_data(self):
		return self.data

	def get_dataVencimento(self):
		return self.dataVencimento

	def get_enderecoCobr(self):
		return self.enderecoCobr

	def get_especieNotaFiscal(self):
		return self.especieNotaFiscal

	def get_linhaDigitavelBoleto(self):
		return self.linhaDigitavelBoleto

	def get_linhaFormatadaBoleto(self):
		return self.linhaFormatadaBoleto

	def get_localPagamento(self):
		return self.localPagamento

	def get_mensagem1(self):
		return self.mensagem1

	def get_mensagem2(self):
		return self.mensagem2

	def get_mensagem3(self):
		return self.mensagem3

	def get_mensagem4(self):
		return self.mensagem4

	def get_mensagem5(self):
		return self.mensagem5

	def get_mensagem6(self):
		return self.mensagem6

	def get_mensagem7(self):
		return self.mensagem7

	def get_mensagem8(self):
		return self.mensagem8

	def get_msg(self):
		return self.msg

	def get_municipio(self):
		return self.municipio

	def get_nomeCliente(self):
		return self.nomeCliente

	def get_nomeLocalCobranca(self):
		return self.nomeLocalCobranca

	def get_numeroBoleto(self):
		return self.numeroBoleto

	def get_parametroMascara(self):
		return self.parametroMascara

	def get_quantidadeURV(self):
		return self.quantidadeURV

	def get_tipoMoeda(self):
		return self.tipoMoeda

	def get_uf(self):
		return self.uf

	def get_usoBancario(self):
		return self.usoBancario

	def get_valorAbatimentoTitulo(self):
		return self.valorAbatimentoTitulo

	def get_valorCobranca(self):
		return self.valorCobranca

	def get_valorDocumento(self):
		return self.valorDocumento

	def get_valorMoraMulta(self):
		return self.valorMoraMulta

	def get_valorOutrasDeducoes(self):
		return self.valorOutrasDeducoes

	def get_valorOutrosAcrescimos(self):
		return self.valorOutrosAcrescimos

	def get_valorURV(self):
		return self.valorURV

from inovai.models.NFeEnvolvido import NFeEnvolvido
from inovai.models.NFeImposto import NFeImposto
from inovai.models.NFeVeiculo import NFeVeiculo
from inovai.models.NFeVolume import NFeVolume
class NFeTransporte:
	contratoTransporte: str
	icmsRetido: NFeImposto
	modal: int
	transportador: NFeEnvolvido
	valorServico: float
	veiculos: [NFeVeiculo]
	volumes: [NFeVolume]

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

	def get_contratoTransporte(self):
		return self.contratoTransporte

	def get_icmsRetido(self):
		return self.icmsRetido

	def get_modal(self):
		return self.modal

	def get_transportador(self):
		return self.transportador

	def get_valorServico(self):
		return self.valorServico

	def get_veiculos(self):
		return self.veiculos

	def get_volumes(self):
		return self.volumes

from wagtail.search.backends.elasticsearch7 import Elasticsearch7SearchBackend
from django.db import connection

class CustomElasticsearch7SearchBackend(Elasticsearch7SearchBackend):
	def __init__(self, params):
		print("✅ USANDO BACKEND CUSTOMIZADO COM get_indexed_fields()")
		super().__init__(params)

	def prepare_document(self, obj):
		try:
			# Usa a propriedade diretamente
			fields = {
				"pk": obj.pk,
				"body": getattr(obj, "body", ""),  # aqui acessa o @property
				"content_type": str(obj.content_type),
			}
			print(f"📦 Indexando via @property body: {obj.pk} - {obj.title}")
			# FECHA CONEXÃO AQUI!
			connection.close()
			return fields
		except Exception as e:
			print(f"💥 Erro preparando documento para {obj.pk}: {e}")
			connection.close()  # FECHA MESMO COM ERRO
			return super().prepare_document(obj)

	def get_searchable_fields(self, model):
		if hasattr(model, "get_indexed_fields"):
			return ["_dummy"]
		return super().get_searchable_fields(model)

	def index(self, model, obj):
		print(f"⚙️ Indexando: {model.__name__} ID={obj.pk}")
		result = super().index(model, obj)
		connection.close()  # FECHA AQUI TAMBÉM
		return result
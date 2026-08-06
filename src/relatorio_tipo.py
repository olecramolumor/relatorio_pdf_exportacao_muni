from dataclasses import dataclass

@dataclass
class RequisicaoRelatorio:
    modo: str
    ano: int
    valor_recorte: str | None = None
    logo: bool = True

    @property
    def nome_arquivo(self):
        if self.modo == "ano":
            return f"Relatório Exportação - Rondônia - {self.ano}"

        return f"Relatório Exportação - {self.valor_recorte} - {self.ano}"

    def parametros(self):
        return {
            "modo": self.modo,
            "nome_arquivo": self.nome_arquivo,
            "ano": self.ano,
            "valor_recorte": self.valor_recorte,
            "logo": self.logo,
        }
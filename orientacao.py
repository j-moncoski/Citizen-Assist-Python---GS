"""Classe Orientacao: representa UM registro da base de conhecimento (um item do JSON).

Responsabilidade: guardar os dados de uma orientação e exibi-la na tela.
"""

AVISO = "este assistente NÃO é um canal oficial."

# Campos que todo registro do JSON precisa ter (e o tipo esperado de cada um)
CAMPOS_OBRIGATORIOS = {
    "id": int,
    "categoria": str,
    "titulo": str,
    "palavras_chave": list,
    "resposta": str,
    "documentos": list,
    "onde": str,
    "fonte": str,
    "verificado_em": str,
}


class Orientacao:
    """Uma orientação ao cidadão (ex.: como habilitar a Carteira de Trabalho Digital)."""

    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave
        self.resposta = resposta
        self.documentos = documentos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    @classmethod
    def de_dicionario(cls, dados):
        """Cria uma Orientacao a partir de um dicionário do JSON.

        Levanta ValueError se faltar campo ou se o tipo estiver errado,
        para que a BaseConhecimento possa ignorar o registro ruim sem travar.
        """
        if not isinstance(dados, dict):
            raise ValueError("registro não é um dicionário")
        for campo, tipo in CAMPOS_OBRIGATORIOS.items():
            if campo not in dados:
                raise ValueError(f"campo ausente: {campo}")
            if not isinstance(dados[campo], tipo):
                raise ValueError(f"campo '{campo}' com tipo inválido")
        return cls(**{campo: dados[campo] for campo in CAMPOS_OBRIGATORIOS})

    def exibir(self):
        """Mostra a orientação na tela, sempre com fonte, data e aviso."""
        print(f"\n>> {self.titulo}  [{self.categoria}]")
        print(self.resposta)
        if self.documentos:
            print("Documentos necessários:")
            for documento in self.documentos:
                print(f"  - {documento}")
        else:
            print("Documentos necessários: nenhum documento específico.")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print(f"Aviso: {AVISO}")

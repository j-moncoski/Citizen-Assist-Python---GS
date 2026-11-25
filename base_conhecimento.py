"""Classe BaseConhecimento: o conjunto de todas as orientações.

Responsabilidade: ler o JSON, listar as categorias e buscar a melhor orientação
usando uma busca por regras com pontuação.
"""

import json

from orientacao import Orientacao

# ---------------------------------------------------------------- regras de pontuação
PONTOS_PALAVRA_CHAVE = 3   # palavra-chave da orientação que aparece na pergunta
PONTOS_TITULO = 1          # palavra da pergunta (4+ letras) que aparece no título
LIMITE_ALTA = 6            # 6 pontos ou mais -> confiança ALTA
LIMITE_MEDIA = 3           # 3 a 5 pontos -> confiança MÉDIA (abaixo disso: não encontrei)

# Palavras comuns que não ajudam a achar o assunto (evitam pontos "falsos" pelo título).
STOPWORDS = {
    "como", "para", "onde", "qual", "quais", "quando", "quero", "preciso",
    "fazer", "posso", "minha", "meu", "sobre", "essa", "esse", "pela", "pelo",
    "tenho", "isso", "algum", "alguma", "saber", "ajuda", "dúvida", "duvida",
}

# ---------------------------------------------------------------- normalização
ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "ä": "a",
           "é": "e", "è": "e", "ê": "e", "ë": "e",
           "í": "i", "ì": "i", "î": "i", "ï": "i",
           "ó": "o", "ò": "o", "õ": "o", "ô": "o", "ö": "o",
           "ú": "u", "ù": "u", "û": "u", "ü": "u", "ç": "c"}

# Sinais trocados por espaço (além dos da especificação, tratamos hífen, barra e º/ª)
SINAIS = "?!.,;:()-/\"'º ª"


def normalizar(texto):
    """Minúsculas, sem acentos, sem pontuação e com espaço no começo e no fim.

    Os espaços nas pontas permitem achar PALAVRAS inteiras com `in`:
    " sus " está em " como faco cartao do sus ", mas não em " ensus ".
    """
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in SINAIS:
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


def nivel_confianca(pontos):
    """Converte pontos em nível de confiança: 'ALTA', 'MÉDIA' ou None."""
    if pontos >= LIMITE_ALTA:
        return "ALTA"
    if pontos >= LIMITE_MEDIA:
        return "MÉDIA"
    return None


class BaseConhecimento:
    """Carrega o JSON e responde: quais categorias existem? qual a melhor orientação?"""

    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []   # lista de objetos Orientacao (composição)

    # ------------------------------------------------------------ leitura do JSON
    def carregar(self):
        """Lê o JSON e cria os objetos Orientacao.

        Arquivo ausente, corrompido ou com registros ruins NÃO trava o programa:
        mostra um aviso e segue com o que for possível. Devolve True se achou
        pelo menos uma orientação válida.
        """
        self.orientacoes = []
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            print(f"Aviso: base de conhecimento não encontrada em '{self.caminho}'.")
            return False
        except (json.JSONDecodeError, UnicodeDecodeError):
            print(f"Aviso: o arquivo '{self.caminho}' está corrompido (JSON inválido).")
            return False
        except OSError as erro:
            print(f"Aviso: não foi possível abrir a base de conhecimento ({erro}).")
            return False

        if not isinstance(dados, list):
            print("Aviso: a base deve ser uma lista de dicionários.")
            return False

        ignorados = 0
        for registro in dados:
            try:
                self.orientacoes.append(Orientacao.de_dicionario(registro))
            except ValueError:
                ignorados += 1
        if ignorados:
            print(f"Aviso: {ignorados} registro(s) inválido(s) foram ignorados.")
        if not self.orientacoes:
            print("Aviso: nenhuma orientação válida foi carregada.")
        return bool(self.orientacoes)

    # ------------------------------------------------------------ categorias
    def categorias(self):
        """Lista as categorias, sem repetir, na ordem em que aparecem."""
        lista = []
        for orientacao in self.orientacoes:
            if orientacao.categoria not in lista:
                lista.append(orientacao.categoria)
        return lista

    def por_categoria(self, categoria):
        """Devolve as orientações de uma categoria."""
        return [o for o in self.orientacoes if o.categoria == categoria]

    # ------------------------------------------------------------ busca por pontuação
    def pontuar(self, pergunta_normalizada, orientacao):
        """Calcula os pontos de UMA orientação para a pergunta já normalizada.

        +3 por palavra-chave que aparece na pergunta;
        +1 por palavra da pergunta (4+ letras, fora as STOPWORDS) que aparece no título.
        """
        pontos = 0

        palavras_chave = {normalizar(p) for p in orientacao.palavras_chave if p.strip()}
        for palavra_chave in palavras_chave:
            if palavra_chave in pergunta_normalizada:
                pontos += PONTOS_PALAVRA_CHAVE

        titulo = normalizar(orientacao.titulo)
        vistas = set()
        for palavra in pergunta_normalizada.split():
            if len(palavra) >= 4 and palavra not in STOPWORDS and palavra not in vistas:
                vistas.add(palavra)
                if f" {palavra} " in titulo:
                    pontos += PONTOS_TITULO
        return pontos

    def buscar(self, pergunta):
        """Devolve uma lista de tuplas (pontos, orientacao), da maior para a menor.

        Só entram orientações com pelo menos LIMITE_MEDIA (3) pontos. Lista vazia
        significa "não encontrei".
        """
        pergunta_normalizada = normalizar(pergunta)
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta_normalizada, orientacao)
            if pontos >= LIMITE_MEDIA:
                resultados.append((pontos, orientacao))
        # maior pontuação primeiro; em empate, menor id primeiro (resultado estável)
        resultados.sort(key=lambda tupla: (-tupla[0], tupla[1].id))
        return resultados

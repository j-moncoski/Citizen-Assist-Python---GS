"""Classe Assistente: quem conversa com o cidadão.

Responsabilidade: fazer o atendimento, guardar o histórico e calcular os indicadores.
Composição: Assistente --tem um--> BaseConhecimento --tem várias--> Orientacao.
"""

import csv
import json
import os
import time
from datetime import datetime

from base_conhecimento import nivel_confianca

CAMPOS_CSV = ["sessao", "data", "origem", "pergunta", "id_orientacao",
              "encontrou", "ajudou", "tentativas", "tempo_segundos",
              "nota_facilidade"]


def ler_texto(mensagem, padrao="0"):
    """input() que não quebra se a entrada acabar (Ctrl+D / pipe): devolve `padrao`."""
    try:
        return input(mensagem).strip()
    except EOFError:
        return padrao


def ler_opcao(mensagem, minimo, maximo):
    """Pede um número entre minimo e maximo e repete até ser válido.

    Letras, vazio e números fora da faixa nunca encerram o programa.
    """
    while True:
        resposta = ler_texto(mensagem, str(minimo))
        if resposta.isdecimal() and minimo <= int(resposta) <= maximo:
            return int(resposta)
        print(f"Opção inválida. Digite um número entre {minimo} e {maximo}.")


def ler_sim_nao(mensagem):
    """Pede 's' ou 'n' e repete até ser válido. Devolve True para 's'."""
    while True:
        resposta = ler_texto(mensagem, "n").lower()
        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "nao", "não"):
            return False
        print("Resposta inválida. Digite s (sim) ou n (não).")


def tem_dado_pessoal(texto):
    """Regra da GS: 8 ou mais dígitos, ou presença de '@', indica dado pessoal."""
    digitos = sum(1 for letra in texto if letra.isdigit())
    return digitos >= 8 or "@" in texto


class Assistente:
    """Atende o cidadão por pergunta livre ou por navegação em categorias."""

    def __init__(self, nome, base, caminho_historico=None, caminho_csv=None):
        self.nome = nome
        self.base = base            # objeto BaseConhecimento
        pasta = os.path.dirname(base.caminho) or "."
        self.caminho_historico = caminho_historico or os.path.join(pasta, "historico.json")
        self.caminho_csv = caminho_csv or os.path.join(pasta, "atendimentos.csv")
        self.sessao = datetime.now().strftime("%Y%m%d-%H%M%S")  # identifica esta execução
        self.historico = self._carregar_historico()

    # ------------------------------------------------------------ histórico em JSON
    def _carregar_historico(self):
        """Lê data/historico.json. Ausente ou corrompido não trava o programa."""
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            return []
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            print("Aviso: histórico ilegível; começando um histórico novo.")
            try:   # guarda uma cópia do arquivo ruim para não perder nada
                os.replace(self.caminho_historico, self.caminho_historico + ".corrompido")
            except OSError:
                pass
            return []
        if not isinstance(dados, list):
            return []
        return [item for item in dados if isinstance(item, dict)]

    def _salvar_historico(self):
        try:
            os.makedirs(os.path.dirname(self.caminho_historico) or ".", exist_ok=True)
            with open(self.caminho_historico, "w", encoding="utf-8") as arquivo:
                json.dump(self.historico, arquivo, ensure_ascii=False, indent=2)
        except OSError as erro:
            print(f"Aviso: não consegui salvar o histórico ({erro}).")

    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou,
                  tentativas, tempo_segundos):
        """Guarda um atendimento (um dicionário) no histórico e no arquivo JSON.

        Perguntas com dados pessoais nunca chegam aqui (são barradas antes).
        """
        atendimento = {
            "sessao": self.sessao,
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,                  # "pergunta" ou "categoria"
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,    # None se nada foi encontrado
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": tempo_segundos,
            "nota_facilidade": "",             # preenchida ao sair
        }
        self.historico.append(atendimento)
        self._salvar_historico()

    # ------------------------------------------------------------ atendimento por pergunta
    def perguntar(self):
        """Atendimento em texto livre: busca com pontuação, confiança e confirmação."""
        if not self.base.orientacoes:
            print("A base de conhecimento não está disponível no momento.")
            return

        inicio = time.time()
        tentativas = 0
        encontrou = False
        id_orientacao = None
        ultima_pergunta = ""

        while True:
            texto = ler_texto("\nDigite sua dúvida (0 para voltar): ")

            if texto == "":
                print("Atenção: a pergunta está vazia. Escreva sua dúvida ou digite 0.")
                continue
            if texto == "0":
                if tentativas > 0:   # saiu sem resolver: vira "dúvida sem solução"
                    self.registrar("pergunta", ultima_pergunta, id_orientacao, encontrou,
                                   False, tentativas, round(time.time() - inicio, 1))
                return
            if tem_dado_pessoal(texto):
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
                continue   # recusada e NÃO registrada

            tentativas += 1
            ultima_pergunta = texto
            resultados = self.base.buscar(texto)   # lista de tuplas (pontos, orientacao)

            if not resultados:
                print("\nNão encontrei uma orientação para essa dúvida.")
                print("Tente outras palavras (ex.: o nome do documento ou do serviço)")
                print("ou use a navegação por categorias: " + ", ".join(self.base.categorias()) + ".")
                continue

            encontrou = True
            pontos, melhor = resultados[0]
            alternativas = resultados[1:3]
            id_orientacao = melhor.id
            print(f"\nConfiança da resposta: {nivel_confianca(pontos)} ({pontos} pontos)")
            melhor.exibir()

            ajudou = ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
            if not ajudou:
                id_alternativa = self._oferecer_alternativas(alternativas)
                if id_alternativa is not None:
                    ajudou = True
                    id_orientacao = id_alternativa

            if ajudou:
                self.registrar("pergunta", ultima_pergunta, id_orientacao, True, True,
                               tentativas, round(time.time() - inicio, 1))
                # começa um atendimento novo
                inicio = time.time()
                tentativas = 0
                encontrou = False
                id_orientacao = None
                ultima_pergunta = ""
            else:
                print("Tudo bem. Reescreva a dúvida com outras palavras ou digite 0 para voltar.")

    def _oferecer_alternativas(self, alternativas):
        """Mostra até 2 orientações parecidas. Devolve o id da que ajudou, ou None."""
        if not alternativas:
            return None
        print("\nTalvez uma destas ajude:")
        for numero, (pontos, orientacao) in enumerate(alternativas, start=1):
            print(f"  {numero}. {orientacao.titulo} [{orientacao.categoria}] ({pontos} pontos)")
        print("  0. Nenhuma")
        escolha = ler_opcao("Qual você quer ver? ", 0, len(alternativas))
        if escolha == 0:
            return None
        orientacao = alternativas[escolha - 1][1]
        orientacao.exibir()
        if ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): "):
            return orientacao.id
        return None

    # ------------------------------------------------------------ navegação por categorias
    def navegar(self):
        """Lista categorias e orientações numeradas, com '0 para voltar' em todas as telas."""
        categorias = self.base.categorias()
        if not categorias:
            print("Não há categorias disponíveis.")
            return

        while True:
            print("\n=== Categorias ===")
            for numero, categoria in enumerate(categorias, start=1):
                print(f"{numero}. {categoria}")
            print("0. Voltar")
            escolha = ler_opcao("Escolha uma categoria: ", 0, len(categorias))
            if escolha == 0:
                return
            self._navegar_categoria(categorias[escolha - 1])

    def _navegar_categoria(self, categoria):
        orientacoes = self.base.por_categoria(categoria)
        while True:
            print(f"\n=== {categoria} ===")
            for numero, orientacao in enumerate(orientacoes, start=1):
                print(f"{numero}. {orientacao.titulo}")
            print("0. Voltar")
            escolha = ler_opcao("Escolha uma orientação: ", 0, len(orientacoes))
            if escolha == 0:
                return
            inicio = time.time()
            orientacao = orientacoes[escolha - 1]
            orientacao.exibir()
            ajudou = ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
            self.registrar("categoria", f"[{categoria}] {orientacao.titulo}", orientacao.id,
                           True, ajudou, 1, round(time.time() - inicio, 1))

    # ------------------------------------------------------------ indicadores
    def indicadores(self):
        """Calcula e exibe os indicadores a partir do histórico. Devolve um dicionário."""
        total = len(self.historico)
        if total == 0:
            print("\nAinda não há atendimentos registrados.")
            return {}

        encontrados = [h for h in self.historico if h.get("encontrou")]
        ajudados = [h for h in self.historico if h.get("ajudou")]
        tempos = [h.get("tempo_segundos", 0) for h in encontrados]
        tentativas = [h.get("tentativas", 1) for h in self.historico]

        # uma nota por sessão (cada execução do programa pede a nota uma vez)
        notas_por_sessao = {}
        for h in self.historico:
            nota = h.get("nota_facilidade")
            if isinstance(nota, int):
                notas_por_sessao[h.get("sessao")] = nota
        notas = list(notas_por_sessao.values())

        sem_solucao = []
        for h in self.historico:
            texto = h.get("pergunta", "")
            if not h.get("ajudou") and texto and texto not in sem_solucao:
                sem_solucao.append(texto)

        resultado = {
            "atendimentos": total,
            "resposta_encontrada_pct": round(100 * len(encontrados) / total, 1),
            "taxa_acerto_pct": round(100 * len(ajudados) / total, 1),
            "tempo_medio_s": round(sum(tempos) / len(tempos), 1) if tempos else None,
            "tentativas_media": round(sum(tentativas) / len(tentativas), 1),
            "facilidade_media": round(sum(notas) / len(notas), 1) if notas else None,
            "sem_solucao": sem_solucao,
        }

        print("\n=== Indicadores ===")
        print(f"Atendimentos registrados:   {resultado['atendimentos']}")
        print(f"Resposta encontrada (%):    {resultado['resposta_encontrada_pct']}")
        print(f"Taxa de acerto: ajudou (%): {resultado['taxa_acerto_pct']}")
        tempo = resultado["tempo_medio_s"]
        print(f"Tempo médio para encontrar: {tempo if tempo is not None else '-'} s")
        print(f"Tentativas por atendimento: {resultado['tentativas_media']}")
        facilidade = resultado["facilidade_media"]
        print(f"Facilidade de uso (1 a 5):  {facilidade if facilidade is not None else '-'}")
        print("Dúvidas sem solução:")
        if sem_solucao:
            for texto in sem_solucao:
                print(f"  - {texto}")
        else:
            print("  (nenhuma)")
        return resultado

    # ------------------------------------------------------------ CSV
    def exportar_csv(self):
        """Exporta todos os atendimentos para data/atendimentos.csv com csv.DictWriter."""
        try:
            os.makedirs(os.path.dirname(self.caminho_csv) or ".", exist_ok=True)
            with open(self.caminho_csv, "w", newline="", encoding="utf-8") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV,
                                          extrasaction="ignore", restval="")
                escritor.writeheader()
                for atendimento in self.historico:
                    escritor.writerow(atendimento)
        except OSError as erro:
            print(f"Aviso: não consegui exportar o CSV ({erro}).")
            return False
        print(f"CSV exportado: {len(self.historico)} atendimento(s) em '{self.caminho_csv}'.")
        return True

    # ------------------------------------------------------------ saída
    def encerrar(self):
        """Ao sair: pede a nota de facilidade (1 a 5), salva, exporta o CSV e mostra indicadores."""
        da_sessao = [h for h in self.historico if h.get("sessao") == self.sessao]
        if da_sessao:
            nota = ler_opcao("\nDe 1 a 5, quão fácil foi usar o assistente? ", 1, 5)
            for atendimento in da_sessao:
                atendimento["nota_facilidade"] = nota
            self._salvar_historico()
        self.exportar_csv()
        self.indicadores()

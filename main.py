"""Citizen Assist AI: assistente de orientação ao cidadão (GS 2026.2 - FIAP).

Público: jovens no primeiro emprego.
Execução: python main.py
"""

import os

from assistente import Assistente
from base_conhecimento import BaseConhecimento
from orientacao import AVISO

PASTA = os.path.dirname(os.path.abspath(__file__))   # funciona de qualquer diretório
CAMINHO_BASE = os.path.join(PASTA, "data", "base_conhecimento.json")


def mostrar_menu():
    print("\n===== MENU =====")
    print("1. Fazer uma pergunta")
    print("2. Navegar por categorias")
    print("3. Ver indicadores")
    print("4. Exportar atendimentos para CSV")
    print("0. Sair")


def main():
    base = BaseConhecimento(CAMINHO_BASE)
    base.carregar()          # lê o JSON e cria os objetos Orientacao

    assistente = Assistente("Citizen Assist AI", base)

    print(f"Bem-vindo(a) ao {assistente.nome}!")
    print("Oriento jovens no primeiro emprego: documentos, trabalho, direitos, saúde e consumo.")
    print(f"Aviso: {AVISO}")
    print("Não digite CPF, telefone, e-mail ou outros dados pessoais.")

    while True:
        mostrar_menu()
        try:
            opcao = input("Escolha uma opção: ").strip()
        except EOFError:
            opcao = "0"
        except KeyboardInterrupt:
            print()
            opcao = "0"

        if opcao == "1":
            assistente.perguntar()
        elif opcao == "2":
            assistente.navegar()
        elif opcao == "3":
            assistente.indicadores()
        elif opcao == "4":
            assistente.exportar_csv()
        elif opcao == "0":
            assistente.encerrar()
            print("\nAté logo!")
            break
        else:
            print("Opção inválida. Digite um número de 0 a 4.")


if __name__ == "__main__":
    main()

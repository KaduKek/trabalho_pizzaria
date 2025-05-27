import os
import pickle
import datetime
from typing import List, Dict, Optional
from pedido import Pedido, ItemPedido

class PedidoUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if name == "Pedido":
            return Pedido
        if name == "ItemPedido":
            return ItemPedido
        return super().find_class(module, name)
class ItemPedido:
    def __init__(self, tipo: str, nome: str, detalhes: Dict = None, quantidade: int = 1):
        self.tipo = tipo  # "pizza" ou "bebida"
        self.nome = nome
        self.detalhes = detalhes or {}  # Para pizzas: tamanho, adicionais, etc.
        self.quantidade = quantidade

    def __str__(self) -> str:
        if self.tipo == "pizza":
            adicionais = ", ".join(self.detalhes.get('adicionais', [])) if self.detalhes.get('adicionais') else "Nenhum"
            return f"{self.quantidade}x Pizza {self.nome} ({self.detalhes.get('tamanho', 'Média')}) - Adicionais: {adicionais}"
        else:
            return f"{self.quantidade}x {self.nome}"

class Pedido:
    def __init__(self, numero: int, cliente: str, itens: List[ItemPedido] = None,
                 observacoes: str = "", data_hora: datetime.datetime = None):
        self.numero = numero
        self.cliente = cliente
        self.itens = itens or []
        self.observacoes = observacoes
        self.data_hora = data_hora or datetime.datetime.now()
        self.status = "Pendente"
        self.tempo_preparo = self._calcular_tempo_preparo()

    def _calcular_tempo_preparo(self) -> int:
        """Calcula o tempo estimado de preparo em minutos"""
        tempo_total = 0
        
        for item in self.itens:
            if item.tipo == "pizza":
                tempo_base = {
                    "Pequena": 15,
                    "Média": 20,
                    "Grande": 25,
                    "Família": 30
                }
                tamanho = item.detalhes.get('tamanho', 'Média')
                tempo_pizza = tempo_base.get(tamanho, 20)
                # Adiciona 2 minutos para cada adicional
                tempo_pizza += len(item.detalhes.get('adicionais', [])) * 2
                tempo_total += tempo_pizza * item.quantidade
            else:
                # Bebidas levam 1 minuto para preparar
                tempo_total += 1 * item.quantidade
        
        return max(tempo_total, 10)  # Tempo mínimo de 10 minutos

    def calcular_valor_total(self, cardapio: Dict) -> float:
        """Calcula o valor total do pedido"""
        valor_total = 0
        
        for item in self.itens:
            if item.tipo == "pizza":
                if item.nome in cardapio["sabores"]:
                    tamanho = item.detalhes.get('tamanho', 'Média')
                    valor_base = cardapio["sabores"][item.nome]["preco"].get(tamanho, 0)
                    valor_adicionais = sum(cardapio["adicionais"].get(a, 0) 
                                         for a in item.detalhes.get('adicionais', []))
                    valor_item = (valor_base + valor_adicionais) * item.quantidade
                    valor_total += valor_item
            elif item.tipo == "bebida":
                if item.nome in cardapio["bebidas"]:
                    valor_item = cardapio["bebidas"][item.nome]["preco"] * item.quantidade
                    valor_total += valor_item
        
        return valor_total

    def __str__(self) -> str:
        itens_str = "; ".join(str(item) for item in self.itens)
        return (f"Pedido #{self.numero} | Cliente: {self.cliente} | "
                f"Itens: {itens_str} | Status: {self.status}")


class SistemaPizzaria:
    def __init__(self, arquivo_pedidos: str = "pedidos.pickle",
                 arquivo_cardapio: str = "cardapio.pickle"):
        self.arquivo_pedidos = arquivo_pedidos
        self.arquivo_cardapio = arquivo_cardapio
        self.fila_pedidos: List[Pedido] = []
        self.contador_pedidos: int = 1
        self.cardapio: Dict[str, Dict] = self._inicializar_cardapio()
        self.historico_pedidos: List[Pedido] = []
        self.carregar_dados()

    def _inicializar_cardapio(self) -> Dict:
        """Inicializa o cardápio base se não existir"""
        cardapio_padrao = {
            "sabores": {
                "Marguerita": {"ingredientes": ["Molho de tomate", "Muçarela", "Manjericão"], "preco": {"Pequena": 30, "Média": 40, "Grande": 52, "Família": 60}},
                "Calabresa": {"ingredientes": ["Molho de tomate", "Muçarela", "Calabresa", "Cebola"], "preco": {"Pequena": 32, "Média": 42, "Grande": 50, "Família": 62}},
                "Frango c/ Catupiry": {"ingredientes": ["Molho de tomate", "Muçarela", "Frango", "Catupiry"], "preco": {"Pequena": 35, "Média": 45, "Grande": 58, "Família": 65}},
                "Portuguesa": {"ingredientes": ["Molho de tomate", "Muçarela", "Presunto", "Ovos", "Cebola", "Ervilha"], "preco": {"Pequena": 38, "Média": 48, "Grande": 55, "Família": 68}},
                "Quatro Queijos": {"ingredientes": ["Molho de tomate", "Muçarela", "Parmesão", "Provolone", "Gorgonzola"], "preco": {"Pequena": 40, "Média": 50, "Grande": 60, "Família": 70}},
                "Presunto": {"ingredientes": ["Molho de tomate", "Presunto", "Muçarela", "Rodelas de tomate"], "preco": {"Pequena": 30, "Média": 35, "Grande": 45, "Família": 50}},
                "Bacon": {"ingredientes": ["Molho de tomate", "Muçarela", "Bacon", "Rodelas de tomate"], "preco": {"Pequena": 35, "Média": 45, "Grande": 55, "Família": 65}},
                "Napolitana": {"ingredientes": ["Molho de tomate", "Muçarela", "Rodelas de tomate", "Parmesão ralado"], "preco": {"Pequena": 40, "Média": 50, "Grande": 60, "Família": 70}}
            },
            "adicionais": {
                "Borda recheada": 8,
                "Catupiry extra": 5,
                "Cheddar extra": 5,
                "Bacon": 6,
                "Azeitona": 3,
                "Palmito": 7
            },
            "tamanhos": ["Pequena", "Média", "Grande", "Família"],
            "bebidas": {
                "Coca-Cola Lata": {"categoria": "Refrigerante", "preco": 6.00},
                "Pepsi Lata": {"categoria": "Refrigerante", "preco": 6.00},
                "Fanta Laranja Lata": {"categoria": "Refrigerante", "preco": 6.00},
                "Fanta Uva Lata": {"categoria": "Refrigerante", "preco": 6.00},
                "Suco de Laranja": {"categoria": "Suco Natural", "preco": 7.50},
                "Suco de Limão": {"categoria": "Suco Natural", "preco": 7.50},
                "Suco de Abacaxi": {"categoria": "Suco Natural", "preco": 7.50},
                "Suco de Maracujá": {"categoria": "Suco Natural", "preco": 7.50},
                "Água Mineral 500ml": {"categoria": "Água", "preco": 4.00},
                "Água com Gás 500ml": {"categoria": "Água", "preco": 4.00}
            }
        }
        return cardapio_padrao

    def salvar_dados(self) -> None:
        """Salva pedidos e cardápio em arquivos"""
        with open(self.arquivo_pedidos, "wb") as f:
            dados = {
                "fila_pedidos": self.fila_pedidos,
                "contador_pedidos": self.contador_pedidos,
                "historico_pedidos": self.historico_pedidos
            }
            pickle.dump(dados, f)

        with open(self.arquivo_cardapio, "wb") as f:
            pickle.dump(self.cardapio, f)

    def carregar_dados(self) -> None:
        """Carrega pedidos e cardápio de arquivos"""
        # Carrega pedidos
        if os.path.exists(self.arquivo_pedidos):
            try:
                with open(self.arquivo_pedidos, "rb") as f:
                    dados = PedidoUnpickler(f).load()
                    self.fila_pedidos = dados.get("fila_pedidos", [])
                    self.contador_pedidos = dados.get("contador_pedidos", 1)
                    self.historico_pedidos = dados.get("historico_pedidos", [])
            except (pickle.PickleError, EOFError, AttributeError) as e:
                print(f"⚠️ Erro ao carregar pedidos ({e}). Iniciando sistema com dados vazios.")

        # Carrega cardápio
        if os.path.exists(self.arquivo_cardapio):
            try:
                with open(self.arquivo_cardapio, "rb") as f:
                    self.cardapio = pickle.load(f)
            except (pickle.PickleError, EOFError):
                print("⚠️ Erro ao carregar cardápio. Usando cardápio padrão.")

    def _adicionar_pizza_ao_pedido(self, itens_pedido: List[ItemPedido]) -> None:
        """Adiciona uma pizza ao pedido"""
        print("\n--- Sabores disponíveis ---")
        for i, sabor in enumerate(self.cardapio["sabores"].keys(), 1):
            print(f"{i}. {sabor}")

        try:
            opcao = int(input("\nEscolha o número do sabor: ")) - 1
            sabores = list(self.cardapio["sabores"].keys())
            if opcao < 0 or opcao >= len(sabores):
                print("⚠️ Opção inválida! Usando primeiro sabor disponível.")
                opcao = 0
            sabor_pizza = sabores[opcao]
        except ValueError:
            print("⚠️ Entrada inválida! Usando primeiro sabor disponível.")
            sabor_pizza = list(self.cardapio["sabores"].keys())[0]

        # Mostra ingredientes
        print(f"\nIngredientes: {', '.join(self.cardapio['sabores'][sabor_pizza]['ingredientes'])}")

        # Escolha do tamanho
        print("\n--- Tamanhos disponíveis ---")
        for i, tamanho in enumerate(self.cardapio["tamanhos"], 1):
            preco = self.cardapio["sabores"][sabor_pizza]["preco"][tamanho]
            print(f"{i}. {tamanho} - R$ {preco:.2f}")

        try:
            opcao = int(input("\nEscolha o número do tamanho: ")) - 1
            if opcao < 0 or opcao >= len(self.cardapio["tamanhos"]):
                print("⚠️ Opção inválida! Usando tamanho médio.")
                opcao = 1
            tamanho = self.cardapio["tamanhos"][opcao]
        except ValueError:
            print("⚠️ Entrada inválida! Usando tamanho médio.")
            tamanho = "Média"

        # Quantidade
        try:
            quantidade = int(input(f"\nQuantidade de pizzas {sabor_pizza} ({tamanho}): "))
            if quantidade <= 0:
                quantidade = 1
        except ValueError:
            print("⚠️ Quantidade inválida! Usando 1.")
            quantidade = 1

        # Adicionais
        adicionais = []
        print("\n--- Adicionais disponíveis ---")
        for i, (adicional, preco) in enumerate(self.cardapio["adicionais"].items(), 1):
            print(f"{i}. {adicional} - R$ {preco:.2f}")

        escolha = input("\nDeseja adicionar algum adicional? (S/N): ").strip().upper()
        if escolha == "S":
            while True:
                try:
                    opcao = int(input("Digite o número do adicional (0 para finalizar): "))
                    if opcao == 0:
                        break

                    if opcao < 1 or opcao > len(self.cardapio["adicionais"]):
                        print("⚠️ Opção inválida!")
                        continue

                    adicional = list(self.cardapio["adicionais"].keys())[opcao-1]
                    if adicional not in adicionais:
                        adicionais.append(adicional)
                        print(f"✅ {adicional} adicionado!")
                    else:
                        print(f"⚠️ {adicional} já foi adicionado!")
                except ValueError:
                    print("⚠️ Entrada inválida!")

        # Cria o item pizza
        item_pizza = ItemPedido(
            tipo="pizza",
            nome=sabor_pizza,
            detalhes={
                "tamanho": tamanho,
                "adicionais": adicionais
            },
            quantidade=quantidade
        )

        itens_pedido.append(item_pizza)
        print(f"✅ {quantidade}x Pizza {sabor_pizza} ({tamanho}) adicionada ao pedido!")

    def _adicionar_bebida_ao_pedido(self, itens_pedido: List[ItemPedido]) -> None:
        """Adiciona uma bebida ao pedido"""
        print("\n--- Bebidas disponíveis ---")
        
        # Agrupa bebidas por categoria
        categorias = {}
        for bebida, info in self.cardapio["bebidas"].items():
            categoria = info["categoria"]
            if categoria not in categorias:
                categorias[categoria] = []
            categorias[categoria].append((bebida, info["preco"]))

        contador = 1
        bebidas_numeradas = []
        
        for categoria, bebidas in categorias.items():
            print(f"\n{categoria}:")
            for bebida, preco in bebidas:
                print(f"  {contador}. {bebida} - R$ {preco:.2f}")
                bebidas_numeradas.append(bebida)
                contador += 1

        try:
            opcao = int(input(f"\nEscolha o número da bebida (1-{len(bebidas_numeradas)}): ")) - 1
            if opcao < 0 or opcao >= len(bebidas_numeradas):
                print("⚠️ Opção inválida! Usando primeira bebida disponível.")
                opcao = 0
            bebida_escolhida = bebidas_numeradas[opcao]
        except ValueError:
            print("⚠️ Entrada inválida! Usando primeira bebida disponível.")
            bebida_escolhida = bebidas_numeradas[0]

        # Quantidade
        try:
            quantidade = int(input(f"\nQuantidade de {bebida_escolhida}: "))
            if quantidade <= 0:
                quantidade = 1
        except ValueError:
            print("⚠️ Quantidade inválida! Usando 1.")
            quantidade = 1

        # Cria o item bebida
        item_bebida = ItemPedido(
            tipo="bebida",
            nome=bebida_escolhida,
            quantidade=quantidade
        )

        itens_pedido.append(item_bebida)
        print(f"✅ {quantidade}x {bebida_escolhida} adicionada ao pedido!")

    def adicionar_pedido(self) -> None:
        """Adiciona um novo pedido à fila"""
        print("\n=== Novo Pedido ===")

        # Informações do cliente
        nome_cliente = input("Nome do cliente: ")
        telefone = input("Telefone para contato: ")

        itens_pedido = []

        while True:
            print("\n--- O que deseja adicionar ao pedido? ---")
            print("1. Pizza")
            print("2. Bebida")
            print("3. Finalizar pedido")

            try:
                opcao = int(input("Escolha uma opção: "))
            except ValueError:
                print("⚠️ Opção inválida!")
                continue

            if opcao == 1:
                self._adicionar_pizza_ao_pedido(itens_pedido)
            elif opcao == 2:
                self._adicionar_bebida_ao_pedido(itens_pedido)
            elif opcao == 3:
                if not itens_pedido:
                    print("⚠️ Adicione pelo menos um item ao pedido!")
                    continue
                break
            else:
                print("⚠️ Opção inválida!")

            # Pergunta se quer adicionar mais itens
            if itens_pedido:
                continuar = input("\nDeseja adicionar mais itens? (S/N): ").strip().upper()
                if continuar != "S":
                    break

        # Observações
        observacoes = input("\nObservações adicionais: ")

        # Cria o pedido temporário para calcular o valor
        pedido_temp = Pedido(
            numero=self.contador_pedidos,
            cliente=f"{nome_cliente} ({telefone})",
            itens=itens_pedido,
            observacoes=observacoes
        )

        valor_total = pedido_temp.calcular_valor_total(self.cardapio)

        # Confirmação do pedido
        print("\n=== Resumo do Pedido ===")
        print(f"Cliente: {nome_cliente}")
        print(f"Telefone: {telefone}")
        print("\nItens:")
        for item in itens_pedido:
            print(f"  - {item}")
            if item.tipo == "pizza":
                valor_base = self.cardapio["sabores"][item.nome]["preco"][item.detalhes["tamanho"]]
                valor_adicionais = sum(self.cardapio["adicionais"].get(a, 0) for a in item.detalhes.get("adicionais", []))
                valor_item = (valor_base + valor_adicionais) * item.quantidade
                print(f"    Valor: R$ {valor_item:.2f}")
            else:
                valor_item = self.cardapio["bebidas"][item.nome]["preco"] * item.quantidade
                print(f"    Valor: R$ {valor_item:.2f}")

        if observacoes:
            print(f"\nObservações: {observacoes}")
        print(f"\nValor total: R$ {valor_total:.2f}")

        confirma = input("\nConfirmar pedido? (S/N): ").strip().upper()
        if confirma != "S":
            print("❌ Pedido cancelado!")
            return

        # Incrementa o contador e adiciona à fila
        self.contador_pedidos += 1
        self.fila_pedidos.append(pedido_temp)
        self.salvar_dados()

        print(f"\n✅ Pedido #{pedido_temp.numero} registrado com sucesso!")
        print(f"⏱️ Tempo estimado de preparo: {pedido_temp.tempo_preparo} minutos")

    def visualizar_fila(self) -> None:
        """Exibe a fila de pedidos atual"""
        if not self.fila_pedidos:
            print("📭 Nenhum pedido na fila!")
            return

        print("\n📋 == FILA DE PEDIDOS ==")
        for i, pedido in enumerate(self.fila_pedidos, 1):
            tempo_espera = (datetime.datetime.now() - pedido.data_hora).total_seconds() // 60
            valor_total = pedido.calcular_valor_total(self.cardapio)
            
            print(f"{i}. Pedido #{pedido.numero} | Cliente: {pedido.cliente}")
            print(f"   Status: {pedido.status} | Valor: R$ {valor_total:.2f}")
            print(f"   ⏱️ Aguardando há {int(tempo_espera)} minutos | Preparo: {pedido.tempo_preparo} min")
            
            print("   Itens:")
            for item in pedido.itens:
                print(f"     - {item}")
            
            if pedido.observacoes:
                print(f"   📝 Obs: {pedido.observacoes}")
            print()

    def entregar_pedido(self) -> None:
        """Remove o primeiro pedido da fila (FIFO)"""
        if not self.fila_pedidos:
            print("🚫 Nenhum pedido na fila!")
            return

        # Mostra os pedidos pendentes
        self.visualizar_fila()

        # Pergunta qual pedido entregar (por padrão, o primeiro)
        try:
            escolha = input("Digite o número da posição do pedido a entregar (ENTER para o primeiro): ")
            if not escolha:
                posicao = 0
            else:
                posicao = int(escolha) - 1
        except ValueError:
            print("⚠️ Entrada inválida! Entregando o primeiro pedido.")
            posicao = 0

        if posicao < 0 or posicao >= len(self.fila_pedidos):
            print("⚠️ Posição inválida!")
            return

        # Remove o pedido da fila
        pedido_entregue = self.fila_pedidos.pop(posicao)
        pedido_entregue.status = "Entregue"

        # Adiciona ao histórico
        self.historico_pedidos.append(pedido_entregue)

        # Salva os dados
        self.salvar_dados()

        valor_total = pedido_entregue.calcular_valor_total(self.cardapio)
        print(f"🍕 Pedido #{pedido_entregue.numero} de {pedido_entregue.cliente} foi entregue!")
        print(f"💰 Valor total: R$ {valor_total:.2f}")

    def alterar_pedido(self) -> None:
        """Altera informações de um pedido"""
        if not self.fila_pedidos:
            print("🚫 Nenhum pedido na fila!")
            return

        try:
            numero_pedido = int(input("Digite o número do pedido que deseja alterar: "))
        except ValueError:
            print("⚠️ Número do pedido inválido!")
            return

        pedido = None
        for p in self.fila_pedidos:
            if p.numero == numero_pedido:
                pedido = p
                break

        if not pedido:
            print("⚠️ Pedido não encontrado!")
            return

        print(f"\nEditando pedido #{pedido.numero}")
        print("O que deseja alterar?")
        print("1. Adicionar item")
        print("2. Remover item")
        print("3. Observações")
        print("4. Status")

        try:
            opcao = int(input("Escolha uma opção: "))
        except ValueError:
            print("⚠️ Opção inválida!")
            return

        if opcao == 1:  # Adicionar item
            print("O que deseja adicionar?")
            print("1. Pizza")
            print("2. Bebida")
            
            try:
                tipo_item = int(input("Escolha: "))
            except ValueError:
                print("⚠️ Opção inválida!")
                return

            if tipo_item == 1:
                self._adicionar_pizza_ao_pedido(pedido.itens)
            elif tipo_item == 2:
                self._adicionar_bebida_ao_pedido(pedido.itens)
            else:
                print("⚠️ Opção inválida!")
                return

        elif opcao == 2:  # Remover item
            if not pedido.itens:
                print("⚠️ Não há itens para remover!")
                return

            print("\nItens no pedido:")
            for i, item in enumerate(pedido.itens, 1):
                print(f"{i}. {item}")

            try:
                item_remover = int(input("Digite o número do item a remover: ")) - 1
                if item_remover < 0 or item_remover >= len(pedido.itens):
                    print("⚠️ Item inválido!")
                    return

                item_removido = pedido.itens.pop(item_remover)
                print(f"✅ Item removido: {item_removido}")
            except ValueError:
                print("⚠️ Entrada inválida!")
                return

        elif opcao == 3:  # Alterar observações
            print(f"Observações atuais: {pedido.observacoes}")
            novas_obs = input("Digite as novas observações: ")
            pedido.observacoes = novas_obs
            print("✅ Observações atualizadas!")

        elif opcao == 4:  # Alterar status
            print("\n--- Status disponíveis ---")
            status_disponiveis = ["Pendente", "Em preparo", "Saiu para entrega"]
            for i, status in enumerate(status_disponiveis, 1):
                print(f"{i}. {status}")

            try:
                escolha = int(input(f"\nEscolha o novo status (atual: {pedido.status}): ")) - 1
                if escolha < 0 or escolha >= len(status_disponiveis):
                    print("⚠️ Opção inválida!")
                    return

                pedido.status = status_disponiveis[escolha]
                print(f"✅ Status alterado para {pedido.status}")
            except ValueError:
                print("⚠️ Entrada inválida!")
                return

        else:
            print("⚠️ Opção inválida!")
            return

        # Recalcula tempo de preparo
        pedido.tempo_preparo = pedido._calcular_tempo_preparo()

        # Salva as alterações
        self.salvar_dados()
        print("✅ Pedido atualizado com sucesso!")

    def consultar_pedido(self) -> None:
        """Consulta detalhes de um pedido específico"""
        try:
            numero_pedido = int(input("Informe o número do pedido que deseja consultar: "))
        except ValueError:
            print("⚠️ Número do pedido inválido!")
            return

        # Procura na fila atual
        for pedido in self.fila_pedidos:
            if pedido.numero == numero_pedido:
                self._exibir_detalhes_pedido(pedido)
                return

        # Procura no histórico
        for pedido in self.historico_pedidos:
            if pedido.numero == numero_pedido:
                self._exibir_detalhes_pedido(pedido)
                print("📝 Nota: Este pedido já foi entregue e está no histórico.")
                return

        print("⚠️ Pedido não encontrado.")

    def _exibir_detalhes_pedido(self, pedido: Pedido) -> None:
        """Exibe detalhes formatados de um pedido"""
        print("\n=== DETALHES DO PEDIDO ===")
        print(f"Número: #{pedido.numero}")
        print(f"Cliente: {pedido.cliente}")
        print(f"Data/Hora: {pedido.data_hora.strftime('%d/%m/%Y %H:%M')}")
        print(f"Status: {pedido.status}")

        print("\nItens do pedido:")
        for item in pedido.itens:
            print(f"  - {item}")
            if item.tipo == "pizza" and item.nome in self.cardapio["sabores"]:
                ingredientes = self.cardapio["sabores"][item.nome]["ingredientes"]
                print(f"    Ingredientes: {', '.join(ingredientes)}")

        # Observações
        if pedido.observacoes:
            print(f"\nObservações: {pedido.observacoes}")

        # Informações de tempo
        tempo_espera = (datetime.datetime.now() - pedido.data_hora).total_seconds() // 60
        print(f"\nTempo de espera: {int(tempo_espera)} minutos")
        print(f"Tempo estimado de preparo: {pedido.tempo_preparo} minutos")

        # Valor total
        valor_total = pedido.calcular_valor_total(self.cardapio)
        print(f"Valor total: R$ {valor_total:.2f}")

    def gerenciar_cardapio(self) -> None:
        """Permite gerenciar o cardápio"""
        print("\n=== GERENCIAMENTO DO CARDÁPIO ===")
        print("1. Ver cardápio completo")
        print("2. Adicionar novo sabor de pizza")
        print("3. Adicionar nova bebida")
        print("4. Adicionar novo adicional")
        print("5. Modificar preços")
        print("6. Remover item")
        print("7. Voltar")

        try:
            opcao = int(input("Escolha uma opção: "))
        except ValueError:
            print("⚠️ Opção inválida!")
            return

        if opcao == 1:  # Ver cardápio
            self._mostrar_cardapio()

        elif opcao == 2:  # Adicionar sabor
            nome_sabor = input("Nome do novo sabor: ")
            
            print("Digite os ingredientes (separados por vírgula):")
            ingredientes_str = input()
            ingredientes = [ing.strip() for ing in ingredientes_str.split(',')]
            
            precos = {}
            for tamanho in self.cardapio["tamanhos"]:
                while True:
                    try:
                        preco = float(input(f"Preço para {tamanho}: R$ "))
                        precos[tamanho] = preco
                        break
                    except ValueError:
                        print("⚠️ Preço inválido!")
            
            self.cardapio["sabores"][nome_sabor] = {
                "ingredientes": ingredientes,
                "preco": precos
            }
            
            self.salvar_dados()
            print(f"✅ Sabor {nome_sabor} adicionado com sucesso!")

        elif opcao == 3:  # Adicionar bebida
            nome_bebida = input("Nome da nova bebida: ")
            categoria = input("Categoria da bebida: ")
            
            while True:
                try:
                    preco = float(input(f"Preço da {nome_bebida}: R$ "))
                    break
                except ValueError:
                    print("⚠️ Preço inválido!")
            
            self.cardapio["bebidas"][nome_bebida] = {
                "categoria": categoria,
                "preco": preco
            }
            
            self.salvar_dados()
            print(f"✅ Bebida {nome_bebida} adicionada com sucesso!")

        elif opcao == 4:  # Adicionar adicional
            nome_adicional = input("Nome do novo adicional: ")
            
            while True:
                try:
                    preco = float(input(f"Preço do {nome_adicional}: R$ "))
                    break
                except ValueError:
                    print("⚠️ Preço inválido!")
            
            self.cardapio["adicionais"][nome_adicional] = preco
            
            self.salvar_dados()
            print(f"✅ Adicional {nome_adicional} adicionado com sucesso!")

        elif opcao == 5:  # Modificar preços
            print("O que deseja modificar?")
            print("1. Preço de pizza")
            print("2. Preço de bebida")
            print("3. Preço de adicional")
            
            try:
                sub_opcao = int(input("Escolha: "))
            except ValueError:
                print("⚠️ Opção inválida!")
                return
            
            if sub_opcao == 1:  # Pizza
                print("Sabores disponíveis:")
                for i, sabor in enumerate(self.cardapio["sabores"].keys(), 1):
                    print(f"{i}. {sabor}")
                
                try:
                    escolha = int(input("Escolha o sabor: ")) - 1
                    sabores = list(self.cardapio["sabores"].keys())
                    sabor_escolhido = sabores[escolha]
                    
                    print("Tamanhos:")
                    for i, tamanho in enumerate(self.cardapio["tamanhos"], 1):
                        preco_atual = self.cardapio["sabores"][sabor_escolhido]["preco"][tamanho]
                        print(f"{i}. {tamanho} - R$ {preco_atual:.2f}")
                    
                    tamanho_idx = int(input("Escolha o tamanho: ")) - 1
                    tamanho_escolhido = self.cardapio["tamanhos"][tamanho_idx]
                    
                    novo_preco = float(input(f"Novo preço para {sabor_escolhido} ({tamanho_escolhido}): R$ "))
                    self.cardapio["sabores"][sabor_escolhido]["preco"][tamanho_escolhido] = novo_preco
                    
                    self.salvar_dados()
                    print("✅ Preço atualizado!")
                    
                except (ValueError, IndexError):
                    print("⚠️ Entrada inválida!")
            
            elif sub_opcao == 2:  # Bebida
                print("Bebidas disponíveis:")
                for i, bebida in enumerate(self.cardapio["bebidas"].keys(), 1):
                    preco_atual = self.cardapio["bebidas"][bebida]["preco"]
                    print(f"{i}. {bebida} - R$ {preco_atual:.2f}")
                
                try:
                    escolha = int(input("Escolha a bebida: ")) - 1
                    bebidas = list(self.cardapio["bebidas"].keys())
                    bebida_escolhida = bebidas[escolha]
                    
                    novo_preco = float(input(f"Novo preço para {bebida_escolhida}: R$ "))
                    self.cardapio["bebidas"][bebida_escolhida]["preco"] = novo_preco
                    
                    self.salvar_dados()
                    print("✅ Preço atualizado!")
                    
                except (ValueError, IndexError):
                    print("⚠️ Entrada inválida!")
            
            elif sub_opcao == 3:  # Adicional
                print("Adicionais disponíveis:")
                for i, (adicional, preco) in enumerate(self.cardapio["adicionais"].items(), 1):
                    print(f"{i}. {adicional} - R$ {preco:.2f}")
                
                try:
                    escolha = int(input("Escolha o adicional: ")) - 1
                    adicionais = list(self.cardapio["adicionais"].keys())
                    adicional_escolhido = adicionais[escolha]
                    
                    novo_preco = float(input(f"Novo preço para {adicional_escolhido}: R$ "))
                    self.cardapio["adicionais"][adicional_escolhido] = novo_preco
                    
                    self.salvar_dados()
                    print("✅ Preço atualizado!")
                    
                except (ValueError, IndexError):
                    print("⚠️ Entrada inválida!")

        elif opcao == 6:  # Remover item
            print("O que deseja remover?")
            print("1. Sabor de pizza")
            print("2. Bebida")
            print("3. Adicional")
            
            try:
                sub_opcao = int(input("Escolha: "))
            except ValueError:
                print("⚠️ Opção inválida!")
                return
            
            if sub_opcao == 1:  # Remover sabor
                if not self.cardapio["sabores"]:
                    print("⚠️ Não há sabores para remover!")
                    return
                
                print("Sabores disponíveis:")
                for i, sabor in enumerate(self.cardapio["sabores"].keys(), 1):
                    print(f"{i}. {sabor}")
                
                try:
                    escolha = int(input("Escolha o sabor a remover: ")) - 1
                    sabores = list(self.cardapio["sabores"].keys())
                    sabor_removido = sabores[escolha]
                    
                    confirma = input(f"Confirma remoção de {sabor_removido}? (S/N): ").strip().upper()
                    if confirma == "S":
                        del self.cardapio["sabores"][sabor_removido]
                        self.salvar_dados()
                        print(f"✅ Sabor {sabor_removido} removido!")
                    
                except (ValueError, IndexError):
                    print("⚠️ Entrada inválida!")
            
            elif sub_opcao == 2:  # Remover bebida
                if not self.cardapio["bebidas"]:
                    print("⚠️ Não há bebidas para remover!")
                    return
                
                print("Bebidas disponíveis:")
                for i, bebida in enumerate(self.cardapio["bebidas"].keys(), 1):
                    print(f"{i}. {bebida}")
                
                try:
                    escolha = int(input("Escolha a bebida a remover: ")) - 1
                    bebidas = list(self.cardapio["bebidas"].keys())
                    bebida_removida = bebidas[escolha]
                    
                    confirma = input(f"Confirma remoção de {bebida_removida}? (S/N): ").strip().upper()
                    if confirma == "S":
                        del self.cardapio["bebidas"][bebida_removida]
                        self.salvar_dados()
                        print(f"✅ Bebida {bebida_removida} removida!")
                        
                except (ValueError, IndexError):
                    print("⚠️ Entrada inválida!")
            
            elif sub_opcao == 3:  # Remover adicional
                if not self.cardapio["adicionais"]:
                    print("⚠️ Não há adicionais para remover!")
                    return
                
                print("Adicionais disponíveis:")
                for i, adicional in enumerate(self.cardapio["adicionais"].keys(), 1):
                    print(f"{i}. {adicional}")
                
                try:
                    escolha = int(input("Escolha o adicional a remover: ")) - 1
                    adicionais = list(self.cardapio["adicionais"].keys())
                    adicional_removido = adicionais[escolha]
                    
                    confirma = input(f"Confirma remoção de {adicional_removido}? (S/N): ").strip().upper()
                    if confirma == "S":
                        del self.cardapio["adicionais"][adicional_removido]
                        self.salvar_dados()
                        print(f"✅ Adicional {adicional_removido} removido!")
                        
                except (ValueError, IndexError):
                    print("⚠️ Entrada inválida!")

    def _mostrar_cardapio(self) -> None:
        """Exibe o cardápio completo"""
        print("\n🍕 === CARDÁPIO DA PIZZARIA ===")
        
        print("\n--- PIZZAS ---")
        for sabor, info in self.cardapio["sabores"].items():
            print(f"\n{sabor}")
            print(f"  Ingredientes: {', '.join(info['ingredientes'])}")
            print("  Preços:")
            for tamanho, preco in info["preco"].items():
                print(f"    {tamanho}: R$ {preco:.2f}")
        
        print("\n--- ADICIONAIS ---")
        for adicional, preco in self.cardapio["adicionais"].items():
            print(f"  {adicional}: R$ {preco:.2f}")
        
        print("\n--- BEBIDAS ---")
        categorias = {}
        for bebida, info in self.cardapio["bebidas"].items():
            categoria = info["categoria"]
            if categoria not in categorias:
                categorias[categoria] = []
            categorias[categoria].append((bebida, info["preco"]))
        
        for categoria, bebidas in categorias.items():
            print(f"\n{categoria}:")
            for bebida, preco in bebidas:
                print(f"  {bebida}: R$ {preco:.2f}")

    def relatorio_vendas(self) -> None:
        """Gera relatório de vendas"""
        if not self.historico_pedidos:
            print("📊 Nenhuma venda registrada ainda!")
            return
        
        print("\n📊 === RELATÓRIO DE VENDAS ===")
        
        # Estatísticas gerais
        total_pedidos = len(self.historico_pedidos)
        valor_total_vendas = sum(pedido.calcular_valor_total(self.cardapio) 
                               for pedido in self.historico_pedidos)
        
        print(f"Total de pedidos entregues: {total_pedidos}")
        print(f"Valor total em vendas: R$ {valor_total_vendas:.2f}")
        print(f"Ticket médio: R$ {valor_total_vendas/total_pedidos:.2f}")
        
        # Itens mais vendidos
        contagem_itens = {}
        for pedido in self.historico_pedidos:
            for item in pedido.itens:
                nome_item = f"{item.nome} ({item.tipo})"
                contagem_itens[nome_item] = contagem_itens.get(nome_item, 0) + item.quantidade
        
        if contagem_itens:
            print("\n--- ITENS MAIS VENDIDOS ---")
            itens_ordenados = sorted(contagem_itens.items(), key=lambda x: x[1], reverse=True)
            for i, (item, quantidade) in enumerate(itens_ordenados[:5], 1):
                print(f"{i}. {item}: {quantidade} unidades")
        
        # Vendas por período
        vendas_por_data = {}
        for pedido in self.historico_pedidos:
            data = pedido.data_hora.date()
            valor = pedido.calcular_valor_total(self.cardapio)
            vendas_por_data[data] = vendas_por_data.get(data, 0) + valor
        
        if vendas_por_data:
            print("\n--- VENDAS POR DIA ---")
            for data, valor in sorted(vendas_por_data.items(), reverse=True)[:7]:
                print(f"{data.strftime('%d/%m/%Y')}: R$ {valor:.2f}")

    def executar(self) -> None:
        """Loop principal do sistema"""
        print("🍕 Bem-vindo ao Sistema de Gerenciamento da Pizzaria! 🍕")
        
        while True:
            print("\n" + "="*50)
            print("🍕 SISTEMA DA PIZZARIA")
            print("="*50)
            print("1. 📝 Novo pedido")
            print("2. 👀 Ver fila de pedidos")
            print("3. 🚚 Entregar pedido")
            print("4. ✏️ Alterar pedido")
            print("5. 🔍 Consultar pedido")
            print("6. 🍕 Gerenciar cardápio")
            print("7. 📊 Relatório de vendas")
            print("8. ❌ Sair")
            print("="*50)
            
            try:
                opcao = int(input("Escolha uma opção: "))
            except ValueError:
                print("⚠️ Por favor, digite um número válido!")
                continue
            
            if opcao == 1:
                self.adicionar_pedido()
            elif opcao == 2:
                self.visualizar_fila()
            elif opcao == 3:
                self.entregar_pedido()
            elif opcao == 4:
                self.alterar_pedido()
            elif opcao == 5:
                self.consultar_pedido()
            elif opcao == 6:
                self.gerenciar_cardapio()
            elif opcao == 7:
                self.relatorio_vendas()
            elif opcao == 8:
                print("👋 Obrigado por usar o Sistema da Pizzaria!")
                break
            else:
                print("⚠️ Opção inválida! Tente novamente.")
            
            # Pausa para o usuário ler as mensagens
            input("\nPressione ENTER para continuar...")


# Função principal
def main():
    sistema = SistemaPizzaria()
    sistema.executar()


if __name__ == "__main__":
  main()


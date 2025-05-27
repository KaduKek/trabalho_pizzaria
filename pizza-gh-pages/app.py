from flask import Flask, render_template, request, jsonify, redirect, url_for
from pizzaria import SistemaPizzaria
import json
from pedido import ItemPedido, Pedido
from db import (
    criar_pedido,
    criar_pedido_bebida,
    obter_id_pizza_por_nome,
    obter_id_bebida_por_nome
)

app = Flask(__name__)

# Inicializa o sistema da pizzaria
sistema = SistemaPizzaria()

@app.route('/')
def index():
    """Página inicial - mostra cardápio"""
    cardapio = sistema.cardapio
    return render_template('index.html', cardapio=cardapio)

@app.route('/api/pedido', methods=['POST'])
@app.route('/api/pedido', methods=['POST'])
def api_criar_pedido():
    try:
        data = request.json
        nome = data['nome_cliente']
        telefone = data['telefone']
        endereco = data.get('endereco', '')
        itens_json = data['itens']

        itens = []
        for item in itens_json:
            tipo = item['tipo']
            nome_item = item['nome']
            quantidade = item.get('quantidade', 1)
            detalhes = item.get('detalhes', {})

            itens.append(ItemPedido(
                tipo=tipo,
                nome=nome_item,
                quantidade=quantidade,
                detalhes=detalhes
            ))

            # Salvar no banco de dados
            if tipo == "pizza":
                pizza_id = obter_id_pizza_por_nome(nome_item)
                if not pizza_id:
                    raise ValueError(f"Pizza '{nome_item}' não encontrada.")
                criar_pedido(pizza_id, quantidade, nome, telefone, endereco)
            elif tipo == "bebida":
                bebida_id = obter_id_bebida_por_nome(nome_item)
                if not bebida_id:
                    raise ValueError(f"Bebida '{nome_item}' não encontrada.")
                criar_pedido_bebida(bebida_id, quantidade, nome, telefone, endereco)

        novo_pedido = Pedido(
            numero=sistema.contador_pedidos,
            cliente=f"{nome} ({telefone})",
            itens=itens,
            observacoes=f"Endereço: {endereco}"
        )

        sistema.contador_pedidos += 1
        sistema.fila_pedidos.append(novo_pedido)
        sistema.salvar_dados()

        return jsonify({'mensagem': f'Pedido #{novo_pedido.numero} criado com sucesso!'})

    except Exception as e:
        return jsonify({'erro': str(e)}), 400
@app.route('/api/cardapio')
def api_cardapio():
    try:
        from db import get_pizzas, get_bebidas_por_categoria
        pizzas = get_pizzas()
        bebidas_por_categoria = get_bebidas_por_categoria()
        bebidas = []
        for lista in bebidas_por_categoria.values():
            bebidas.extend(lista)
        return jsonify({"pizzas": pizzas, "bebidas": bebidas})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
@app.route('/pedidos-db')
def pedidos_db():
    from db import get_connection
    conn = get_connection()
    pedidos = conn.execute('SELECT * FROM pedidos ORDER BY data_pedido DESC').fetchall()
    pedidos_bebidas = conn.execute('SELECT * FROM pedidos_bebidas ORDER BY data_pedido DESC').fetchall()
    conn.close()
    return render_template('pedidos_db.html', pedidos=pedidos, pedidos_bebidas=pedidos_bebidas)
@app.route('/home')
def home():
    # Apenas redireciona para a página inicial
    return redirect(url_for('index'))

@app.route('/menu')
def menu():
    sabores_disponiveis = [
        'Calabresa',
        'Frango c/ Catupiry',
        'Marguerita',
        'Portuguesa',
        'Quatro Queijos',
        'Presunto',
        'Bacon',
        'Napolitana'
    ]

    # Bebidas organizadas por categoria
    bebidas_disponiveis = {
        'Refrigerante': [
            {'nome': 'Coca-Cola Lata', 'preco': 6.00, 'imagem': 'coca_cola_lata.jpg'},
            {'nome': 'Pepsi Lata', 'preco': 6.00, 'imagem': 'pepsi_lata.jpg'},
            {'nome': 'Fanta Laranja Lata', 'preco': 6.00, 'imagem': 'fanta_laranja_lata.jpg'},
            {'nome': 'Fanta Uva Lata', 'preco': 6.00, 'imagem': 'fanta_uva_lata.jpg'},
        ],
        'Suco Natural': [
            {'nome': 'Suco de Laranja', 'preco': 7.50, 'imagem': 'suco_laranja.jpg'},
            {'nome': 'Suco de Limão', 'preco': 7.50, 'imagem': 'suco_limao.jpg'},
            {'nome': 'Suco de Abacaxi', 'preco': 7.50, 'imagem': 'suco_abacaxi.jpg'},
            {'nome': 'Suco de Maracujá', 'preco': 7.50, 'imagem': 'suco_maracuja.jpg'},
        ],
        'Água': [
            {'nome': 'Água Mineral 500ml', 'preco': 4.00, 'imagem': 'agua_mineral.jpg'},
            {'nome': 'Água com Gás 500ml', 'preco': 4.00, 'imagem': 'agua_com_gas.jpg'},
        ]
    }
    
    return render_template('menu.html', 
                         sabores_disponiveis=sabores_disponiveis,
                         bebidas_disponiveis=bebidas_disponiveis)

@app.route('/sobre')
def sobre():
    return render_template('about.html')

@app.route('/contato')
def contato():
    return render_template('contact.html')

@app.route('/servicos')
def servicos():
    return render_template('services.html')

@app.route('/pedido')
def pedido():
    # Bebidas para o formulário de pedido
    bebidas_disponiveis = {
        'Coca-Cola Lata': 6.00,
        'Pepsi Lata': 6.00,
        'Fanta Laranja Lata': 6.00,
        'Fanta Uva Lata': 6.00,
        'Suco de Laranja': 7.50,
        'Suco de Limão': 7.50,
        'Suco de Abacaxi': 7.50,
        'Suco de Maracujá': 7.50,
        'Água Mineral 500ml': 4.00,
        'Água com Gás 500ml': 4.00,
    }
    
    return render_template('pedido.html', bebidas_disponiveis=bebidas_disponiveis)

@app.route('/pedidos')
def listar_pedidos():
    """Lista todos os pedidos na fila"""
    pedidos = []
    for pedido in sistema.fila_pedidos:
        pedidos.append({
            'numero': pedido.numero,
            'cliente': pedido.cliente,
            'sabor': pedido.sabor,
            'tamanho': pedido.tamanho,
            'adicionais': pedido.adicional,
            'bebidas': getattr(pedido, 'bebidas', []),  # Adiciona bebidas se existir
            'observacoes': pedido.observacoes,
            'status': pedido.status,
            'tempo_preparo': pedido.tempo_preparo,
            'data_hora': pedido.data_hora.strftime('%d/%m/%Y %H:%M')
        })
    return render_template('pedidos.html', pedidos=pedidos)

@app.route('/novo-pedido', methods=['GET', 'POST'])
def novo_pedido():
    """Formulário para criar novo pedido"""
    if request.method == 'GET':
        # Bebidas para o formulário
        bebidas_disponiveis = {
            'Coca-Cola Lata': 6.00,
            'Pepsi Lata': 6.00,
            'Fanta Laranja Lata': 6.00,
            'Fanta Uva Lata': 6.00,
            'Suco de Laranja': 7.50,
            'Suco de Limão': 7.50,
            'Suco de Abacaxi': 7.50,
            'Suco de Maracujá': 7.50,
            'Água Mineral 500ml': 4.00,
            'Água com Gás 500ml': 4.00,
        }
        return render_template('novo_pedido.html', 
                             cardapio=sistema.cardapio,
                             bebidas_disponiveis=bebidas_disponiveis)
    
    # Processa o formulário
    try:
        nome_cliente = request.form['nome_cliente']
        telefone = request.form['telefone']
        sabor = request.form['sabor']
        tamanho = request.form['tamanho']
        adicionais = request.form.getlist('adicionais')  # Lista de adicionais
        bebidas = request.form.getlist('bebidas')  # Lista de bebidas
        observacoes = request.form.get('observacoes', '')
        
        # Cria o pedido usando a classe do sistema
        from pizzaria import Pedido
        novo_pedido = Pedido(
            numero=sistema.contador_pedidos,
            cliente=f"{nome_cliente} ({telefone})",
            sabor=sabor,
            tamanho=tamanho,
            adicional=adicionais,
            observacoes=observacoes
        )
        
        # Adiciona bebidas ao pedido (se a classe Pedido suportar)
        if hasattr(novo_pedido, 'bebidas'):
            novo_pedido.bebidas = bebidas
        else:
            # Se não suportar, adiciona às observações
            if bebidas:
                bebidas_texto = ', '.join(bebidas)
                if observacoes:
                    novo_pedido.observacoes += f" | Bebidas: {bebidas_texto}"
                else:
                    novo_pedido.observacoes = f"Bebidas: {bebidas_texto}"
        
        # Adiciona à fila
        sistema.contador_pedidos += 1
        sistema.fila_pedidos.append(novo_pedido)
        sistema.salvar_dados()
        
        return redirect(url_for('listar_pedidos'))
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 400

@app.route('/entregar-pedido/<int:numero_pedido>', methods=['POST'])
def entregar_pedido(numero_pedido):
    """Marca um pedido como entregue"""
    try:
        # Procura o pedido na fila
        pedido_encontrado = None
        for i, pedido in enumerate(sistema.fila_pedidos):
            if pedido.numero == numero_pedido:
                pedido_encontrado = sistema.fila_pedidos.pop(i)
                break
        
        if not pedido_encontrado:
            return jsonify({'erro': 'Pedido não encontrado'}), 404
        
        # Move para o histórico
        pedido_encontrado.status = "Entregue"
        sistema.historico_pedidos.append(pedido_encontrado)
        sistema.salvar_dados()
        
        return jsonify({'sucesso': True, 'mensagem': f'Pedido #{numero_pedido} entregue!'})
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 400

@app.route('/atualizar-status/<int:numero_pedido>', methods=['POST'])
def atualizar_status(numero_pedido):
    """Atualiza o status de um pedido"""
    try:
        novo_status = request.json.get('status')
        
        # Procura o pedido na fila
        for pedido in sistema.fila_pedidos:
            if pedido.numero == numero_pedido:
                pedido.status = novo_status
                sistema.salvar_dados()
                return jsonify({'sucesso': True})
        
        return jsonify({'erro': 'Pedido não encontrado'}), 404
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 400

@app.route('/cardapio')
def ver_cardapio():
    """Exibe o cardápio completo incluindo bebidas"""
    # Bebidas organizadas para exibição
    bebidas = {
        'Refrigerante': [
            {'nome': 'Coca-Cola Lata', 'preco': 6.00},
            {'nome': 'Pepsi Lata', 'preco': 6.00},
            {'nome': 'Fanta Laranja Lata', 'preco': 6.00},
            {'nome': 'Fanta Uva Lata', 'preco': 6.00},
        ],
        'Suco Natural': [
            {'nome': 'Suco de Laranja', 'preco': 7.50},
            {'nome': 'Suco de Limão', 'preco': 7.50},
            {'nome': 'Suco de Abacaxi', 'preco': 7.50},
            {'nome': 'Suco de Maracujá', 'preco': 7.50},
        ],
        'Água': [
            {'nome': 'Água Mineral 500ml', 'preco': 4.00},
            {'nome': 'Água com Gás 500ml', 'preco': 4.00},
        ]
    }
    
    return render_template('cardapio.html', 
                         cardapio=sistema.cardapio,
                         bebidas=bebidas)

@app.route('/relatorio')
def relatorio():
    """Página de relatórios incluindo vendas de bebidas"""
    if not sistema.historico_pedidos:
        return render_template('relatorio.html', dados=None)
    
    # Preços das bebidas para cálculo
    precos_bebidas = {
        'Coca-Cola Lata': 6.00,
        'Pepsi Lata': 6.00,
        'Fanta Laranja Lata': 6.00,
        'Fanta Uva Lata': 6.00,
        'Suco de Laranja': 7.50,
        'Suco de Limão': 7.50,
        'Suco de Abacaxi': 7.50,
        'Suco de Maracujá': 7.50,
        'Água Mineral 500ml': 4.00,
        'Água com Gás 500ml': 4.00,
    }
    
    # Calcula estatísticas básicas
    total_pedidos = len(sistema.historico_pedidos)
    faturamento = 0
    sabores_populares = {}
    bebidas_vendidas = {}
    
    for pedido in sistema.historico_pedidos:
        # Calcula faturamento das pizzas
        if (pedido.sabor in sistema.cardapio["sabores"] and 
            pedido.tamanho in sistema.cardapio["sabores"][pedido.sabor]["preco"]):
            valor_base = sistema.cardapio["sabores"][pedido.sabor]["preco"][pedido.tamanho]
            valor_adicionais = sum(sistema.cardapio["adicionais"].get(a, 0) for a in pedido.adicional)
            faturamento += valor_base + valor_adicionais
        
        # Calcula faturamento das bebidas
        bebidas_pedido = getattr(pedido, 'bebidas', [])
        if not bebidas_pedido and pedido.observacoes and 'Bebidas:' in pedido.observacoes:
            # Extrai bebidas das observações se não estiver no atributo bebidas
            try:
                parte_bebidas = pedido.observacoes.split('Bebidas:')[1].split('|')[0].strip()
                bebidas_pedido = [b.strip() for b in parte_bebidas.split(',')]
            except:
                bebidas_pedido = []
        
        for bebida in bebidas_pedido:
            if bebida in precos_bebidas:
                faturamento += precos_bebidas[bebida]
                bebidas_vendidas[bebida] = bebidas_vendidas.get(bebida, 0) + 1
        
        # Conta sabores populares
        if pedido.sabor in sabores_populares:
            sabores_populares[pedido.sabor] += 1
        else:
            sabores_populares[pedido.sabor] = 1
    
    dados_relatorio = {
        'total_pedidos': total_pedidos,
        'faturamento': faturamento,
        'sabores_populares': sorted(sabores_populares.items(), 
                                  key=lambda x: x[1], reverse=True)[:5],
        'bebidas_populares': sorted(bebidas_vendidas.items(),
                                  key=lambda x: x[1], reverse=True)[:5]
    }
    
    return render_template('relatorio.html', dados=dados_relatorio)

@app.route('/api/pedidos')
def api_pedidos():
    """API para obter pedidos em JSON"""
    pedidos = []
    for pedido in sistema.fila_pedidos:
        pedidos.append({
            'numero': pedido.numero,
            'cliente': pedido.cliente,
            'sabor': pedido.sabor,
            'tamanho': pedido.tamanho,
            'adicionais': pedido.adicional,
            'bebidas': getattr(pedido, 'bebidas', []),
            'status': pedido.status,
            'tempo_preparo': pedido.tempo_preparo
        })
    return jsonify(pedidos)

@app.route('/api/bebidas')
def api_bebidas():
    """API para obter lista de bebidas disponíveis"""
    bebidas = {
        'Coca-Cola Lata': {'categoria': 'Refrigerante', 'preco': 6.00},
        'Pepsi Lata': {'categoria': 'Refrigerante', 'preco': 6.00},
        'Fanta Laranja Lata': {'categoria': 'Refrigerante', 'preco': 6.00},
        'Fanta Uva Lata': {'categoria': 'Refrigerante', 'preco': 6.00},
        'Suco de Laranja': {'categoria': 'Suco Natural', 'preco': 7.50},
        'Suco de Limão': {'categoria': 'Suco Natural', 'preco': 7.50},
        'Suco de Abacaxi': {'categoria': 'Suco Natural', 'preco': 7.50},
        'Suco de Maracujá': {'categoria': 'Suco Natural', 'preco': 7.50},
        'Água Mineral 500ml': {'categoria': 'Água', 'preco': 4.00},
        'Água com Gás 500ml': {'categoria': 'Água', 'preco': 4.00},
    }
    return jsonify(bebidas)

@app.route('/pedido/confirmado')
def pedido_confirmado():
    return render_template('pedido_confirmado.html')

@app.route('/admin/resetar-cardapio')
def resetar_cardapio():
    from db import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pizzas")
    cursor.execute("DELETE FROM bebidas")
    conn.commit()
    conn.close()
    return "✅ Cardápio apagado com sucesso!"

if __name__ == '__main__':
    from db import criar_tabelas, inserir_pizzas_exemplo, inserir_bebidas_exemplo

    criar_tabelas()
    inserir_pizzas_exemplo()
    inserir_bebidas_exemplo()

    app.run(debug=True)
    

if __name__ == '__main__':
    app.run(debug=True)
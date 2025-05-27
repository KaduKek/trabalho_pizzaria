import sqlite3
from datetime import datetime

DATABASE = 'pizzaria.db'

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Para acessar colunas por nome
    return conn

def get_pizzas():
    """Busca todas as pizzas disponíveis"""
    conn = get_connection()
    pizzas = conn.execute('''
        SELECT id, nome, descricao, preco, imagem 
        FROM pizzas 
        WHERE ativo = 1
        ORDER BY nome
    ''').fetchall()
    conn.close()
    
    # Converter para lista de dicionários
    return [dict(pizza) for pizza in pizzas]

def get_pizza_por_id(pizza_id):
    """Busca uma pizza específica por ID"""
    conn = get_connection()
    pizza = conn.execute('''
        SELECT id, nome, descricao, preco, imagem 
        FROM pizzas 
        WHERE id = ? AND ativo = 1
    ''', (pizza_id,)).fetchone()
    conn.close()
    
    return dict(pizza) if pizza else None

def criar_pedido(pizza_id, quantidade, nome_cliente, telefone, endereco=None):
    """Cria um novo pedido no banco de dados"""
    conn = get_connection()
    
    # Buscar preço da pizza
    pizza = conn.execute('SELECT preco FROM pizzas WHERE id = ?', (pizza_id,)).fetchone()
    if not pizza:
        conn.close()
        raise ValueError("Pizza não encontrada")
    
    preco_total = pizza['preco'] * quantidade
    
    # Inserir pedido
    cursor = conn.execute('''
        INSERT INTO pedidos (pizza_id, quantidade, nome_cliente, telefone, endereco, preco_total, data_pedido, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (pizza_id, quantidade, nome_cliente, telefone, endereco, preco_total, datetime.now(), 'pendente'))
    
    pedido_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return pedido_id

def criar_tabelas():
    """Cria as tabelas necessárias se não existirem"""
    conn = get_connection()
    
    # Tabela de pizzas
    conn.execute('''
        CREATE TABLE IF NOT EXISTS pizzas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            preco REAL NOT NULL,
            imagem TEXT,
            ativo INTEGER DEFAULT 1
        )
    ''')
    
    # Tabela de pedidos
    conn.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pizza_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            nome_cliente TEXT NOT NULL,
            telefone TEXT NOT NULL,
            endereco TEXT,
            preco_total REAL NOT NULL,
            data_pedido TEXT NOT NULL,
            status TEXT DEFAULT 'pendente',
            FOREIGN KEY (pizza_id) REFERENCES pizzas (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def inserir_pizzas_exemplo():
    """Insere pizzas apenas se a tabela estiver vazia"""
    conn = get_connection()
    cursor = conn.cursor()

    # Verifica se já tem alguma pizza
    cursor.execute("SELECT COUNT(*) FROM pizzas")
    total = cursor.fetchone()[0]

    if total == 0:
        pizzas_exemplo = [
            ('Marguerita', 'Molho de tomate, muçarela, manjericão', 52.00, 'marguerita.jpg'),
            ('Calabresa', 'Molho de tomate, muçarela, calabresa, cebola', 50.00, 'calabresa.jpg'),
            ('Frango c/ Catupiry', 'Molho de tomate, muçarela, frango, catupiry', 58.00, 'frango_catupiry.jpg'),
            ('Portuguesa', 'Molho de tomate, muçarela, presunto, ovos, cebola, ervilha', 55.00, 'portuguesa.jpg'),
            ('Quatro Queijos', 'Molho de tomate, muçarela, parmesão, provolone, gorgonzola', 60.00, 'quatro_queijos.jpg'),
            ('Presunto', 'Molho de tomate, presunto, muçarela, rodelas de tomate', 45.00, 'presunto.jpg'),
            ('Bacon', 'Molho de tomate, muçarela, bacon, rodelas de tomate', 55.00, 'bacon.jpg'),
            ('Napolitana', 'Molho de tomate, muçarela, rodelas de tomate, parmesão ralado', 60.00, 'napolitana.jpg')
        ]

        cursor.executemany("INSERT INTO pizzas (nome, descricao, preco, imagem) VALUES (?, ?, ?, ?)", pizzas_exemplo)
        conn.commit()

    conn.close()

if __name__ == '__main__':
    criar_tabelas()
    inserir_pizzas_exemplo()
    print("Banco de dados configurado com sucesso!")

import sqlite3
from datetime import datetime

DATABASE = 'pizzaria.db'

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Para acessar colunas por nome
    return conn

def get_bebidas():
    """Busca todas as bebidas disponíveis"""
    conn = get_connection()
    bebidas = conn.execute('''
        SELECT id, nome, categoria, preco, imagem 
        FROM bebidas 
        WHERE ativo = 1
        ORDER BY categoria, nome
    ''').fetchall()
    conn.close()
    
    # Converter para lista de dicionários
    return [dict(bebida) for bebida in bebidas]

def get_bebida_por_id(bebida_id):
    """Busca uma bebida específica por ID"""
    conn = get_connection()
    bebida = conn.execute('''
        SELECT id, nome, categoria, preco, imagem 
        FROM bebidas 
        WHERE id = ? AND ativo = 1
    ''', (bebida_id,)).fetchone()
    conn.close()
    
    return dict(bebida) if bebida else None

def get_bebidas_por_categoria():
    """Busca bebidas agrupadas por categoria"""
    conn = get_connection()
    bebidas = conn.execute('''
        SELECT id, nome, categoria, preco, imagem 
        FROM bebidas 
        WHERE ativo = 1
        ORDER BY categoria, nome
    ''').fetchall()
    conn.close()
    
    # Agrupar por categoria
    bebidas_por_categoria = {}
    for bebida in bebidas:
        categoria = bebida['categoria']
        if categoria not in bebidas_por_categoria:
            bebidas_por_categoria[categoria] = []
        bebidas_por_categoria[categoria].append(dict(bebida))
    
    return bebidas_por_categoria

def criar_pedido_bebida(bebida_id, quantidade, nome_cliente, telefone, endereco=None):
    """Cria um novo pedido de bebida no banco de dados"""
    conn = get_connection()
    
    # Buscar preço da bebida
    bebida = conn.execute('SELECT preco FROM bebidas WHERE id = ?', (bebida_id,)).fetchone()
    if not bebida:
        conn.close()
        raise ValueError("Bebida não encontrada")
    
    preco_total = bebida['preco'] * quantidade
    
    # Inserir pedido
    cursor = conn.execute('''
        INSERT INTO pedidos_bebidas (bebida_id, quantidade, nome_cliente, telefone, endereco, preco_total, data_pedido, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (bebida_id, quantidade, nome_cliente, telefone, endereco, preco_total, datetime.now(), 'pendente'))
    
    pedido_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return pedido_id

def criar_tabelas_bebidas():
    """Cria as tabelas necessárias para bebidas se não existirem"""
    conn = get_connection()
    
    # Tabela de bebidas
    conn.execute('''
        CREATE TABLE IF NOT EXISTS bebidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            preco REAL NOT NULL,
            imagem TEXT,
            ativo INTEGER DEFAULT 1
        )
    ''')
    
    # Tabela de pedidos de bebidas
    conn.execute('''
        CREATE TABLE IF NOT EXISTS pedidos_bebidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bebida_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            nome_cliente TEXT NOT NULL,
            telefone TEXT NOT NULL,
            endereco TEXT,
            preco_total REAL NOT NULL,
            data_pedido TEXT NOT NULL,
            status TEXT DEFAULT 'pendente',
            FOREIGN KEY (bebida_id) REFERENCES bebidas (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def inserir_bebidas_exemplo():
    """Insere bebidas apenas se a tabela estiver vazia"""
    conn = get_connection()
    cursor = conn.cursor()

    # Verifica se já tem alguma bebida
    cursor.execute("SELECT COUNT(*) FROM bebidas")
    total = cursor.fetchone()[0]

    if total == 0:
        bebidas_exemplo = [
            # Refrigerantes de lata - R$ 6,00
            ('Coca-Cola Lata', 'Refrigerante', 6.00, 'coca_cola_lata.jpg'),
            ('Pepsi Lata', 'Refrigerante', 6.00, 'pepsi_lata.jpg'),
            ('Fanta Laranja Lata', 'Refrigerante', 6.00, 'fanta_laranja_lata.jpg'),
            ('Fanta Uva Lata', 'Refrigerante', 6.00, 'fanta_uva_lata.jpg'),

            # Sucos naturais - R$ 7,50
            ('Suco de Laranja', 'Suco Natural', 7.50, 'suco_laranja.jpg'),
            ('Suco de Limão', 'Suco Natural', 7.50, 'suco_limao.jpg'),
            ('Suco de Abacaxi', 'Suco Natural', 7.50, 'suco_abacaxi.jpg'),
            ('Suco de Maracujá', 'Suco Natural', 7.50, 'suco_maracuja.jpg'),

            # Água mineral - R$ 4,00
            ('Água Mineral 500ml', 'Água', 4.00, 'agua_mineral.jpg'),
            ('Água com Gás 500ml', 'Água', 4.00, 'agua_com_gas.jpg')
        ]

        cursor.executemany('''
            INSERT INTO bebidas (nome, categoria, preco, imagem)
            VALUES (?, ?, ?, ?)
        ''', bebidas_exemplo)

        conn.commit()

    conn.close()

def criar_pedido_completo(pizza_id, bebida_id, quantidade_pizza, quantidade_bebida, nome_cliente, telefone, endereco=None):
    """Cria um pedido completo com pizza e bebida"""
    conn = get_connection()
    
    try:
        # Buscar preços
        pizza = conn.execute('SELECT preco FROM pizzas WHERE id = ?', (pizza_id,)).fetchone()
        bebida = conn.execute('SELECT preco FROM bebidas WHERE id = ?', (bebida_id,)).fetchone()
        
        if not pizza:
            raise ValueError("Pizza não encontrada")
        if not bebida:
            raise ValueError("Bebida não encontrada")
        
        preco_pizza = pizza['preco'] * quantidade_pizza
        preco_bebida = bebida['preco'] * quantidade_bebida
        preco_total = preco_pizza + preco_bebida
        
        # Inserir pedido completo
        cursor = conn.execute('''
            INSERT INTO pedidos_completos (pizza_id, bebida_id, quantidade_pizza, quantidade_bebida, 
                                         nome_cliente, telefone, endereco, preco_total, data_pedido, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (pizza_id, bebida_id, quantidade_pizza, quantidade_bebida, 
              nome_cliente, telefone, endereco, preco_total, datetime.now(), 'pendente'))
        
        pedido_id = cursor.lastrowid
        conn.commit()
        
        return pedido_id
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def criar_tabela_pedidos_completos():
    """Cria tabela para pedidos que incluem pizza e bebida"""
    conn = get_connection()
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS pedidos_completos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pizza_id INTEGER NOT NULL,
            bebida_id INTEGER,
            quantidade_pizza INTEGER NOT NULL,
            quantidade_bebida INTEGER DEFAULT 0,
            nome_cliente TEXT NOT NULL,
            telefone TEXT NOT NULL,
            endereco TEXT,
            preco_total REAL NOT NULL,
            data_pedido TEXT NOT NULL,
            status TEXT DEFAULT 'pendente',
            FOREIGN KEY (pizza_id) REFERENCES pizzas (id),
            FOREIGN KEY (bebida_id) REFERENCES bebidas (id)
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    # Importar e executar a criação das tabelas de pizza
    
    # Criar todas as tabelas
    criar_tabelas()
    criar_tabelas_bebidas()
    criar_tabela_pedidos_completos()
    
    # Inserir dados de exemplo
    inserir_pizzas_exemplo()
    inserir_bebidas_exemplo()
    
    print("Banco de dados configurado com sucesso!")
    print("Tabelas criadas: pizzas, bebidas, pedidos, pedidos_bebidas, pedidos_completos")
    
    # Mostrar bebidas cadastradas
    print("\nBebidas cadastradas:")
    bebidas = get_bebidas_por_categoria()
    for categoria, lista_bebidas in bebidas.items():
        print(f"\n{categoria}:")
        for bebida in lista_bebidas:
            print(f"  - {bebida['nome']}: R$ {bebida['preco']:.2f}")
def obter_id_pizza_por_nome(nome):
    conn = get_connection()
    pizza = conn.execute('SELECT id FROM pizzas WHERE nome = ? AND ativo = 1', (nome,)).fetchone()
    conn.close()
    return pizza['id'] if pizza else None

def obter_id_bebida_por_nome(nome):
    conn = get_connection()
    bebida = conn.execute('SELECT id FROM bebidas WHERE nome = ? AND ativo = 1', (nome,)).fetchone()
    conn.close()
    return bebida['id'] if bebida else None
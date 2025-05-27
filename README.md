Pizzaria Calabresos
Trabalho desenvolvido para a disciplina de Estrutura de Dados, com o objetivo de implementar um sistema web de pedidos online para uma pizzaria. O projeto aplica conceitos fundamentais de estrutura de dados (listas, dicionários, ordenação) e banco de dados relacional, integrados em um sistema moderno com interface gráfica para o usuário.

 Descrição do Projeto
O sistema simula o funcionamento de uma pizzaria digital chamada Pizzaria Calabresos, permitindo que o cliente:

Visualize o cardápio com pizzas e bebidas (com imagens, descrição e preço);

Selecione os itens desejados e monte seu pedido;

Informe seus dados pessoais (nome, telefone e endereço);

Envie o pedido para a pizzaria;

Visualize uma página de confirmação com o resumo do pedido.

Tecnologias Utilizadas:

Python 3.x

Flask (Python) – servidor web e gerenciamento de rotas da API

SQLite – banco de dados relacional leve, armazenando pizzas, bebidas e pedidos

HTML + CSS – estrutura visual e estilo das páginas

JavaScript (DOM + Fetch API) – manipulação dinâmica da interface e comunicação com o backend

Bootstrap + estilos customizados – layout responsivo e moderno

Estrutura dos Arquivos

/pizzaria_calabresos/
├── app.py
├── db.py
├── pedido.py
├── pizzaria.py
├── pizzaria.db
├── cardapio.pickle
├── pedidos.pickle
├── requirements.txt
├── /templates/
│   ├── pedido.html
│   └── pedido_confirmado.html
├── /static/
│   ├── css/
│   │   └── style.css
│   └── images/
└── __pycache__/

Instruções de Execução

1-Instale os pacotes necessários:
dê cd .\pizza-gh-pages
depois:
pip install flask
depois:
pip install -r requirements.txt

2-Execute o servidor:
python app.py ou flask run

Integrantes do grupo:
Carlos Eduardo Alves Teixeira de Oliveira

Pedro Canellas de Sousa Alcantara

Luiz Filipe Estrela Lara

3-Acesse no navegador:
http://127.0.0.1:5000



# Projeto E-commerce com Microserviços

Este é um projeto de e-commerce desenvolvido com arquitetura de microserviços utilizando Python Flask, Docker e Docker Compose.

## Arquitetura

O projeto é composto pelos seguintes microserviços:

1. **API Gateway** (Porta 5000): Ponto de entrada para todos os serviços
2. **Serviço de Itens** (Porta 5001): Gerencia o catálogo de produtos
3. **Serviço de Pedidos** (Porta 5002): Gerencia os pedidos dos clientes
4. **Serviço de Usuários** (Porta 5003): Gerencia os usuários e autenticação

## Requisitos

- Docker
- Docker Compose

## Como executar

Para iniciar todos os serviços:

```bash
cd NODO-PROJETO-DO-ZERO
docker-compose up --build
```

Para executar em segundo plano:

```bash
docker-compose up -d --build
```

## Endpoints disponíveis

### API Gateway

- `GET /`: Verificar status do API Gateway
- `GET /health`: Verificar status de saúde de todos os serviços

### Serviço de Itens

- `GET /api/itens`: Listar todos os itens
- `GET /api/itens/<id>`: Obter item específico
- `POST /api/itens`: Criar novo item
- `PUT /api/itens/<id>`: Atualizar item
- `DELETE /api/itens/<id>`: Remover item

### Serviço de Pedidos

- `GET /api/pedidos`: Listar todos os pedidos
- `GET /api/pedidos/<id>`: Obter pedido específico
- `GET /api/pedidos/usuario/<usuario_id>`: Listar pedidos de um usuário
- `POST /api/pedidos`: Criar novo pedido
- `PATCH /api/pedidos/<id>/status`: Atualizar status de um pedido
- `DELETE /api/pedidos/<id>`: Cancelar pedido

### Serviço de Usuários

- `GET /api/usuarios`: Listar todos os usuários
- `GET /api/usuarios/<id>`: Obter usuário específico
- `POST /api/usuarios`: Cadastrar novo usuário
- `PUT /api/usuarios/<id>`: Atualizar usuário
- `DELETE /api/usuarios/<id>`: Remover usuário
- `POST /api/auth/login`: Realizar login
- `POST /api/auth/verificar`: Verificar token de autenticação
- `POST /api/auth/logout`: Realizar logout

## Testes

### Serviço de Itens

Listar todos os itens:
```bash
curl http://localhost:5000/api/itens/
```

### Serviço de Usuários

Fazer login com usuário padrão:
```bash
curl -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -d '{"email": "usuario@teste.com", "senha": "senha123"}'
```

### Serviço de Pedidos

Criar um novo pedido (necessita token de autenticação):
```bash
curl -X POST http://localhost:5000/api/pedidos -H "Content-Type: application/json" -d '{"usuario_id": 1, "itens": [{"item_id": 1, "quantidade": 1, "preco_unitario": 4999.90}]}'
```

## Estrutura de dados

Todas as informações são armazenadas em arquivos JSON para simplificar o projeto. Em um ambiente de produção, você deve considerar usar bancos de dados adequados para cada microserviço.

## Volumes

Os dados são armazenados em volumes Docker para persistência:
- `./data/itens`: Dados do serviço de itens
- `./data/pedidos`: Dados do serviço de pedidos
- `./data/usuarios`: Dados do serviço de usuários
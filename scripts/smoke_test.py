#!/usr/bin/env python3
"""Teste de ponta a ponta pelo API Gateway (só biblioteca padrão).

Uso: docker compose up -d --build && python3 scripts/smoke_test.py
"""
import json
import os
import sys
import urllib.error
import urllib.request

API = os.environ.get('API_URL', 'http://localhost:5000')
falhas = 0


def chamar(metodo, caminho, corpo=None, token=None, headers=None):
    req = urllib.request.Request(f'{API}{caminho}', method=metodo, data=json.dumps(corpo).encode() if corpo is not None else None)
    req.add_header('Content-Type', 'application/json')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read() or b'{}')
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b'{}')


def checar(descricao, condicao):
    global falhas
    print(f"{'ok ' if condicao else 'FALHOU'}  {descricao}")
    falhas += not condicao


status, saude = chamar('GET', '/health')
checar('gateway e os três serviços online', status == 200 and set(saude['services'].values()) == {'online'})

status, catalogo = chamar('GET', '/api/itens')
checar('catálogo público', status == 200 and len(catalogo['itens']) > 0)

checar('pedidos exigem login', chamar('GET', '/api/pedidos')[0] == 401)
checar('lista de usuários exige login', chamar('GET', '/api/usuarios')[0] == 401)
checar('senha errada é recusada', chamar('POST', '/api/auth/login', {'email': 'cliente@lumestore.dev', 'senha': 'errada'})[0] == 401)

_, login = chamar('POST', '/api/auth/login', {'email': 'cliente@lumestore.dev', 'senha': 'senha123'})
token = login.get('token')
checar('login do cliente', bool(token))

checar('cliente não lista usuários', chamar('GET', '/api/usuarios', token=token)[0] == 403)
checar('header de admin forjado é ignorado',
       chamar('GET', '/api/usuarios', token=token, headers={'X-Usuario-Admin': '1', 'X-Usuario-Id': '1'})[0] == 403)
checar('cliente não cadastra produto', chamar('POST', '/api/itens', {'nome': 'x', 'preco': 1}, token=token)[0] == 403)

item = catalogo['itens'][0]
status, pedido = chamar('POST', '/api/pedidos', {'itens': [{'item_id': item['id'], 'quantidade': 1, 'preco_unitario': 0.01}]}, token=token)
checar('pedido criado com o preço do catálogo (não o do cliente)', status == 201 and pedido['valor_total'] == item['preco'])
checar('estoque reservado', chamar('GET', f"/api/itens/{item['id']}")[1]['estoque'] == item['estoque'] - 1)

status, _ = chamar('POST', '/api/pedidos', {'itens': [{'item_id': item['id'], 'quantidade': 10**6}]}, token=token)
checar('estoque insuficiente é recusado', status == 409)

status, cancelado = chamar('DELETE', f"/api/pedidos/{pedido['id']}", token=token)
checar('cancelamento devolve o estoque', status == 200 and cancelado['status'] == 'cancelado'
       and chamar('GET', f"/api/itens/{item['id']}")[1]['estoque'] == item['estoque'])

_, admin = chamar('POST', '/api/auth/login', {'email': 'admin@lumestore.dev', 'senha': 'admin123'})
checar('admin lista usuários', chamar('GET', '/api/usuarios', token=admin.get('token'))[0] == 200)

print('\nTudo certo.' if not falhas else f'\n{falhas} verificação(ões) falharam.')
sys.exit(1 if falhas else 0)

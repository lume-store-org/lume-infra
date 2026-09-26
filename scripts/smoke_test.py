#!/usr/bin/env python3
"""End-to-end test through the API Gateway (standard library only).

Usage: docker compose up -d --build && python3 scripts/smoke_test.py
"""
import json
import os
import sys
import urllib.error
import urllib.request

API = os.environ.get('API_URL', 'http://localhost:5000')
failures = 0


def call(method, path, body=None, token=None, headers=None):
    req = urllib.request.Request(f'{API}{path}', method=method, data=json.dumps(body).encode() if body is not None else None)
    req.add_header('Content-Type', 'application/json')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read() or b'{}')
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b'{}')


def check(description, condition):
    global failures
    print(f"{'ok ' if condition else 'FAIL'}  {description}")
    failures += not condition


status, health = call('GET', '/health')
check('gateway and the three services are online', status == 200 and set(health['services'].values()) == {'online'})

status, catalog = call('GET', '/api/products')
check('public catalog', status == 200 and len(catalog['products']) > 0)

check('orders require login', call('GET', '/api/orders')[0] == 401)
check('user list requires login', call('GET', '/api/users')[0] == 401)
check('wrong password is rejected', call('POST', '/api/auth/login', {'email': 'cliente@lumestore.dev', 'password': 'wrong'})[0] == 401)

_, login = call('POST', '/api/auth/login', {'email': 'cliente@lumestore.dev', 'password': 'senha123'})
token = login.get('token')
check('customer login', bool(token))

check('customer cannot list users', call('GET', '/api/users', token=token)[0] == 403)
check('forged admin header is ignored',
      call('GET', '/api/users', token=token, headers={'X-User-Admin': '1', 'X-User-Id': '1'})[0] == 403)
check('customer cannot create products', call('POST', '/api/products', {'name': 'x', 'price': 1}, token=token)[0] == 403)

product = catalog['products'][0]
status, order = call('POST', '/api/orders', {'items': [{'product_id': product['id'], 'quantity': 1, 'unit_price': 0.01}]}, token=token)
check('order uses the catalog price (not the client one)', status == 201 and order['total'] == product['price'])
check('stock reserved', call('GET', f"/api/products/{product['id']}")[1]['stock'] == product['stock'] - 1)

status, _ = call('POST', '/api/orders', {'items': [{'product_id': product['id'], 'quantity': 10**6}]}, token=token)
check('not enough stock is rejected', status == 409)

status, cancelled = call('DELETE', f"/api/orders/{order['id']}", token=token)
check('cancelling releases the stock', status == 200 and cancelled['status'] == 'cancelled'
      and call('GET', f"/api/products/{product['id']}")[1]['stock'] == product['stock'])

_, admin = call('POST', '/api/auth/login', {'email': 'admin@lumestore.dev', 'password': 'admin123'})
check('admin lists users', call('GET', '/api/users', token=admin.get('token'))[0] == 200)

print('\nAll good.' if not failures else f'\n{failures} check(s) failed.')
sys.exit(1 if failures else 0)

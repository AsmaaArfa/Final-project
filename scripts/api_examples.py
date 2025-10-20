#!/usr/bin/env python3
"""Run example API requests against the running FastAPI server.

Steps:
- GET /patients
- POST /auth/register (create a user)
- Promote the user to 'admin' via direct DB access
- POST /auth/token to obtain access token
- POST /patients to create a patient with admin token

Run with:
PYTHONPATH=. ./scripts/api_examples.py
"""
import urllib.request
import urllib.parse
import json
import sys
import time

BASE = 'http://127.0.0.1:8001/adsweb/api/v1'

def http_get(path):
    url = BASE + path
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, resp.read().decode()

def http_post(path, data=None, headers=None):
    url = BASE + path
    body = None
    hdrs = headers or {}
    if data is not None:
        if hdrs.get('Content-Type') == 'application/json':
            body = json.dumps(data).encode()
        else:
            body = urllib.parse.urlencode(data).encode()
            hdrs.setdefault('Content-Type', 'application/x-www-form-urlencoded')
    req = urllib.request.Request(url, data=body, headers=hdrs, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as he:
        try:
            err = he.read().decode()
        except Exception:
            err = ''
        return he.code, err


def main():
    print('1) GET /patients')
    status, body = http_get('/patients')
    print('status', status)
    try:
        parsed = json.loads(body)
        print('patients_count', len(parsed))
        if len(parsed):
            print('first_patient', parsed[0])
    except Exception:
        print('raw', body[:400])

    # register a new user
    username = 'cliuser'
    email = f'{username}@example.com'
    password = 'clipass'
    print('\n2) POST /auth/register (create user)', username)
    qs = urllib.parse.urlencode({'username': username, 'email': email, 'password': password})
    status, body = http_post('/auth/register?' + qs)
    print('status', status, 'body', body)

    # promote user to admin via DB
    print('\n3) Promote user to admin via DB')
    try:
        # import DB and models
        from code.database import get_session
        from code import crud, models
        db = get_session()
        try:
            user = db.query(models.User).filter_by(username=username).first()
            if not user:
                print('user not found in DB')
            admin = db.query(models.Role).filter_by(name='admin').first()
            if not admin:
                admin = crud.create_role(db, name='admin', description='Administrator')
            if user and not any(r.name == 'admin' for r in user.roles):
                user.roles.append(admin)
                db.commit()
                print('promoted', username)
            else:
                print('already admin or user missing')
        finally:
            db.close()
    except Exception as e:
        print('DB promotion failed:', e)
        sys.exit(1)

    # obtain token
    print('\n4) POST /auth/token (obtain token)')
    status, body = http_post('/auth/token', data={'username': username, 'password': password})
    print('status', status)
    try:
        token = json.loads(body).get('access_token')
        print('token_len', len(token) if token else None)
    except Exception:
        print('token response', body)
        sys.exit(1)

    # create a patient using token
    print('\n5) POST /patients (create patient)')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    patient = {'first_name': 'CLI', 'last_name': 'Test', 'email': 'cli.test@example.com'}
    status, body = http_post('/patients', data=patient, headers=headers)
    print('status', status)
    print('body', body)

if __name__ == '__main__':
    main()

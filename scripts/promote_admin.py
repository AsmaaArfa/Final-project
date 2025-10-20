#!/usr/bin/env python
"""Promote a user to admin role.
Usage: python scripts/promote_admin.py <username>
"""
import sys
from code.database import get_session
from code import crud, models

if len(sys.argv) < 2:
    print('usage: promote_admin.py <username>')
    sys.exit(2)

username = sys.argv[1]

db = get_session()
try:
    user = db.query(models.User).filter_by(username=username).first()
    if not user:
        print('user not found')
        sys.exit(1)
    admin = db.query(models.Role).filter_by(name='admin').first()
    if not admin:
        admin = crud.create_role(db, name='admin', description='Administrator')
    if not any(r.name == 'admin' for r in user.roles):
        user.roles.append(admin)
        db.commit()
        print(f'promoted {username} to admin')
    else:
        print(f'{username} already admin')
finally:
    db.close()

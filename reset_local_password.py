"""Local-only recovery for an existing Reflect password account.

Run while the local Reflect server is stopped. Never deploy this script.
"""
import getpass
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from server import DB_PATH, hash_password

path = Path(DB_PATH).resolve()
if not path.exists():
    raise SystemExit('Database not found. No changes made.')
print('Database:', path)
email = input('Existing account email: ').strip().lower()
with sqlite3.connect(path) as db:
    account = db.execute('SELECT id, name FROM users WHERE email=?', (email,)).fetchone()
if not account:
    raise SystemExit('Account not found in this database. No changes made.')
print('Account found:', account[1])
new_password = getpass.getpass('New password (8–128 characters): ')
confirmation = getpass.getpass('Confirm new password: ')
if new_password != confirmation or not 8 <= len(new_password) <= 128:
    raise SystemExit('Passwords do not match or length is invalid. No changes made.')
backup = path.with_name('reflect_backup_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.sqlite3')
# sqlite backup API captures committed transactions even in WAL mode.
with sqlite3.connect(path) as source, sqlite3.connect(backup) as target:
    source.backup(target)
print('Database backup:', backup)
with sqlite3.connect(path) as db:
    db.execute('UPDATE users SET passhash=? WHERE id=?', (hash_password(new_password), account[0]))
    db.execute('DELETE FROM sessions WHERE user_id=?', (account[0],))
print('Password updated, previous sessions signed out. Other user data unchanged.')

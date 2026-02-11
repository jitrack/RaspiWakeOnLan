import sqlite3
from config import DATABASE_PATH


def get_db():
    """Retourne une connexion SQLite avec row_factory."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crée la table et insère les 7 jours par défaut si absents."""
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            id          INTEGER PRIMARY KEY,
            day_of_week INTEGER NOT NULL UNIQUE,   -- 0=Lundi … 6=Dimanche
            start_time  TEXT    DEFAULT '08:00',    -- HH:MM
            stop_time   TEXT    DEFAULT '22:00',    -- HH:MM
            enabled     INTEGER DEFAULT 0           -- 0=inactif, 1=actif
        )
    ''')
    for day in range(7):
        exists = conn.execute(
            'SELECT 1 FROM schedules WHERE day_of_week = ?', (day,)
        ).fetchone()
        if not exists:
            conn.execute(
                'INSERT INTO schedules (day_of_week, start_time, stop_time, enabled) '
                'VALUES (?, ?, ?, ?)',
                (day, '08:00', '22:00', 0),
            )
    conn.commit()
    conn.close()


def get_schedules():
    """Retourne les 7 planifications ordonnées lundi→dimanche."""
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM schedules ORDER BY day_of_week'
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_schedule(day_of_week: int, start_time: str, stop_time: str, enabled: bool):
    """Met à jour la planification d'un jour donné."""
    conn = get_db()
    conn.execute(
        'UPDATE schedules SET start_time = ?, stop_time = ?, enabled = ? '
        'WHERE day_of_week = ?',
        (start_time, stop_time, int(enabled), day_of_week),
    )
    conn.commit()
    conn.close()

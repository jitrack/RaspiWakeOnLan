import sqlite3
from datetime import datetime
from config import DATABASE_PATH


def get_db():
    """Returns a SQLite connection with row_factory."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Creates tables and inserts default 7 days if absent."""
    conn = get_db()
    
    # Weekly schedule table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            id          INTEGER PRIMARY KEY,
            day_of_week INTEGER NOT NULL UNIQUE,   -- 0=Monday … 6=Sunday
            start_time  TEXT    DEFAULT '08:00',    -- HH:MM
            stop_time   TEXT    DEFAULT '22:00',    -- HH:MM
            enabled     INTEGER DEFAULT 0           -- 0=disabled, 1=enabled
        )
    ''')
    
    # One-time scheduled shutdowns
    conn.execute('''
        CREATE TABLE IF NOT EXISTS scheduled_shutdowns (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            scheduled_at    TEXT NOT NULL,          -- ISO datetime
            created_at      TEXT NOT NULL,
            executed        INTEGER DEFAULT 0       -- 0=pending, 1=executed
        )
    ''')
    
    # Action tracking (for timeout detection)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS action_tracking (
            id          INTEGER PRIMARY KEY CHECK (id = 1),  -- Single row
            action_type TEXT NOT NULL,              -- 'start' or 'stop'
            started_at  TEXT NOT NULL               -- ISO datetime
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
    """Returns the 7 schedules ordered Monday→Sunday."""
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM schedules ORDER BY day_of_week'
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_schedule(day_of_week: int, start_time: str, stop_time: str, enabled: bool):
    """Updates the schedule for a given day."""
    conn = get_db()
    conn.execute(
        'UPDATE schedules SET start_time = ?, stop_time = ?, enabled = ? '
        'WHERE day_of_week = ?',
        (start_time, stop_time, int(enabled), day_of_week),
    )
    conn.commit()
    conn.close()


def add_scheduled_shutdown(scheduled_at: str):
    """Add a one-time scheduled shutdown."""
    conn = get_db()
    now = datetime.now().isoformat()
    conn.execute(
        'INSERT INTO scheduled_shutdowns (scheduled_at, created_at) VALUES (?, ?)',
        (scheduled_at, now)
    )
    conn.commit()
    conn.close()


def get_pending_shutdowns():
    """Get all pending scheduled shutdowns (and cleanup expired ones)."""
    conn = get_db()
    
    # Delete expired shutdowns (more than 1 minute in the past)
    now = datetime.now()
    rows = conn.execute(
        'SELECT * FROM scheduled_shutdowns WHERE executed = 0'
    ).fetchall()
    
    for row in rows:
        scheduled_dt = datetime.fromisoformat(row['scheduled_at'])
        if scheduled_dt < now:
            elapsed = (now - scheduled_dt).total_seconds()
            # Delete if expired by more than 60 seconds
            if elapsed > 60:
                conn.execute('DELETE FROM scheduled_shutdowns WHERE id = ?', (row['id'],))
    
    conn.commit()
    
    # Return remaining pending shutdowns
    rows = conn.execute(
        'SELECT * FROM scheduled_shutdowns WHERE executed = 0 ORDER BY scheduled_at'
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def mark_shutdown_executed(shutdown_id: int):
    """Mark a scheduled shutdown as executed."""
    conn = get_db()
    conn.execute(
        'UPDATE scheduled_shutdowns SET executed = 1 WHERE id = ?',
        (shutdown_id,)
    )
    conn.commit()
    conn.close()


def delete_scheduled_shutdown(shutdown_id: int):
    """Delete a scheduled shutdown."""
    conn = get_db()
    conn.execute('DELETE FROM scheduled_shutdowns WHERE id = ?', (shutdown_id,))
    conn.commit()
    conn.close()


def set_action_in_progress(action_type: str):
    """Record that an action (start/stop) is in progress."""
    conn = get_db()
    now = datetime.now().isoformat()
    conn.execute(
        'INSERT OR REPLACE INTO action_tracking (id, action_type, started_at) VALUES (1, ?, ?)',
        (action_type, now)
    )
    conn.commit()
    conn.close()


def get_action_in_progress():
    """Get current action in progress, or None if none/expired."""
    conn = get_db()
    row = conn.execute('SELECT * FROM action_tracking WHERE id = 1').fetchone()
    conn.close()
    
    if not row:
        return None
    
    started_at = datetime.fromisoformat(row['started_at'])
    now = datetime.now()
    elapsed = (now - started_at).total_seconds()
    
    # 60 second timeout
    if elapsed > 60:
        return None
    
    return {
        'action_type': row['action_type'],
        'started_at': row['started_at'],
        'elapsed': elapsed
    }


def clear_action_in_progress():
    """Clear the action tracking."""
    conn = get_db()
    conn.execute('DELETE FROM action_tracking WHERE id = 1')
    conn.commit()
    conn.close()

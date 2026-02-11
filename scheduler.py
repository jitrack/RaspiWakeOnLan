import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from database import get_schedules
from nas_controller import wake_nas, shutdown_nas

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(daemon=True)

DAY_CRON = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']


def _start_job():
    logger.info('⏰ Tâche planifiée : démarrage du NAS')
    wake_nas()


def _stop_job():
    logger.info('⏰ Tâche planifiée : arrêt du NAS')
    shutdown_nas()


def reload_schedules():
    """Supprime les anciens jobs et recharge depuis la BDD."""
    # Supprimer les jobs existants liés au planning
    for job in scheduler.get_jobs():
        if job.id.startswith('sched_'):
            job.remove()

    for row in get_schedules():
        if not row['enabled']:
            continue

        day = DAY_CRON[row['day_of_week']]

        if row['start_time']:
            h, m = row['start_time'].split(':')
            scheduler.add_job(
                _start_job,
                CronTrigger(day_of_week=day, hour=int(h), minute=int(m)),
                id=f"sched_start_{row['day_of_week']}",
                replace_existing=True,
            )

        if row['stop_time']:
            h, m = row['stop_time'].split(':')
            scheduler.add_job(
                _stop_job,
                CronTrigger(day_of_week=day, hour=int(h), minute=int(m)),
                id=f"sched_stop_{row['day_of_week']}",
                replace_existing=True,
            )

    logger.info(
        'Planifications rechargées – %d jobs actifs',
        len([j for j in scheduler.get_jobs() if j.id.startswith('sched_')]),
    )


def init_scheduler():
    """Charge les planifications et démarre le scheduler."""
    reload_schedules()
    if not scheduler.running:
        scheduler.start()
        logger.info('Scheduler démarré')

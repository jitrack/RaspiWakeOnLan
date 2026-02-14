import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

from database import get_schedules, get_pending_shutdowns, mark_shutdown_executed
from nas_controller import wake_nas, shutdown_nas

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(daemon=True)

DAY_CRON = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']


def _start_job():
    logger.info('⏰ Scheduled task: starting NAS')
    wake_nas()


def _stop_job():
    logger.info('⏰ Scheduled task: stopping NAS')
    shutdown_nas()


def _one_time_shutdown(shutdown_id: int):
    logger.info('⏰ One-time scheduled shutdown: %d', shutdown_id)
    shutdown_nas()
    mark_shutdown_executed(shutdown_id)


def reload_schedules():
    """Remove old jobs and reload from DB."""
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
        'Schedules reloaded – %d active jobs',
        len([j for j in scheduler.get_jobs() if j.id.startswith('sched_')]),
    )


def reload_one_time_shutdowns():
    """Load pending one-time shutdowns."""
    for job in scheduler.get_jobs():
        if job.id.startswith('onetime_'):
            job.remove()

    for row in get_pending_shutdowns():
        scheduled_dt = datetime.fromisoformat(row['scheduled_at'])
        if scheduled_dt > datetime.now():
            scheduler.add_job(
                _one_time_shutdown,
                DateTrigger(run_date=scheduled_dt),
                args=[row['id']],
                id=f"onetime_{row['id']}",
                replace_existing=True,
            )
            logger.info('One-time shutdown scheduled: %s (ID %d)', row['scheduled_at'], row['id'])


def init_scheduler():
    """Load schedules and start the scheduler."""
    reload_schedules()
    reload_one_time_shutdowns()
    if not scheduler.running:
        scheduler.start()
        logger.info('Scheduler started')

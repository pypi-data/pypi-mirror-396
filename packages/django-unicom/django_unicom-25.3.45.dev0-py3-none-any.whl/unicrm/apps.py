import os
import sys

from django.apps import AppConfig
from django.conf import settings


def _should_start_scheduler() -> bool:
    if not getattr(settings, 'UNICRM_AUTO_START_SCHEDULER', True):
        return False

    # Explicit opt-out
    if getattr(settings, 'UNICRM_DISABLE_GP_POLLER', False):
        return False

    argv = sys.argv or []
    entrypoint = (argv[0] or '').lower()
    args = [a.lower() for a in argv[1:]]

    # Skip known non-server commands
    skip_cmds = {
        'migrate',
        'makemigrations',
        'collectstatic',
        'shell',
        'shell_plus',
        'test',
        'dbshell',
        'createsuperuser',
        'loaddata',
    }
    if 'PYTEST_CURRENT_TEST' in os.environ:
        return False

    if len(argv) > 1 and argv[1] in skip_cmds:
        return False

    # Avoid worker/queue processes
    if any(arg for arg in args if 'celery' in arg or 'rqworker' in arg):
        return False

    # Avoid pytest invocation
    if 'pytest' in entrypoint or any('pytest' in a for a in args):
        return False

    # If we detect common server binaries or runserver, enable
    server_names = ('daphne', 'gunicorn', 'uvicorn', 'asgiref', 'asgi', 'runserver')
    if any(name in entrypoint for name in server_names):
        return True
    if any(name in args for name in server_names):
        return True

    # Fallback: assume True (web container often hides argv)
    return True


class UnicrmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'unicrm'

    def ready(self):
        from . import signals  # noqa: F401
        # Register save_new_leads callback handlers (cross-platform buttons)
        from unicrm.services import save_new_leads_callbacks  # noqa: F401

        if _should_start_scheduler():
            from unicrm.services.communication_runner import communication_scheduler_runner
            from unicrm.services.getprospect_email_poller import getprospect_email_poller

            interval = getattr(settings, 'UNICRM_SCHEDULER_INTERVAL', 10)
            communication_scheduler_runner.start(interval=interval)
            # Start the GetProspect email poller (separate interval)
            gp_interval = getattr(settings, 'UNICRM_GP_POLL_INTERVAL', 60)
            getprospect_email_poller.start(interval=gp_interval)

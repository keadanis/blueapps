import logging

logger = logging.getLogger(__name__)


def migrate(cr, version):
    # Change data ownwer
    tables = [
        'nibbana_area', 'nibbana_area_project', 'nibbana_area_reference',
        'nibbana_area_task', 'nibbana_context', 'nibbana_context_project',
        'nibbana_context_task', 'nibbana_inbox',
        'nibbana_project', 'nibbana_project_area', 'nibbana_project_inactive',
        'nibbana_reference', 'nibbana_schedule_task', 'nibbana_settings',
        'nibbana_task', 'nibbana_timeline', 'nibbana_waiting_task',
    ]
    for t in tables:
        cr.execute(
            "UPDATE {0} SET create_uid = 2 WHERE create_uid = 1".format(t))

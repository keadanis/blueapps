# ©️ OdooPBX by Odooist, Odoo Proprietary License v1.0, 2020
import json
import logging

import psycopg2
from odoo.tools import mute_logger

from odoo import models, fields, api, registry, SUPERUSER_ID, _
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


DEFAULT_EXPIRE_SECONDS = 3600 * 24  # One day


class Cache(models.Model):
    """
    Simple key/value storage with expiration feature.
    Duplicate keys are accepted but get returns the first key.
    """
    # TODO: ORM Cache

    _name = 'kv_cache.cache'
    _description = 'Cache Impementation'
    _log = False  # TODO: Check that auto disables special fields

    key = fields.Char(required=True, index=True)
    tag = fields.Char(required=True, default='/', index=True)
    value = fields.Char(required=True)
    expire = fields.Datetime(required=True, index=True)

    _sql_constraints = [
        ('tag_key_uniq', 'unique (tag,key)',
            _('The key/tag must be unique !')),
    ]

    @api.model
    def put(self, key, value, tag='/', expire=DEFAULT_EXPIRE_SECONDS,
            serialize=None, new_env=False, overwrite_existing=True):
        self.do_expiration()
        try:
            expire_time = (datetime.utcnow() + timedelta(
                seconds=expire)).strftime('%Y-%m-%d %H:%M:%S')
            # Check serialize option
            if serialize == 'json':
                value = json.dumps(value)
            if not new_env:
                with mute_logger('odoo.sql_db'), self.env.cr.savepoint():
                    self.create({
                        'key': key,
                        'tag': tag,
                        'value': value,
                        'expire': expire_time,
                    })
                    logger.debug('CACHE PUT KEY: %s VALUE: %s', key, value)
            else:
                with mute_logger('odoo.sql_db'), api.Environment.manage():
                    with registry(self.env.cr.dbname).cursor() as new_cr:
                        env = api.Environment(
                            new_cr, self.env.uid, self.env.context)
                        env['kv_cache.cache'].create({
                            'key': key,
                            'tag': tag,
                            'value': value,
                            'expire': expire_time,
                        })
                        env.cr.commit()
                logger.debug('CACHE NEW ENV PUT KEY: %s VALUE: %s', key, value)
        except psycopg2.IntegrityError as e:
            if e.pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION:
                if not new_env:
                    with self.env.cr.savepoint():
                        # Find duplicate record to update
                        cache_record = self.env['kv_cache.cache'].search([('key', '=', key), ('tag', '=', tag)])
                        cache_record.update({
                            'key': key,
                            'tag': tag,
                            'value': value,
                            'expire': expire_time,
                        })
                        logger.debug('CACHE UPDATE KEY: %s VALUE: %s', key, value)
                else:
                    with api.Environment.manage():
                        with registry(self.env.cr.dbname).cursor() as new_cr:
                            env = api.Environment(
                                new_cr, self.env.uid, self.env.context)
                            cache_record = env['kv_cache.cache'].search([('key', '=', key), ('tag', '=', tag)])
                            cache_record.update({
                                'key': key,
                                'tag': tag,
                                'value': value,
                                'expire': expire_time,
                            })
                            env.cr.commit()
                    logger.debug('CACHE NEW ENV UPDATE KEY: %s VALUE: %s', key, value)
        except Exception:
            logger.exception('[ODOO_ERROR] CACHE PUT ERROR')
            raise Exception('CACHE PUT ERROR')

    @api.model
    def get(self, key, tag='/', clean=False, serialize=None):
        try:
            now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            res = self.search([('tag', '=', tag), ('key', '=', key),
                               ('expire', '>=', now)])
            if res:
                val = res[0].value
                # Check for serialize
                if serialize == 'json':
                    val = json.loads(val)
                if clean:
                    res.unlink()
                logger.debug('CACHE GET KEY: %s, CLEAN: %s, VALUE: %s.',
                             key, clean, val)
                return val
            else:
                logger.debug('CACHE TAG %s KEY %s NOT FOUND', tag, key)
                return {} if serialize == 'json' else False
        except Exception:
            logger.exception('[ODOO_ERROR] CACHE GET ERROR:')
            return {} if serialize == 'json' else False

    @api.model
    def delete(self, key, tag='/'):
        self.do_expiration()
        try:
            with self.env.cr.savepoint():
                res = self.search([('tag', '=', tag), ('key', '=', key)])
                if res:
                    res.unlink()
                else:
                    logger.debug('KEY %s NOT FOUND UNDER TAG: %s', key, tag)
        except Exception:
            logger.exception('[ODOO_ERROR] CACHE DELETE ERROR:')

    @api.model
    def do_expiration(self):
        try:
            now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            with self.env.cr.savepoint():
                expired_recs = self.search(
                    [('expire', '<', now)])
                logger.debug('CACHE VACUUM %s RECORDS', len(expired_recs))
                expired_recs.unlink()
        except Exception:
            logger.exception('[ODOO_ERROR] CACHE DO EXPIRATION ERROR:')

import datetime
import logging
import os
import time

from bottle import request
from bottle_utils.i18n import i18n_url

from librarian_content.library.archive import Archive
from librarian_lock.lock import global_lock
from librarian_core.contrib.databases.helpers import (get_database_configs,
                                                      migrate)

from .backup import backup


DB_NAME = 'content'


def get_dbpath():
    conf = request.app.config
    db_configs = get_database_configs(conf)
    return db_configs[DB_NAME]['path']


def get_backup_dir():
    conf = request.app.config
    backupdir = os.path.normpath(conf['dbmanage.backupdir'])
    if not os.path.exists(backupdir):
        os.makedirs(backupdir)
    return backupdir


def get_backup_path():
    backupdir = get_backup_dir()
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = 'db_backup_%s.sqlite' % timestamp
    return os.path.join(backupdir, filename)


def get_file_url():
    suburl = request.app.config['dbmanage.backupdir'].replace('\\', '/')
    return i18n_url('files:path', path=suburl)


def remove_dbfile():
    dbpath = get_dbpath()
    paths = [dbpath, dbpath + '-wal', dbpath + '-shm']
    for p in paths:
        try:
            os.unlink(p)
        except OSError:
            pass
        finally:
            assert not os.path.exists(p), 'Expected db file to be gone'


def run_migrations(db, db_config):
    conf = request.app.config
    migration_pkg = '{0}.migrations.{1}'.format(db_config['package_name'],
                                                DB_NAME)
    migrate(db, migration_pkg, conf)
    logging.debug("Finished running migrations")


def rebuild():
    conf = request.app.config
    db_configs = get_database_configs(conf)
    dbpath = db_configs[DB_NAME]['path']
    bpath = get_backup_path()
    start = time.time()
    db = request.db.content
    logging.debug('Locking database')
    db.acquire_lock()
    logging.debug('Acquiring global lock')
    with global_lock(always_release=True):
        db.commit()
        db.close()
        backup(dbpath, bpath)
        remove_dbfile()
        logging.debug('Removed database')
        db.reconnect()
        run_migrations(db, db_configs[DB_NAME])
        logging.debug('Prepared new database')
        archive = Archive.setup(conf['library.backend'],
                                request.app.supervisor.exts.fsal,
                                db,
                                contentdir=conf['library.contentdir'],
                                meta_filenames=conf['library.metadata'])
        rows = archive.reload_content()
        logging.info('Restored metadata for %s pieces of content', rows)
    request.app.supervisor.exts.cache.invalidate('content')
    logging.debug('Released global lock')
    end = time.time()
    return end - start

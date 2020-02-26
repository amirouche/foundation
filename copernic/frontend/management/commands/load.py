import json
from uuid import UUID

import fdb
from django.core.management.base import BaseCommand, CommandError

import vnstore
import nstore
from frontend.models import ChangeRequest


fdb.api_version(620)
db = fdb.open()


ITEMS = ['uid', 'key', 'value']

var = nstore.var
# nstore contain the latest version snapshot
nstore = nstore.open(['copernic', 'nstore'], ITEMS)
# vnstore contains the versioned ITEMS
vnstore = vnstore.open(['copernic', 'vnstore'], ITEMS)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('filename')
        parser.add_argument('message')

    def handle(self, *args, **kwargs):
        filename = kwargs['filename']
        message = kwargs['message']

        file = open(filename)

        @fdb.transactional
        def change_create(tr, message):
            changeid = vnstore.change_create(tr)
            vnstore.change_message(tr, changeid, message)
            change = ChangeRequest(changeid=changeid, message=message)
            change.save()
            return changeid

        changeid = change_create(db, message)

        @fdb.transactional
        def save(tr, changeid, line):
            # TODO: need more validation
            line = line.strip()
            if not line:
                return
            triple = json.loads(line)

            if (not isinstance(triple, list)) and len(triple) != 3:
                raise Exception('Wrong format')

            uid, key, value = triple

            uid = uid.strip()
            if not uid:
                raise Exception('uid is required')

            try:
                uid = UUID(hex=uid)
            except ValueError as exc:
                raise Exception('not a uuid: {}'.format(uid))

            key = key.strip().lower()
            if not key:
                raise Exception('wrong key: {}'.format(key))

            if not value:
                raise Exception('empty value')

            if isinstance(value, str):
                try:
                    value = UUID(hex=value)
                except ValueError:
                    if value.lower() == 'false':
                        value = False
                    elif value.lower() == 'true':
                        value = True

            # value is something interesting
            assert isinstance(value, (UUID, int, bool, str))

            vnstore.change_continue(tr, changeid)

            vnstore.add(tr, uid, key, value)

        for line in file:
            save(db, changeid, line)

        @fdb.transactional
        def apply(tr, change, changeid):
            # apply change to vnstore
            vnstore.change_apply(tr, changeid)
            # mark the change as applied
            change.status = ChangeRequest.STATUS_APPLIED
            change.save()
            # apply changes to snapshot
            changes = vnstore._tuples.FROM(
                tr,
                var('uid'), var('key'), var('value'), var('alive'), changeid
            )
            for change in changes:
                if change['alive']:
                    op = nstore.add
                else:
                    op = nstore.delete
                op(tr, change['uid'], change['key'], change['value'])

        change = ChangeRequest.objects.get(changeid=changeid)
        apply(db, change, changeid)

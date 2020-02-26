import json
from uuid import UUID

import rdflib
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
        parser.add_argument('format')
        parser.add_argument('filename')
        parser.add_argument('message')

    def handle(self, *args, **kwargs):
        format = kwargs['format']
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
        def save(tr, changeid, uid, key, value):
            vnstore.change_continue(tr, changeid)
            vnstore.add(tr, uid, key, value)

        for index, line in enumerate(file):
            if index % 100_000 == 0:
                print(index)

            g = rdflib.Graph()
            g.parse(data=line, format=format)
            uid, key, value = next(iter(g))
            save(db, changeid, uid, key, value)

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

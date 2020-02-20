from uuid import UUID
from uuid import uuid4

from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotFound
from django.template.defaulttags import register

import fdb

import vnstore
import nstore
from .models import ChangeRequest
from .models import Comment


fdb.api_version(620)
db = fdb.open()


ITEMS = ['uid', 'key', 'value', 'license']

var = nstore.var
# nstore contain the latest version snapshot
nstore = nstore.open(['copernic', 'nstore'], ITEMS)
# vnstore contains the versioned ITEMS
vnstore = vnstore.open(['copernic', 'vnstore'], ITEMS)


@register.filter
def getattr(dictionary, key):
    return dictionary.get(key)

def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def make_query(params):
    # make query for the win ;-)
    variables = set()
    patterns = []
    for index in range(5):
        index = str(index)
        pattern = []
        for name in ['uid', 'key', 'value', 'license']:
            key = name + index
            try:
                value = params[key]
            except KeyError:
                # skip that pattern row
                break
            else:
                value = value.strip()
                if value.endswith('?'):
                    # it is a variable
                    variables.add(value)
                    pattern.append(var(value))
                    continue

                if not value:
                    # skip that pattern row
                    break

                # Try to guess the Python object
                try:
                    value = UUID(hex=value)
                except ValueError:
                    try:
                        value = int(value)
                    except ValueError:
                        if value.lower() == 'false':
                            value = False
                        elif value.lower() == 'true':
                            value = True
                        else:
                            # just a string
                            value = value
                pattern.append(value)
        else:
            patterns.append(pattern)

    return variables, patterns


def take(iterator, count):
    for _ in range(count):
        out = next(iterator)
        yield out


def drop(iterator, count):
    for _ in range(count):
        next(iterator)
    yield from iterator


def query(request):
    if request.GET:
        variables, patterns = make_query(request.GET)

        if not patterns:
            msg = 'There is no complete pattern...'
            return HttpResponseBadRequest(msg)

        if all(isinstance(x, var) for x in patterns[0]):
            msg = 'The first pattern must not be only made of variables!'
            return HttpResponseBadRequest(msg)

        def do(tr, patterns):
            out = nstore.FROM(tr, *patterns[0])
            # see nstore.select
            for pattern in patterns[1:]:
                where = nstore.where(tr, *pattern)
                out = where(out)
            out = list(take(out, 100))
            return out

        bindings = do(db, patterns)

        variables = sorted(variables)
    else:
        variables = []
        bindings = []

    context = dict(
        variables=variables,
        bindings=bindings,
        patterns=request.GET,
    )
    return render(request, 'query.html', context)


def uid(request, uid):
    try:
        uid = UUID(uid)
    except ValueError:
        return HttpResponseNotFound()

    @fdb.transactional
    def get(tr, uid):
        out = nstore.FROM(tr, uid, var('key'), var('value'), var('license'))
        out = list(out)
        return out

    tuples = get(db, uid)

    return render(request, 'uid.html', dict(uid=uid, tuples=tuples))

def changes(request):
    changes = ChangeRequest.objects.all().order_by('-created_at')
    return render(request, 'changes.html', dict(changes=changes))


def change_new(request):

    @fdb.transactional
    def change_create(tr):
        changeid = vnstore.change_create(tr)
        change = ChangeRequest(changeid=changeid)
        change.save()
        return changeid

    changeid = change_create(db)

    return redirect('/change/{}/'.format(changeid.hex.upper()))


def change(request, changeid):
    changeid = UUID(changeid)
    change = get_object_or_404(ChangeRequest, changeid=changeid)
    comments = change.comment_set.all().order_by('created_at')

    # fetch changes
    def fetch(tr, changeid):
        # TODO: move the vnstore
        out = vnstore._tuples.FROM(
            tr,
            var('uid'), var('key'), var('value'), var('license'), var('alive'), changeid
        )
        out = list(out)
        return out

    changes = fetch(db, changeid)
    context = dict(
        change=change,
        comments=comments,
        changes=changes,
        superuser=request.user.is_superuser,
    )
    return render(request, 'change.html', context)


def comment_add(request, changeid):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    changeid = UUID(hex=changeid)
    change = ChangeRequest.objects.get(changeid=changeid)
    body = request.POST['body']
    comment = Comment(body=body, change_request=change)
    comment.save()
    return redirect('/change/{}/'.format(changeid.hex.upper()))


def change_add(request, changeid):
    changeid = UUID(hex=changeid)
    change = get_object_or_404(ChangeRequest, changeid=changeid)

    # TODO: better validation
    if request.method == 'POST':
        # get or create unique identifier
        uid = request.POST.get('uid', '')
        uid = uid.strip()
        if uid:
            try:
                uid = UUID(hex=uid)
            except ValueError as exc:
                return HttpResponseBadRequest()
        else:
            uid = uuid4()
        # get keys TODO: validate kebab-case with a regex
        key = request.POST['key']
        key = key.strip()
        if not key:
            return HttpResponseBadRequest()
        # get value, try to detect the type
        value = request.POST['value']
        value = value.strip()
        if not value:
            return HttpResponseBadRequest()
        try:
            value = UUID(hex=value)
        except ValueError:
            try:
                value = int(value)
            except ValueError:
                if value.lower() == 'false':
                    value = False
                elif value.lower() == 'true':
                    value = True
        # value is something interesting
        assert isinstance(value, (UUID, int, bool, str))
        # get the license
        license = request.POST['license']
        license = license.strip()
        if not license:
            return HTTP-HttpResponseBadRequest()

        @fdb.transactional
        def add(tr, uid, key, value, license):
            vnstore.change_continue(tr, change.changeid)
            vnstore.add(tr, uid, key, value, license)

        add(db, uid, key, value, license)

        return redirect('/change/{}'.format(changeid))
    else:
        return render(request, 'change_add.html', dict(changeid=changeid))


def change_delete(request, changeid):
    changeid = UUID(hex=changeid)
    change = get_object_or_404(ChangeRequest, changeid=changeid)

    # TODO: better validation
    if request.method == 'POST':
        # get or create unique identifier
        uid = request.POST.get('uid', '')
        uid = uid.strip()
        if uid:
            try:
                uid = UUID(hex=uid)
            except ValueError as exc:
                return HttpResponseBadRequest()
        else:
            uid = uuid4()
        # get keys TODO: validate kebab-case with a regex
        key = request.POST['key']
        key = key.strip()
        if not key:
            return HttpResponseBadRequest()
        key = key.lower()

        # get value, try to detect the type
        value = request.POST['value']
        value = value.strip()
        if not value:
            return HttpResponseBadRequest()
        try:
            value = UUID(hex=value)
        except ValueError:
            try:
                value = int(value)
            except ValueError:
                if value.lower() == 'false':
                    value = False
                elif value.lower() == 'true':
                    value = True
        # value is something interesting
        assert isinstance(value, (UUID, int, bool, str))

        # get the license
        license = request.POST['license']
        license = license.strip()
        if not license:
            return HttpResponseBadRequest()
        license = license.upper()

        @fdb.transactional
        def delete(tr, uid, key, value, license):
            vnstore.change_continue(tr, change.changeid)
            vnstore.delete(tr, uid, key, value, license)

        delete(db, uid, key, value, license)

        return redirect('/change/{}'.format(changeid))
    else:
        return render(request, 'change_delete.html', dict(changeid=changeid))


def change_import(request, changeid):
    pass


def change_apply(request, changeid):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    if not request.user.is_superuser:
        return HttpResponseForbidden('Only superuser can apply changes!')

    changeid = UUID(hex=changeid)
    change = get_object_or_404(ChangeRequest, changeid=changeid)

    if change.status == ChangeRequest.STATUS_APPLIED:
        return HttpResponseBadRequest('Change already applied!')

    def apply(tr, change, changeid):
        # apply change to vnstore
        vnstore.change_apply(tr, changeid)
        # mark the change as applied
        change.status = ChangeRequest.STATUS_APPLIED
        change.save()
        # apply changes to snapshot
        changes = vnstore._tuples.FROM(
            tr,
            var('uid'), var('key'), var('value'), var('license'), var('alive'), changeid
        )
        for change in changes:
            if change['alive']:
                op = nstore.add
            else:
                op = nstore.delete
            op(tr, change['uid'], change['key'], change['value'], change['license'])


    apply(db, change, changeid)

    return redirect('/change/{}'.format(changeid))

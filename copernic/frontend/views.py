from uuid import UUID

from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponseBadRequest

import fdb

import vnstore
import nstore
from .models import ChangeRequest
from .models import Comment


fdb.api_version(620)
db = fdb.open()


ITEMS = ['uid', 'key', 'value', 'license']

# nstore contain the latest version snapshot
nstore = nstore.open(['copernic', 'nstore'], ITEMS)
# vnstore contains the versioned ITEMS
vnstore = vnstore.open(['copernic', 'vnstore'], ITEMS)


def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

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
    changeid = UUID(hex=changeid)
    change = ChangeRequest.objects.get(changeid=changeid)
    comments = change.comment_set.all().order_by('created_at')
    return render(request, 'change.html', dict(change=change, comments=comments))

def comment_add(request, changeid):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    changeid = UUID(hex=changeid)
    change = ChangeRequest.objects.get(changeid=changeid)
    body = request.POST['body']
    comment = Comment(body=body, change_request=change)
    comment.save()
    return redirect('/change/{}/'.format(changeid.hex.upper()))

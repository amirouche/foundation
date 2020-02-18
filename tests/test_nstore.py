import logging
import os
import uuid
from shutil import rmtree
from uuid import uuid4

import daiquiri
import pytest
import fdb
from fdb.tuple import pack
from fdb.tuple import unpack

from copernic import nstore


daiquiri.setup(logging.DEBUG, outputs=("stderr",))

fdb.api_version(620)


def open():
    db = fdb.open()

    # XXX: clear database
    db.clear_range(b"", b"\xff")

    return db


triplestore = nstore.open(['copernic', 'test'], ('uid', 'key', 'value'))


def test_nop():
    db = open()
    assert db


def test_simple_single_item_db_subject_lookup():
    db = open()

    expected = uuid4()
    triplestore.add(db, expected, "title", "hyper.dev")
    query = triplestore.FROM(db, nstore.var("subject"), "title", "hyper.dev")
    out = list(query)
    out = out[0]["subject"]
    assert out == expected


def test_ask_delete_and_ask():
    db = open()
    expected = uuid4()
    triplestore.add(db, expected, "title", "hyper.dev")
    assert triplestore.ask(db, expected, "title", "hyper.dev")
    triplestore.delete(db, expected, "title", "hyper.dev")
    assert not triplestore.ask(db, expected, "title", "hyper.dev")


def test_simple_multiple_items_db_subject_lookup():
    db = open()
    expected = uuid4()
    triplestore.add(db, expected, "title", "hyper.dev")
    triplestore.add(db, uuid4(), "title", "vstinner.readthedocs.io")
    triplestore.add(db, uuid4(), "title", "julien.danjou.info")
    query = triplestore.FROM(db, nstore.var("subject"), "title", "hyper.dev")
    out = list(query)
    out = out[0]["subject"]
    assert out == expected


def test_complex():
    db = open()
    hyperdev = uuid4()
    triplestore.add(db, hyperdev, "title", "hyper.dev")
    triplestore.add(db, hyperdev, "keyword", "scheme")
    triplestore.add(db, hyperdev, "keyword", "python")
    triplestore.add(db, hyperdev, "keyword", "hacker")

    vstinner = uuid4()
    triplestore.add(db, vstinner, "title", "vstinner.readthedocs.io")
    triplestore.add(db, vstinner, "keyword", "python")
    triplestore.add(db, vstinner, "keyword", "hacker")

    julien = uuid4()
    triplestore.add(db, julien, "title", "julien.danjou.info")
    triplestore.add(db, julien, "keyword", "python")
    triplestore.add(db, julien, "keyword", "hacker")

    out = nstore.select(
        triplestore.FROM(db, nstore.var("identifier"), "keyword", "scheme"),
        triplestore.where(db, nstore.var("identifier"), "title", nstore.var("blog")),
    )
    out = [x["blog"] for x in out]
    assert out == ["hyper.dev"]


def test_seed_subject_variable():
    db = open()
    hyperdev = uuid4()
    triplestore.add(db, hyperdev, "title", "hyper.dev")
    triplestore.add(db, hyperdev, "keyword", "scheme")
    triplestore.add(db, hyperdev, "keyword", "python")
    triplestore.add(db, hyperdev, "keyword", "hacker")

    vstinner = uuid4()
    triplestore.add(db, vstinner, "title", "vstinner.readthedocs.io")
    triplestore.add(db, vstinner, "keyword", "python")
    triplestore.add(db, vstinner, "keyword", "hacker")

    julien = uuid4()
    triplestore.add(db, julien, "title", "julien.danjou.info")
    triplestore.add(db, julien, "keyword", "python")
    triplestore.add(db, julien, "keyword", "hacker")

    out = nstore.select(
        triplestore.FROM(db, nstore.var("uid"), "title", "vstinner.readthedocs.io"),
    )
    out = [x["uid"] for x in out]
    assert out == [vstinner]


def test_seed_subject_lookup():
    db = open()
    hyperdev = uuid4()
    triplestore.add(db, hyperdev, "title", "hyper.dev")
    triplestore.add(db, hyperdev, "keyword", "scheme")
    triplestore.add(db, hyperdev, "keyword", "python")
    triplestore.add(db, hyperdev, "keyword", "hacker")

    vstinner = uuid4()
    triplestore.add(db, vstinner, "title", "vstinner.readthedocs.io")
    triplestore.add(db, vstinner, "keyword", "python")
    triplestore.add(db, vstinner, "keyword", "hacker")

    julien = uuid4()
    triplestore.add(db, julien, "title", "julien.danjou.info")
    triplestore.add(db, julien, "keyword", "python")
    triplestore.add(db, julien, "keyword", "hacker")

    query = triplestore.FROM(db, vstinner, nstore.var("key"), nstore.var("value"))
    out = [dict(x) for x in query]

    expected = [
        {"key": "keyword", "value": "hacker"},
        {"key": "keyword", "value": "python"},
        {"key": "title", "value": "vstinner.readthedocs.io"},
    ]

    assert out == expected


def test_seed_object_variable():
    db = open()
    hyperdev = uuid4()
    triplestore.add(db, hyperdev, "title", "hyper.dev")
    triplestore.add(db, hyperdev, "keyword", "scheme")
    triplestore.add(db, hyperdev, "keyword", "python")
    triplestore.add(db, hyperdev, "keyword", "hacker")

    vstinner = uuid4()
    triplestore.add(db, vstinner, "title", "vstinner.readthedocs.io")
    triplestore.add(db, vstinner, "keyword", "python")
    triplestore.add(db, vstinner, "keyword", "hacker")

    julien = uuid4()
    triplestore.add(db, julien, "title", "julien.danjou.info")
    triplestore.add(db, julien, "keyword", "python")
    triplestore.add(db, julien, "keyword", "hacker")

    query = triplestore.FROM(db, hyperdev, 'title', nstore.var("value"))
    out = [dict(x) for x in query][0]['value']

    assert out == 'hyper.dev'


def test_subject_variable():
    db = open()

    # prepare
    hyperdev = uuid4()
    triplestore.add(db, hyperdev, "title", "hyper.dev")
    triplestore.add(db, hyperdev, "keyword", "fantastic")
    triplestore.add(db, hyperdev, "keyword", "python")
    triplestore.add(db, hyperdev, "keyword", "scheme")
    triplestore.add(db, hyperdev, "keyword", "hacker")

    post1 = uuid4()
    triplestore.add(db, post1, "blog", hyperdev)
    triplestore.add(db, post1, "title", "hoply is awesome")

    post2 = uuid4()
    triplestore.add(db, post2, "blog", hyperdev)
    triplestore.add(db, post2, "title", "hoply triple store")

    # exec, fetch all blog title from hyper.dev
    out = nstore.select(
        triplestore.FROM(db, nstore.var("blog"), "title", "hyper.dev"),
        triplestore.where(db, nstore.var("post"), "blog", nstore.var("blog")),
        triplestore.where(db, nstore.var("post"), "title", nstore.var("title")),
    )
    out = sorted([x["title"] for x in out])
    assert out == ["hoply is awesome", "hoply triple store"]

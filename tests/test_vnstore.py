import logging

import daiquiri
import pytest
import fdb

from copernic import vnstore


daiquiri.setup(logging.DEBUG, outputs=("stderr",))

fdb.api_version(620)


def open():
    db = fdb.open()

    # XXX: clear database
    db.clear_range(b"", b"\xff")

    return db


v3store = vnstore.open(['copernic', 'test'], ('uid', 'key', 'value'))


def test_nop():
    db = open()
    assert db


def test_ask_empty_branch():
    db = open()

    @fdb.transactional
    def ask(tr):
        return v3store.ask(tr, 'hello', 'world', 'again')

    assert not ask(db)


def test_add_and_ask():
    db = open()

    branch = None

    @fdb.transactional
    def ask(tr):
        return v3store.ask(tr, 'hello', 'world', 'again')

    assert not ask(db)

    @fdb.transactional
    def add(tr):
        change = v3store.change_create(tr)
        out = v3store.add(tr, 'hello', 'world', 'again')
        assert out
        v3store.change_apply(tr, change)

    add(db)

    @fdb.transactional
    def try_again(tr):
        v3store.change_create(tr)
        out = v3store.add(tr, 'hello', 'world', 'again')
        assert not out

    try_again(db)

    assert ask(db)


def test_parallel_history():
    db = open()

    @fdb.transactional
    def create_some_change(tr, something):
        change = v3store.change_create(tr)
        assert v3store.add(tr, 'hello', 'world', something)
        # XXX: do not apply the change

    for i in range(3):
        create_some_change(db, i)

    for i in range(3):
        create_some_change(db, i)

    @fdb.transactional
    def ask(tr, something):
        return v3store.ask(tr, 'hello', 'world', something)

    for i in range(3):
        assert not ask(db, i)

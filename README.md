# [foundation](https://github.com/amirouche/foundation)

**alpha**

![data](https://github.com/amirouche/foundation/raw/main/data.jpg)

## Abstract

foundation is a programming system (mostly) implemented with seeds, by seeds.

It is supported by a data store that keeps track of everything that
can be understood. It is possible to time travel at any point in
History, and through any story. Meanwhile it is still efficient to
query
and modify the present.  

The data, and its history is stored in Foundation.

foundation demonstrate that versioned knowledge allow to implement workflows
that ease cooperation.

## De suite

Follow the hip cli hop dance:

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./manage.sh migrate
./manage.sh createsuperuser
./manage.sh runserver
```

## Foundation

Versioning in production systems is a trick everybody knows about
whether it is through backup, doublpe, and triple backups, logging
systems, bank and ad-hoc audit trail, in other words tracebility wins
(wait for the debbuger (read how to debug programs by Dybvig!)!).

It allows to inspect, debug and in worst cases rollback to previous
states. There is no need to explain the great importance of history in
software enginerring as tools like fossil have shaped the
anthroposcene.

Having the power of History kicks the beats of manyfolds.

Like, it allows to implement a mechanic similar to  pull
requests and change requests in many products.  That very
mechanic is explicit about actual people, in particular, 
when we reply, and cheers a change made by another.

*versioned structured knowledge* make the implementation of such
mechanics more systematic and less error prone as the implementation
can be shared across various tools and communities.

foundation takes the path of versioning data (or things, or ghosts,
(or people)) and apply the change-request mechanic to collaborate
around our making.

**foundation aims to make practical cooperation around the creation,
publication, storage, re-use and sustainability of knowledge that is
bigger than any known human memory.**

**Tech**: Foundation is stored in
[FoundationDB](https://www.foundationdb.org/) to deliver, with opt-in,
a pragmatic versatile ACID-compliant versioned triple store, where
people can cooperate around the making of knowledge.

--

a Foundation engineer. 

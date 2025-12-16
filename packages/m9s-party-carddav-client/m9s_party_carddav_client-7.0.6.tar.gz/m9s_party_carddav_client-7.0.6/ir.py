# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from collections import defaultdict

from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction


class Cron(metaclass=PoolMeta):
    __name__ = 'ir.cron'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.method.selection.extend([
                ('res.user|update_all_vcards',
                    "Update all VCards on the DAV backend"),
                ])


class Note(metaclass=PoolMeta):
    __name__ = 'ir.note'

    @classmethod
    def create(cls, vlist):
        notes = super().create(vlist)
        parties = list([
            x.resource for x in notes
            if str(x.resource).startswith('party.party,')])
        cls.update_vcards(parties)
        return notes

    @classmethod
    def write(cls, *args):
        actions = iter(args)
        parties = []
        for notes, values in zip(actions, actions):
            parties.extend([
                x.resource for x in notes
                if str(x.resource).startswith('party.party,')])
        super().write(*args)
        cls.update_vcards(parties)

    @classmethod
    def delete(cls, notes):
        parties = list([
            x.resource for x in notes
            if str(x.resource).startswith('party.party,')])
        cls.update_vcards(parties)
        super().delete(notes)

    @classmethod
    def update_vcards(cls, parties):
        pool = Pool()
        Party = pool.get('party.party')

        if parties:
            to_update = defaultdict(dict)
            for party in parties:
                if party.carddav_collection and party.export_notes:
                    to_update[party.id] = {
                        'old_collection': party.carddav_collection.id,
                        'new_collection': party.carddav_collection.id,
                        }
            with Transaction().set_context(dav_to_update=to_update):
                Party.__queue__.update_vcards(to_update)

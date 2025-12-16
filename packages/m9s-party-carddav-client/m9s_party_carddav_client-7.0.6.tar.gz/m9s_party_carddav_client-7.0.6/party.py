# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import logging

from collections import defaultdict

from trytond.model import Index, ModelSQL, Unique, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction

logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)


class Party(metaclass=PoolMeta):
    __name__ = 'party.party'

    carddav_collection = fields.Function(
        fields.Many2One('webdav.carddav_collection',
            'CardDAV Addressbook',
            domain=[
                ('user', '=', Eval('context_user', -1)),
            ],
            help='Select the DAV addressbook used for this party.\n'
            'Leave empty to not upload this contact.'
            ),
        'get_carddav_collection', setter='set_carddav_collection',
        searcher='search_carddav_collection')

    @staticmethod
    def default_carddav_collection():
        pool = Pool()
        User = pool.get('res.user')
        user = User(Transaction().user)
        if user.default_carddav_collection:
            return user.default_carddav_collection.id

    def get_carddav_collection(self, name):
        pool = Pool()
        CardDAVCollectionRel = pool.get('party.carddav_collection_rel')

        rel = CardDAVCollectionRel.search([
                ('user', '=', Transaction().user),
                ('party', '=', self.id),
                ], limit=1)
        if rel:
            return rel[0].carddav_collection.id

    @classmethod
    def set_carddav_collection(cls, parties, name, value):
        pool = Pool()
        CardDAVCollectionRel = pool.get('party.carddav_collection_rel')

        user = Transaction().user
        for party in parties:
            existing = CardDAVCollectionRel.search([
                ('party', '=', party.id),
                ('user', '=', user),
            ], limit=1)

            if value:
                if existing:
                    existing[0].carddav_collection = value
                    existing[0].save()
                else:
                    CardDAVCollectionRel.create([{
                        'party': party.id,
                        'user': user,
                        'carddav_collection': value,
                    }])
            else:
                if existing:
                    CardDAVCollectionRel.delete(existing)

    @classmethod
    def search_carddav_collection(cls, name, clause):
        pool = Pool()
        CardDAVCollectionRel = pool.get('party.carddav_collection_rel')

        rels = CardDAVCollectionRel.search([
            ('user', '=', Transaction().user),
            ('carddav_collection',) + tuple(clause[1:])
        ])
        return [('id', 'in', [r.carddav_collection.id for r in rels])]

    @fields.depends('carddav_collection')
    def on_change_carddav_collection(self):
        pool = Pool()
        User = pool.get('res.user')

        user = User(Transaction().user)
        if self.carddav_collection:
            # TODO: put it on the queue
            try:
                user.ensure_dav_collection(self.carddav_collection)
            except:
                pass

    @classmethod
    def create(cls, vlist):
        vlist = super().create(vlist)
        to_update = defaultdict(dict)
        for values in vlist:
            if values.carddav_collection:
                to_update[values.id] = {
                    'old_collection': None,
                    'new_collection': values.carddav_collection.id,
                    }
        # Put to_update also in the context to make it accessible for workers
        with Transaction().set_context(dav_to_update=to_update):
            cls.__queue__.update_vcards(to_update)
        return vlist

    @classmethod
    def write(cls, *args):
        actions = iter(args)
        to_update = defaultdict(dict)
        for party, values in zip(actions, actions):
            old_collection = (party[0].carddav_collection.id
                if party[0].carddav_collection else None)
            new_collection = (values['carddav_collection'] if
                values.get('carddav_collection') else old_collection)
            to_update[party[0].id] = {
                    'old_collection': old_collection,
                    'new_collection': new_collection,
                    }
            # Delete vcards of deactivated parties
            if 'active' in values and values['active'] is False:
                old_url = (
                    f'{party[0].carddav_collection.url}/{party[0].uuid}.vcf')
                to_update[party[0].id].update({
                        'old_url': old_url,
                        'new_collection': None,
                        })
        super().write(*args)
        # Put to_update also in the context to make it accessible for workers
        with Transaction().set_context(dav_to_update=to_update):
            cls.__queue__.update_vcards(to_update)

    @classmethod
    def delete(cls, parties):
        pool = Pool()
        Company = pool.get('company.company')

        to_update = defaultdict(dict)
        for party in parties:
            if party.carddav_collection:
                to_update[party.id] = {
                    'old_collection': party.carddav_collection.id,
                    'new_collection': None,
                    'old_url': (
                        f'{party.carddav_collection.url}/{party.uuid}.vcf'),
                    }
        # Put to_update also in the context to make it accessible for workers
        # Note: dirty hack
        # Since this doesn't work on the queue, because the queue cannot
        # instanciate any more the deleted records, we use the party of the
        # company to run the code. This works, because we are sure that we are
        # only running the delete_vcard code without touching the party and the
        # correct data are pulled from the context.
        company = Company(Transaction().context.get('company'))
        party = company.party
        with Transaction().set_context(dav_to_update=to_update):
            cls.__queue__.update_vcards([party])
        super().delete(parties)

    @classmethod
    def update_vcards(cls, to_update):
        '''
        DAV wrapper for vCard (preferably executed on the queue)

        Args:
            to_update: Dict with key party.id and value Dict
                    with keys:
                    old_collection
                    new_collection
                    old_url (only used for DELETE because party is no more
                    available at execution time)

                    Pulls this dict also with precedence from the
                    context key dav_to_update to be functional on the queue.
        '''
        pool = Pool()
        CardDAVCollection = pool.get('webdav.carddav_collection')

        context = Transaction().context
        to_update = context.get('dav_to_update') or to_update
        for record in to_update:
            party = cls(record)
            old_collection = to_update[record]['old_collection']
            new_collection = to_update[record]['new_collection']
            (old_coll := (CardDAVCollection(old_collection)
                if old_collection else None))
            (new_coll := (CardDAVCollection(new_collection)
                if new_collection else None))
            # no collection assigned, skip
            if (old_collection is None
                    and new_collection is None):
                continue
            # same collection, just update
            elif old_collection == new_collection:
                party.upload_vcard()
            # collection was unassigned, delete
            elif (old_collection is not None
                    and new_collection is None):
                party.delete_vcard(
                    to_update[record].get('old_url') or old_coll.url)
            # collection was changed, move
            # (is automatically uploaded before move)
            elif (old_collection is not None
                    and new_collection is not None):
                party.move_vcard(old_coll.url, new_coll.url)
            # anything else, update
            else:
                party.upload_vcard()

    def upload_vcard(self):
        '''
        Upload a vCard (.vcf) to the given addressbook
        '''
        pool = Pool()
        User = pool.get('res.user')

        user = User(Transaction().user)
        card_url = (f'{user.base_url}/addressbooks/users/'
            f'{user.webdav_username}/{self.carddav_collection.url}/'
            f'{self.uuid}.vcf')

        headers = {
            "Content-Type": "text/vcard; charset=utf-8",
        }
        data = self.vcard
        request = user.dav_request(
            card_url, 'PUT', headers=headers, data=data, expected=(201, 204))

        # Debug logging
        if request['status_code'] in (201, 204):
            logger.debug(f"vCard {self.uuid} uploaded to {card_url}")
            return card_url
        logger.debug(f"Failed to upload vCard: {request['status_code']}"
            f"{request['text']} {card_url}")

    def move_vcard(self, old_url, new_url):
        """
        Move a vCard from old URL to new URL
        """
        pool = Pool()
        User = pool.get('res.user')

        user = User(Transaction().user)
        card_url = f'{user.base_url}/addressbooks/users/{user.webdav_username}'
        old_card_url = f'{card_url}/{old_url}/{self.uuid}.vcf'
        new_card_url = f'{card_url}/{new_url}/{self.uuid}.vcf'
        request = user.dav_move(old_card_url, new_card_url)

        # Debug logging
        if request['status_code'] in (201, 204):
            logger.debug(f"vCard {self.uuid} moved from {old_card_url} to "
                f"{new_card_url}")
            return True
        elif request['status_code'] == 404:
            logger.debug(f"vCard {self.uuid} not found.")
            logger.debug(f"Error: {request['text']}")
            return self.upload_vcard()
        logger.debug(f"Failed to move vCard: "
            f"{request['status_code']} {request['text']}")

    def delete_vcard(self, url):
        """
        Delete a vCard by UID
        """
        pool = Pool()
        User = pool.get('res.user')

        user = User(Transaction().user)
        context = Transaction().context
        to_update = context.get('dav_to_update')
        if to_update:
            key = next(iter(to_update))
            vcf_url = to_update[key]['old_url']
        else:
            vcf_url = f'{url}/{self.uuid}.vcf'

        card_url = (f'{user.base_url}/addressbooks/users/'
            f'{user.webdav_username}/{vcf_url}')
        request = user.dav_request(
            card_url, 'DELETE', expected=(200, 204))

        # Debug logging
        if request['status_code'] in (200, 204):
            logger.debug(f"vCard {vcf_url} deleted.")
            return True
        elif request['status_code'] == 404:
            logger.debug(f"vCard {vcf_url} not found.")
            return False
        logger.debug(f"Failed to delete vCard: "
            f"{request['status_code']} {request.text}")


class PartyCardDAVCollection(ModelSQL):
    "CardDAV Collection per Party and User"
    __name__ = "party.carddav_collection_rel"
    party = fields.Many2One('party.party', 'Party', required=True,
        ondelete='CASCADE')
    user = fields.Many2One('res.user', 'User', required=True,
        ondelete='CASCADE')
    carddav_collection = fields.Many2One('webdav.carddav_collection',
        'CardDAV Addressbook', required=True)

    @classmethod
    def __setup__(cls):
        super().__setup__()
        t = cls.__table__()
        cls._sql_constraints.extend([
                ('party_user_unique', Unique(t, t.party, t.user),
                    'party_carddav_client.msg_party_user_unique'),
                ])
        cls._sql_indexes.update({
            Index(t, (t.party, Index.Equality())),
            Index(t, (t.user, Index.Equality())),
        })

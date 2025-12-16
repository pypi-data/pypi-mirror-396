# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from collections import defaultdict
from xml.etree import ElementTree as ET

from trytond.config import config
from trytond.model import ModelView, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.tools import grouped_slice
from trytond.transaction import Transaction

_batch_size = config.getint('vcard', 'batch_size', default=300)


class User(metaclass=PoolMeta):
    __name__ = "res.user"
    default_carddav_collection = fields.Many2One('webdav.carddav_collection',
        'Default Addressbook',
        domain=[('user', '=', Eval('id'))],
        help='Select the addressbook used for new parties.',
        )

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._buttons.update({
            'update_all_vcards': {},
            'update_vcard_categories': {},
            })

    @classmethod
    @ModelView.button
    def update_all_vcards(cls, records):
        cls.update_carddav_collection(records)
        cls.update_vcards(records)

    @classmethod
    def update_vcards(cls, records):
        pool = Pool()
        Party = pool.get('party.party')

        all_parties = Party.search([])
        for record in records:
            for parties in grouped_slice(all_parties, _batch_size):
                to_update = defaultdict(dict)
                for party in parties:
                    if party.carddav_collection:
                        to_update[party.id] = {
                            'old_collection': party.carddav_collection.id,
                            'new_collection': party.carddav_collection.id,
                        }
                        if not party.active:
                            old_url = (
                                f'{party.carddav_collection.url}/'
                                f'{party.uuid}.vcf')
                            to_update[party[0].id].update({
                                    'old_url': old_url,
                                    'new_collection': None,
                                    })
                with Transaction().set_context(dav_to_update=to_update):
                    Party.__queue__.update_vcards(to_update)

    @classmethod
    @ModelView.button
    def update_vcard_categories(cls, records):
        cls.update_carddav_collection(records)
        cls.update_vcard_category(records)

    @classmethod
    def update_vcard_category(cls, records):
        '''
        Update VCard categories of the current user by using REPORT instead
        of downloading all vcards.
        '''
        pool = Pool()
        VCardCategory = pool.get('webdav.vcard_category')

        categories = set()

        report_body = """<?xml version="1.0" encoding="utf-8" ?>
        <card:addressbook-query xmlns:d="DAV:" xmlns:card="urn:ietf:params:xml:ns:carddav">
          <d:prop>
            <card:address-data>
              <card:prop name="CATEGORIES"/>
            </card:address-data>
          </d:prop>
        </card:addressbook-query>
        """
        for record in records:
            for collection in record.carddav_collections:
                dav_url = (f'{record.base_url}/addressbooks/users/'
                    f'{record.webdav_username}/{collection.url}/')
                request = record.dav_request(
                    dav_url, 'REPORT', depth=1, xml=report_body)

                tree = ET.fromstring(request['text'])
                ns = cls.namespace_map
                for response in tree.findall(".//card:address-data", ns):
                    data = response.text
                    if not data:
                        continue
                    # Parse CATEGORIES lines manually to avoid
                    # full vobject parsing
                    for line in data.splitlines():
                        if line.startswith("CATEGORIES:"):
                            cats = line[len("CATEGORIES:"):].strip().split(",")
                            categories.update(
                                c.strip() for c in cats if c.strip())

            existent_categories = VCardCategory.search([
                        ('user', '=', record.id),
                        ])
            existent_names = [e.name for e in existent_categories]
            new_categories = []
            for category in categories:
                if category not in existent_names:
                    new_category = VCardCategory()
                    new_category.name = category
                    new_category.user = record.id
                    new_categories.append(new_category)
            if new_categories:
                VCardCategory.save(new_categories)

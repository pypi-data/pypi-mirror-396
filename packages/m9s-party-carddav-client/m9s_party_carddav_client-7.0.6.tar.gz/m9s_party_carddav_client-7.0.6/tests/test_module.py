# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.tests.test_tryton import ModuleTestCase


class PartyCarddavClientTestCase(ModuleTestCase):
    "Test Party Carddav Client module"
    module = 'party_carddav_client'


del ModuleTestCase

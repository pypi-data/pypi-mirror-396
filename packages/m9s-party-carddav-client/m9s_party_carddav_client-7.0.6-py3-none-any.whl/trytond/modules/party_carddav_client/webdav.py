# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.model import Index, ModelSQL, ModelView, Unique, fields
from trytond.pyson import Eval


class CardDAVCollection(ModelSQL, ModelView):
    "CardDAV Collection (Addressbook)"
    __name__ = "webdav.carddav_collection"
    user = fields.Many2One('res.user', 'User', required=True,
        ondelete='RESTRICT', readonly=True)
    name = fields.Char("Name", required=True)
    url = fields.Char('URL', required=True,
        states={
            'readonly': Eval('id', 0) > 0
            })
    description = fields.Char("Description")
    ctag = fields.Char('CTag', readonly=True)

    @classmethod
    def __setup__(cls):
        super().__setup__()
        t = cls.__table__()
        cls._sql_constraints.extend([
                ('user_url_uniq', Unique(t, t.user, t.url),
                    'dav_client.msg_url_unique_per_user'),
                ])
        cls._sql_indexes.update({
            Index(t, (t.url, Index.Equality())),
            Index(t, (t.ctag, Index.Equality())),
        })


class CalDAVCollection(ModelSQL, ModelView):
    "CalDAV Collection (Calendar)"
    __name__ = "webdav.caldav_collection"
    user = fields.Many2One('res.user', 'User', required=True,
        ondelete='RESTRICT', readonly=True)
    name = fields.Char("Name", required=True)
    url = fields.Char('URL', required=True,
        states={
            'readonly': Eval('id', 0) > 0
            })
    description = fields.Char("Description")
    ctag = fields.Char('CTag', readonly=True)

    @classmethod
    def __setup__(cls):
        super().__setup__()
        t = cls.__table__()
        cls._sql_constraints.extend([
                ('user_url_uniq', Unique(t, t.user, t.url),
                    'dav_client.msg_url_unique_per_user'),
                ])
        cls._sql_indexes.update({
            Index(t, (t.url, Index.Equality())),
            Index(t, (t.ctag, Index.Equality())),
        })

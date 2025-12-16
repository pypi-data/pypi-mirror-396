"""Generic string substitution

>>> portal = layer['portal']
>>> sandbox = portal._getOb('sandbox')
>>> sandbox.setEffectiveDate('2021/10/10')
>>> sandbox.setSubject((u'air', u'pollution'))

"""

from AccessControl import Unauthorized
from Acquisition import aq_base
from DateTime import DateTime
from plone.stringinterp.adapters import BaseSubstitution
from Products.CMFCore.interfaces import IContentish
from Products.CMFPlone.i18nl10n import ulocalized_time
from Products.CMFPlone.utils import safe_unicode
from zope.component import adapter

from eea.stringinterp import EEAMessageFactory as _

_marker = "_bad_"


@adapter(IContentish)
class GenericContextAttributeSubstitution(BaseSubstitution):
    """Generic string substitution adapter to dynamically get
    attributes from context

    >>> from plone.stringinterp.interfaces import IStringSubstitution
    >>> substitute = IStringSubstitution(sandbox)
    >>> substitute
    <eea.stringinterp.adapters.GenericContextAttributeSubstitution...>

    """

    category = _("All Content")
    description = _("Generic context attribute, e.g.: ${my_custom_field}")

    def __call__(self, key=None):
        """Safe get attribute from context

        >>> substitute('title')
        'Sandbox'

        >>> substitute('Title')
        'Sandbox'

        >>> substitute('acl_users')
        '${acl_users}'

        >>> substitute('password')
        '${password}'

        >>> substitute('effective')
        'Oct 10, 2021 12:00 AM'

        >>> substitute('Subject')
        'air, pollution'

        """
        try:
            return safe_unicode(self.safe_call(key=key))
        except Unauthorized:
            return _("Unauthorized")

    def formatDate(self, adate):
        """Format date"""
        try:
            return safe_unicode(
                ulocalized_time(adate, long_format=True, context=self.context)
            )
        except ValueError:
            return "???"

    def safe_call(self, key):
        """Safe call"""
        res = getattr(aq_base(self.context), key, _marker)
        if callable(res):
            res = res()

        if not res:
            return ""

        if res is _marker:
            return "${%s}" % (key)

        if isinstance(res, (tuple, list, set)):
            return ", ".join(res)

        if isinstance(res, DateTime):
            return self.formatDate(res)

        return res

==========================
eea.stringinterp
==========================
.. image:: https://ci.eionet.europa.eu/buildStatus/icon?job=eea/eea.stringinterp/develop
  :target: https://ci.eionet.europa.eu/job/eea/job/eea.stringinterp/job/develop/display/redirect
  :alt: Develop
.. image:: https://ci.eionet.europa.eu/buildStatus/icon?job=eea/eea.stringinterp/master
  :target: https://ci.eionet.europa.eu/job/eea/job/eea.stringinterp/job/master/display/redirect
  :alt: Master

Extends `plone.stringinterp <https://github.com/plone/plone.stringinterp>`_ functionallity with a 
generic fallback string substitution adapter that lookup **context** properties if no explicit named
**IStringSubstitution** is defined.

.. contents::

Main features
=============

1. **Generic string substitution** adapter to easily grab custom properties from context

Install
=======

* Add eea.stringinterp to your eggs section in your buildout and
  re-run buildout::

    [buildout]
    eggs +=
      eea.stringinterp

* You can download a sample buildout from:

  - https://github.com/eea/eea.stringinterp/tree/master/buildouts/plone4
  - https://github.com/eea/eea.stringinterp/tree/master/buildouts/plone5

* Or via docker::

    $ docker run --rm -p 8080:8080 -e ADDONS="eea.stringinterp" plone

* Install *eea.stringinterp* within Site Setup > Add-ons


Usage
=====

* Via **Site Setup > Dexterity Content Types > Page > Fields Tab** add new Field, `e.g.: custom_field`
* Via **Site Setup > Content Rules** add a rule to send email on Workflow change
* Within **Message** add some `Custom: ${custom_field}`
* Add new **Page** and fill the **custom_field**
* Publish your **Page**
* Check your email

Code usage
==========

    >>> from plone.stringinterp.interfaces import IStringSubstitution
    >>> substitute = IStringSubstitution(sandbox)
    >>> substitute
    <eea.stringinterp.adapters.GenericContextAttributeSubstitution object at...>

    >>> substitute('title')
    'Sandbox'

    >>> substitute('effective')
    'Oct 10, 2021 12:00 AM'

    >>> substitute('Subject')
    'air, pollution'


Buildout installation
=====================

- `Plone 4+ <https://github.com/eea/eea.stringinterp/tree/master/buildouts/plone4>`_
- `Plone 5+ <https://github.com/eea/eea.stringinterp/tree/master/buildouts/plone5>`_


Source code
===========

- `Plone 4+ on github <https://github.com/eea/eea.stringinterp>`_
- `Plone 5+ on github <https://github.com/eea/eea.stringinterp>`_


Eggs repository
===============

- https://pypi.python.org/pypi/eea.stringinterp
- http://eggrepo.eea.europa.eu/simple


Plone versions
==============
It has been developed and tested for Plone 4 and 5. See buildouts section above.


How to contribute
=================
See the `contribution guidelines (CONTRIBUTING.md) <https://github.com/eea/eea.stringinterp/blob/master/CONTRIBUTING.md>`_.

Copyright and license
=====================

eea.stringinterp (the Original Code) is free software; you can
redistribute it and/or modify it under the terms of the
GNU General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc., 59
Temple Place, Suite 330, Boston, MA 02111-1307 USA.

The Initial Owner of the Original Code is European Environment Agency (EEA).
Portions created by Eau de Web are Copyright (C) 2009 by
European Environment Agency. All Rights Reserved.


Funding
=======

EEA_ - European Environment Agency (EU)

.. _EEA: https://www.eea.europa.eu/
.. _`EEA Web Systems Training`: http://www.youtube.com/user/eeacms/videos?view=1

# -*- coding: UTF-8 -*-
# Copyright 2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import dd, rt, _


class DeedTypes(dd.ChoiceList):
    pass


add = DeedTypes.add_item
add("10", _("Sale"), 'sale')
add("20", _("Rent"), 'rent')


class PropertyConditions(dd.ChoiceList):
    pass


add = PropertyConditions.add_item
add("10", _("New building"))
add("20", _("Ready to move in"))
add("30", _("Needs renovation"))
add("40", _("Project"))


class AvailabilityTexts(dd.ChoiceList):
    pass


add = AvailabilityTexts.add_item
add("10", _("Available as of"))
add("20", _("Immediately"))
add("30", _("After signing the deed"))
add("40", _("To be defined"))
add("50", _("Depending on the tenant"))

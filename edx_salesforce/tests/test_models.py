"""
Unit tests for edx_salesforce models.
"""

from __future__ import absolute_import, unicode_literals

from ddt import ddt, data, unpack
from django.test import TestCase

from edx_salesforce.models import (Account, Campaign, CampaignMember, Contact, DiscountCode, Lead, Opportunity,
                                   OpportunityContactRole, OpportunityLineItem, Pricebook2, PricebookEntry, Product2)

ACCOUNT = Account(name='foo')
CAMPAIGN = Campaign(name='foo')
LEAD = Lead(username='foo')
CAMPAIGN_MEMBER = CampaignMember(campaign=CAMPAIGN, lead=LEAD)
CONTACT = Contact(name='foo')
DISCOUNT_CODE = DiscountCode(name='foo')
OPPORTUNITY = Opportunity(name='foo')
OPPORTUNITY_CONTACT_ROLE = OpportunityContactRole(opportunity=OPPORTUNITY, contact=CONTACT)
PRICEBOOK = Pricebook2(name='foo')
PRODUCT = Product2(name='foo')
PRICEBOOK_ENTRY = PricebookEntry(pricebook2=PRICEBOOK, product2=PRODUCT)
OPPORTUNITY_LINE_ITEM = OpportunityLineItem(opportunity=OPPORTUNITY, pricebook_entry=PRICEBOOK_ENTRY)


@ddt
class TestUnicode(TestCase):
    """
    Test utilities module.
    """

    @data(
        (ACCOUNT, ACCOUNT.name),
        (CAMPAIGN, CAMPAIGN.name),
        (LEAD, LEAD.username),
        (CAMPAIGN_MEMBER, '{}:{}'.format(CAMPAIGN.name, LEAD.username)),
        (CONTACT, CONTACT.name),
        (DISCOUNT_CODE, DISCOUNT_CODE.name),
        (OPPORTUNITY, OPPORTUNITY.name),
        (OPPORTUNITY_CONTACT_ROLE, '{}:{}'.format(OPPORTUNITY.name, CONTACT.name)),
        (PRICEBOOK, PRICEBOOK.name),
        (PRODUCT, PRODUCT.name),
        (PRICEBOOK_ENTRY, '{}:{}'.format(PRICEBOOK.name, PRODUCT.name)),
        (OPPORTUNITY_LINE_ITEM, '{}:{}'.format(OPPORTUNITY.name, PRICEBOOK_ENTRY))
    )
    @unpack
    def test_unicode(self, model, expected):
        self.assertEqual(unicode(model), expected)

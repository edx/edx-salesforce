# pylint: disable=unused-argument
"""
Unit tests for sync_salesforce management command.
"""

from __future__ import absolute_import, unicode_literals

import decimal

import pytz
from mock import Mock, patch, PropertyMock

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from edx_salesforce.choices import COUNTRIES_BY_CODE, EDUCATION_BY_CODE
from edx_salesforce.management.commands.sync_salesforce import Command as SyncSalesforceCommand
from edx_salesforce.models import (Campaign, Contact, DiscountCode, Lead, Opportunity, Pricebook2, PricebookEntry,
                                   Product2)
from edx_salesforce.tests.edx_sample_data import USER_DATA
from edx_salesforce.utils import parse_user_full_name


class TestSyncSalesForce(TestCase):
    """
    Test sync_salesforce management command.
    """

    def setUp(self):
        super(TestSyncSalesForce, self).setUp()

        self.orgs = ['testX']
        self.site_domain = 'test_server.fake_domain'
        self.user_data = USER_DATA[0]

    def _get_user_data(self):
        """
        Returns user data dictionary.
        """
        first_name, last_name = parse_user_full_name(self.user_data['full_name'])
        return {
            'first_name': first_name,
            'last_name': last_name,
            'email': self.user_data['email'],
            'country': COUNTRIES_BY_CODE.get((self.user_data['country'] or '').upper()),
            'year_of_birth': str(self.user_data['year_of_birth']),
            'language': settings.LANGUAGES_BY_CODE.get(self.user_data['language']),
            'level_of_education': EDUCATION_BY_CODE.get((self.user_data['level_of_education'] or '').lower()),
            'interest': self.user_data['goals'],
            'gender': (self.user_data['gender'] or '').upper(),
            'registration_date': pytz.utc.localize(self.user_data['registration_date'].replace(microsecond=0))
        }

    def _get_lead_object(self, is_converted=False):
        """
        Returns Lead object.

        """
        lead_data = {
            'username': self.user_data['username'],
            'is_converted': is_converted,
            'converted_contact': Contact(**self._get_user_data()),
            'pi_utm_campaign': self.user_data['tracking']['utm_campaign'],
            'pi_utm_content': self.user_data['tracking']['utm_content'],
            'pi_utm_medium': self.user_data['tracking']['utm_medium'],
            'pi_utm_source': self.user_data['tracking']['utm_source'],
            'pi_utm_term': self.user_data['tracking']['utm_term']
        }
        lead_data.update(self._get_user_data())
        return Lead(**lead_data)

    @patch.object(PricebookEntry, 'save')
    @patch.object(Contact, 'save')
    @patch.object(Lead, 'save')
    @patch('edx_salesforce.models.OpportunityLineItem.objects.create')
    @patch('edx_salesforce.management.commands.sync_salesforce.convert_lead')
    @patch('edx_salesforce.models.PricebookEntry.objects.get')
    @patch('edx_salesforce.models.OpportunityContactRole.objects.create')
    @patch('edx_salesforce.models.Product2.objects.get_or_create')
    @patch('edx_salesforce.models.DiscountCode.objects.get_or_create')
    @patch('edx_salesforce.models.Opportunity.objects.get_or_create')
    @patch('edx_salesforce.models.Lead.objects.get')
    @patch('edx_salesforce.models.Pricebook2.objects.get')
    @patch('edx_salesforce.management.commands.sync_salesforce.fetch_user_data')
    def test_command_with_not_converted_lead(self, mock_user_fetch_data, mock_pricebook_get, mock_lead_get,
                                             mock_opp_get_or_create, mock_dc_get_or_create,
                                             mock_product2_get_or_create, mock_opp_contact_role_create,
                                             mock_price_book_entry_get, mock_convert_lead,
                                             mock_opp_line_item_create, mock_lead_save, mock_contact_save,
                                             mock_price_book_save):
        """
        Test management command when lead is not converted contact.
        """
        course = self.user_data['courses'][0]
        opportunity = Opportunity(
            name=course['course_id'],
            amount=course['unit_price'] * course['quantity'],
            close_date=course['purchase_date'],
            stage_name='Paid',
        )
        product = Product2(name=course['course_id'])
        price_book = Pricebook2(is_standard=True)

        mock_user_fetch_data.return_value = [self.user_data]
        mock_pricebook_get.return_value = price_book
        mock_lead_get.return_value = self._get_lead_object(is_converted=False)
        mock_opp_get_or_create.return_value = opportunity, True
        mock_dc_get_or_create.return_value = DiscountCode(name=course['coupon_codes'][0]), True
        mock_product2_get_or_create.return_value = product, True
        mock_price_book_entry_get.return_value = PricebookEntry(
            pricebook2=price_book,
            product2=product,
            is_active=True,
            unit_price=decimal.Decimal('1.2')
        )

        call_command(
            'sync_salesforce',
            '--site-domain', self.site_domain,
            '--orgs', self.orgs
        )

        mock_lead_get.assert_called_with(username=self.user_data['username'])
        mock_pricebook_get.assert_called_with(is_standard=True)
        mock_opp_get_or_create.assert_called_with(
            account=None,
            name=course['course_id'],
            amount=course['unit_price'] * course['quantity'],
            close_date=course['purchase_date'],
            paid_date=course['purchase_date'],
            stage_name='Paid'
        )
        mock_price_book_entry_get.assert_called_with(
            pricebook2=price_book,
            product2=product,
            is_active=True
        )
        mock_product2_get_or_create.assert_called_with(name=course['course_id'])
        mock_dc_get_or_create.assert_called_with(name=course['coupon_codes'][0])

        self.assertFalse(mock_lead_save.called)
        self.assertTrue(mock_convert_lead.called)
        self.assertTrue(mock_contact_save.called)
        self.assertTrue(mock_opp_contact_role_create.called)
        self.assertTrue(mock_price_book_save.called)
        self.assertTrue(mock_opp_line_item_create.called)

    @patch.object(PricebookEntry, 'save')
    @patch.object(Contact, 'save')
    @patch.object(Lead, 'save')
    @patch('edx_salesforce.models.OpportunityLineItem.objects.create')
    @patch('edx_salesforce.management.commands.sync_salesforce.convert_lead')
    @patch('edx_salesforce.models.PricebookEntry.objects.create')
    @patch('edx_salesforce.models.PricebookEntry.objects.get', side_effect=PricebookEntry.DoesNotExist)
    @patch('edx_salesforce.models.OpportunityContactRole.objects.create')
    @patch('edx_salesforce.models.Product2.objects.get_or_create')
    @patch('edx_salesforce.models.DiscountCode.objects.get_or_create')
    @patch('edx_salesforce.models.Opportunity.objects.get_or_create')
    @patch('edx_salesforce.models.Lead.objects.get')
    @patch('edx_salesforce.models.Pricebook2.objects.get')
    @patch('edx_salesforce.management.commands.sync_salesforce.fetch_user_data')
    def test_command_with_converted_lead(self, mock_user_fetch_data, mock_pricebook_get, mock_lead_get,
                                         mock_opp_get_or_create, mock_dc_get_or_create,
                                         mock_product2_get_or_create, mock_opp_contact_role_create,
                                         mock_price_book_entry_get, mock_price_book_entry_create,
                                         mock_convert_lead, mock_opp_line_item_create, mock_lead_save,
                                         mock_contact_save, mock_price_book_save):
        """
        Test management command when lead is converted contact.
        """
        course = self.user_data['courses'][0]
        opportunity = Opportunity(
            name=course['course_id'],
            amount=course['unit_price'] * course['quantity'],
            close_date=course['purchase_date'],
            stage_name='Paid',
        )
        product = Product2(name=course['course_id'])
        price_book = Pricebook2(is_standard=True)

        mock_user_fetch_data.return_value = [self.user_data]
        mock_pricebook_get.return_value = price_book
        mock_lead_get.return_value = self._get_lead_object(is_converted=True)
        mock_opp_get_or_create.return_value = opportunity, True
        mock_dc_get_or_create.return_value = DiscountCode(name=course['coupon_codes'][0]), True
        mock_product2_get_or_create.return_value = product, True

        call_command(
            'sync_salesforce',
            '--site-domain', self.site_domain,
            '--orgs', self.orgs
        )

        mock_lead_get.assert_called_with(username=self.user_data['username'])
        mock_pricebook_get.assert_called_with(is_standard=True)
        self.assertTrue(mock_price_book_entry_create.called)
        self.assertFalse(mock_contact_save.called)

    @patch('edx_salesforce.models.CampaignMember.objects.create')
    @patch('edx_salesforce.models.Campaign.objects.get_or_create')
    @patch.object(Lead, 'save')
    @patch('edx_salesforce.models.Lead.objects.get', side_effect=Lead.DoesNotExist)
    @patch('edx_salesforce.models.Pricebook2.objects.get')
    @patch('edx_salesforce.management.commands.sync_salesforce.fetch_user_data')
    def test_command_with_no_lead(self, mock_user_fetch_data, mock_pricebook_get, mock_lead_get, mock_lead_save,
                                  mock_campaign_get_or_create, mock_campaign_member_create):
        """
        Test management command when lead does not exist for given user data.
        """
        utm_campaign = self.user_data['tracking']['utm_campaign']
        mock_pricebook_get.return_value = Pricebook2(is_standard=True)
        user_data_without_courses = dict(self.user_data)
        user_data_without_courses['courses'] = {}
        mock_user_fetch_data.return_value = [user_data_without_courses]
        mock_campaign_get_or_create.return_value = Campaign(name=utm_campaign), True

        call_command(
            'sync_salesforce',
            '--site-domain', self.site_domain,
            '--orgs', self.orgs
        )

        mock_campaign_get_or_create.assert_called_with(name=utm_campaign)
        mock_pricebook_get.assert_called_with(is_standard=True)
        self.assertTrue(mock_campaign_member_create.called)
        self.assertTrue(mock_lead_save.called)

    @patch('edx_salesforce.models.CampaignMember.objects.create')
    @patch('edx_salesforce.models.Campaign.objects.get_or_create')
    @patch.object(Lead, 'save')
    @patch('edx_salesforce.models.Lead.objects.get', side_effect=Lead.DoesNotExist)
    @patch('edx_salesforce.models.Pricebook2.objects.get')
    @patch('edx_salesforce.management.commands.sync_salesforce.fetch_user_data')
    def test_command_with_no_lead_and_empty_campaign(self, mock_user_fetch_data, mock_pricebook_get, mock_lead_get,
                                                     mock_lead_save, mock_campaign_get_or_create,
                                                     mock_campaign_member_create):
        """
        Test management command when lead does not exist for given user data and utm_campaign is empty.
        """
        utm_campaign = self.user_data['tracking']['utm_campaign']
        mock_pricebook_get.return_value = Pricebook2(is_standard=True)
        user_data_without_courses = dict(self.user_data)
        user_data_without_courses['courses'] = {}
        user_data_without_courses['tracking']['utm_campaign'] = None
        mock_user_fetch_data.return_value = [user_data_without_courses]
        mock_campaign_get_or_create.return_value = Campaign(name=utm_campaign), True

        call_command(
            'sync_salesforce',
            '--site-domain', self.site_domain,
            '--orgs', self.orgs
        )

        mock_pricebook_get.assert_called_with(is_standard=True)
        self.assertTrue(mock_lead_save.called)

    @patch.object(PricebookEntry, 'save')
    @patch.object(Contact, 'save')
    @patch.object(Lead, 'save')
    @patch('edx_salesforce.models.OpportunityLineItem.objects.create')
    @patch('edx_salesforce.models.OpportunityContactRole.objects.create')
    @patch('edx_salesforce.models.PricebookEntry.objects.get')
    @patch('edx_salesforce.models.Product2.objects.get_or_create')
    @patch('edx_salesforce.models.Opportunity.objects.get_or_create')
    @patch('edx_salesforce.management.commands.sync_salesforce.convert_lead')
    @patch('edx_salesforce.models.Lead.objects.get')
    @patch('edx_salesforce.models.Pricebook2.objects.get')
    @patch('edx_salesforce.management.commands.sync_salesforce.fetch_user_data')
    def test_command_without_coupon_codes(self, mock_user_fetch_data, mock_pricebook_get,
                                          mock_lead_get, mock_convert_lead,
                                          mock_opp_get_or_create, mock_product2_get_or_create,
                                          mock_price_book_entry_get, mock_opp_contact_role_create,
                                          mock_opp_line_item_create, mock_lead_save, mock_contact_save,
                                          mock_price_book_save):
        """
        Test management command when coupon codes are empty.
        """
        course = self.user_data['courses'][0]
        opportunity = Opportunity(
            name=course['course_id'],
            amount=course['unit_price'] * course['quantity'],
            close_date=course['purchase_date'],
            stage_name='Paid',
        )
        product = Product2(name=course['course_id'])
        price_book = Pricebook2(is_standard=True)

        mock_pricebook_get.return_value = price_book
        mock_lead_get.return_value = self._get_lead_object(is_converted=False)
        user_data_without_discount_code = dict(self.user_data)
        user_data_without_discount_code['courses'][0]['coupon_codes'] = None
        mock_user_fetch_data.return_value = [user_data_without_discount_code]
        mock_opp_get_or_create.return_value = opportunity, True
        mock_product2_get_or_create.return_value = product, True
        mock_price_book_entry_get.return_value = PricebookEntry(
            pricebook2=price_book,
            product2=product,
            is_active=True,
            unit_price=decimal.Decimal('10.2')
        )

        call_command(
            'sync_salesforce',
            '--site-domain', self.site_domain,
            '--orgs', self.orgs
        )

        mock_product2_get_or_create.assert_called_with(name=course['course_id'])
        mock_pricebook_get.assert_called_with(is_standard=True)
        self.assertTrue(mock_opp_contact_role_create.called)
        self.assertTrue(mock_opp_line_item_create.called)
        self.assertTrue(mock_contact_save.called)
        self.assertFalse(mock_lead_save.called)

    @patch.object(Contact, 'save')
    @patch.object(Lead, 'save')
    @patch('edx_salesforce.models.Opportunity.objects.get_or_create')
    @patch('edx_salesforce.management.commands.sync_salesforce.convert_lead')
    @patch('edx_salesforce.models.Lead.objects.get')
    @patch('edx_salesforce.models.Pricebook2.objects.get')
    @patch('edx_salesforce.management.commands.sync_salesforce.fetch_user_data')
    def test_command_with_opportunity(self, mock_user_fetch_data, mock_pricebook_get,
                                      mock_lead_get, mock_convert_lead,
                                      mock_opp_get_or_create, mock_lead_save,
                                      mock_contact_save):
        """
        Test management command with a lead which is in "In Sync" status.
        """
        course = self.user_data['courses'][0]
        opportunity = Opportunity(
            name=course['course_id'],
            amount=course['unit_price'] * course['quantity'],
            close_date=course['purchase_date'],
            stage_name='Paid',
        )
        mock_pricebook_get.return_value = Pricebook2(is_standard=True)
        mock_lead_get.return_value = self._get_lead_object(is_converted=False)
        mock_user_fetch_data.return_value = [self.user_data]
        mock_opp_get_or_create.return_value = opportunity, False

        call_command(
            'sync_salesforce',
            '--site-domain', self.site_domain,
            '--orgs', self.orgs
        )

        mock_pricebook_get.assert_called_with(is_standard=True)
        self.assertTrue(mock_contact_save.called)
        self.assertFalse(mock_lead_save.called)

    @patch('edx_salesforce.models.Pricebook2.objects.get')
    @patch('edx_salesforce.management.commands.sync_salesforce.fetch_user_data')
    def test_command_with_no_user_data(self, mock_user_fetch_data, mock_pricebook_get):
        """
        Test management command with empty user data.
        """

        mock_user_fetch_data.return_value = []
        call_command(
            'sync_salesforce',
            '--site-domain', self.site_domain,
            '--orgs', self.orgs
        )

    @patch.object(Lead, 'save')
    @patch('edx_salesforce.models.Lead.objects.get')
    @patch('edx_salesforce.models.Pricebook2.objects.get')
    @patch('edx_salesforce.management.commands.sync_salesforce.fetch_user_data')
    def test_command_with_in_sync_lead(self, mock_user_fetch_data, mock_pricebook_get,
                                       mock_lead_get, mock_lead_save):
        """
        Test management command with invalid user data.
        """
        mock_pricebook_get.return_value = Pricebook2(is_standard=True)
        user_data_without_courses = dict(self.user_data)
        mock_lead_get.return_value = self._get_lead_object(is_converted=False)
        user_data_without_courses['courses'] = {}
        mock_user_fetch_data.return_value = [user_data_without_courses]

        call_command(
            'sync_salesforce',
            '--site-domain', self.site_domain,
            '--orgs', self.orgs
        )

        mock_pricebook_get.assert_called_with(is_standard=True)
        self.assertFalse(mock_lead_save.called)

    @patch.object(Lead, 'save')
    @patch('edx_salesforce.models.Campaign.objects.get_or_create')
    @patch('edx_salesforce.models.CampaignMember.objects.create')
    @patch('edx_salesforce.models.Lead.objects.get', side_effect=Lead.DoesNotExist)
    @patch('edx_salesforce.models.Pricebook2.objects.get')
    @patch('edx_salesforce.management.commands.sync_salesforce.fetch_user_data')
    def test_command_with_invalid_data(self, mock_user_fetch_data, mock_pricebook_get,
                                       mock_lead_get, mock_lead_save, mock_campaign_get_or_create,
                                       mock_campaign_member_create):
        """
        Test management command with invalid user data.
        """
        user_data_without_courses = dict(self.user_data)
        user_data_without_courses.pop('courses')

        mock_pricebook_get.return_value = Pricebook2(is_standard=True)
        mock_user_fetch_data.return_value = [user_data_without_courses]
        mock_lead_get.return_value = self._get_lead_object()
        mock_campaign_get_or_create.return_value = Campaign(name='fake-campaign-utm'), True

        call_command(
            'sync_salesforce',
            '--site-domain', self.site_domain,
            '--orgs', self.orgs
        )

        call_command(
            'sync_salesforce',
            '--site-domain', self.site_domain,
            '--orgs', self.orgs
        )

    @patch('edx_salesforce.models.Pricebook2.objects.get')
    @patch('edx_salesforce.models.Campaign.objects.get_or_create')
    def test_get_or_create_cached(self, mock_campaign_get_or_create, mock_pricebook_get):
        """
        Test calls to _get_or_create are appropriately cached.
        """
        mock_campaign_get_or_create.return_value = Campaign(name='foo'), True
        command = SyncSalesforceCommand()

        command._get_or_create('Campaign', name='foo')  # pylint: disable=protected-access
        mock_campaign_get_or_create.assert_called()
        mock_campaign_get_or_create.reset_mock()

        command._get_or_create('Campaign', name='foo')  # pylint: disable=protected-access
        mock_campaign_get_or_create.assert_not_called()
        mock_campaign_get_or_create.reset_mock()

        command._get_or_create('Campaign', name='bar')  # pylint: disable=protected-access
        mock_campaign_get_or_create.assert_called()

    @patch.object(Contact, 'save')
    @patch('edx_salesforce.models.Lead.objects.get')
    @patch('edx_salesforce.models.Pricebook2.objects.get')
    @patch('edx_salesforce.management.commands.sync_salesforce.fetch_user_data')
    def test_command_with_manually_deleted_converted_contact(self, mock_user_fetch_data, mock_pricebook_get,
                                                             mock_lead_get, mock_contact_save):
        """
        Test management command when converted Contact object was manually deleted in Salesforce.
        """
        mock_user_fetch_data.return_value = [self.user_data]
        lead = Mock(is_converted=True)
        type(lead).converted_contact = PropertyMock(side_effect=Contact.DoesNotExist)
        mock_lead_get.return_value = lead

        call_command(
            'sync_salesforce',
            '--site-domain', self.site_domain,
            '--orgs', self.orgs
        )

        self.assertFalse(mock_contact_save.called)

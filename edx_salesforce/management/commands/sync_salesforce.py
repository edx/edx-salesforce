"""Django command for synchronizing EdX user account data with Salesforce."""

from __future__ import absolute_import, unicode_literals

import traceback
from collections import OrderedDict, defaultdict
from itertools import izip

import pytz
from salesforce.utils import convert_lead

from django.conf import settings
from django.core.management.base import BaseCommand

from edx_salesforce.choices import COUNTRIES_BY_CODE, EDUCATION_BY_CODE
from edx_salesforce.edx_data import fetch_user_data
from edx_salesforce.models import (Campaign, CampaignMember, Contact, DiscountCode, Lead, Opportunity,
                                   OpportunityContactRole, OpportunityLineItem, Pricebook2, PricebookEntry, Product2)
from edx_salesforce.utils import parse_user_full_name


STATUS_IN_SYNC = 'In Sync'
STATUS_SYNCHRONIZED = 'SYNCHRONIZED'
STATUS_FAILED = 'FAILED'


class Command(BaseCommand):
    """
    This command synchronizes Open EdX user account and associated course purchase data with Salesforce
    for the given site and organizations. The organizations provided are used to find ecommerce orders
    made by users who may not have created their user accounts on the given site.

    This command uses django-salesforce to interact with the Salesforce API, thus the Salesforce API
    credentials used to syncrhonize are configured in the Django database settings of this project.

    Salesforce Lead objects are created for each user account. Leads are converted to Contact objects
    if a course purchase is associated with the user account. Opportunity objects are created for each
    course purchase.
    """
    help = 'Synchronize the user account data for the given site/organization with a Salesforce account'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        self.pricebook = Pricebook2.objects.get(is_standard=True)
        self.cache = defaultdict(dict)

    def add_arguments(self, parser):
        parser.add_argument(
            '-s',
            '--site-domain',
            dest='site_domain',
            required=True,
            help='Domain of site for which user account data should be collected'
        )
        parser.add_argument(
            '-o',
            '--orgs',
            nargs='+',
            dest='orgs',
            required=True,
            help=(
                'Organizations for which user account data should be collected for '
                'course purchases associated with those organizations'
            )
        )

    def handle(self, *args, **options):
        site_domain = options['site_domain']
        orgs = options['orgs']

        users = fetch_user_data(site_domain, orgs)

        if not users:
            self.stdout.write(
                'No user accounts found for site {site} and orgs {orgs}...'.format(
                    site=site_domain,
                    orgs=','.join(orgs),
                )
            )
            return

        status_count = self._sync_user_data(users, site_domain, orgs)

        # Output sync status summary
        for status, count in status_count.items():
            self.stdout.write('{count} {status}'.format(count=count, status=status))

    def _sync_user_data(self, users, site_domain, orgs):
        """
        Synchronizes the provided user data with the configured Salesforce account.
        Returns a dictionary containing the count of how many user synchronizations
        produced each sync status (for logging purposes).
        """
        total_users = len(users)
        pluralize_total_users = '' if total_users == 1 else 's'
        org_count = len(orgs)
        pluralize_orgs = '' if org_count == 1 else 's'

        self.stdout.write(
            'Synchronizing {total_users} user account{pluralize_total_users} '
            'for site {site} and org{pluralize_orgs} {orgs}...'.format(
                total_users=total_users,
                pluralize_total_users=pluralize_total_users,
                site=site_domain,
                pluralize_orgs=pluralize_orgs,
                orgs=','.join(orgs),
            )
        )

        status_count = OrderedDict()
        status_count[STATUS_FAILED] = 0
        status_count[STATUS_IN_SYNC] = 0
        status_count[STATUS_SYNCHRONIZED] = 0

        for user in users:
            try:
                salesforce_updated = False
                status = STATUS_IN_SYNC
                username = user['username']

                # Create a new Lead if it doesn't exist, otherwise
                # make sure the user account data is in sync with
                # the Lead or converted Contact object.
                try:
                    lead = Lead.objects.get(username=username)
                    if lead.is_converted:
                        contact = None
                        try:
                            contact = lead.converted_contact
                        except Contact.DoesNotExist:
                            # Converted contact must have been manually deleted in Salesforce
                            pass

                        if contact:
                            salesforce_updated = self._update_lead_or_contact(lead.converted_contact, user)
                        else:
                            self.stdout.write(
                                '{user}: Converted Contact object manually deleted in Salesforce. '
                                'This user will no longer be synchronized.'.format(
                                    user=username
                                )
                            )
                            continue
                    else:
                        salesforce_updated = self._update_lead_or_contact(lead, user)
                except Lead.DoesNotExist:
                    lead = self._create_lead(user)
                    salesforce_updated = True

                # Synchronize course purchase data with Salesforce Opportunity objects
                courses = user['courses']
                if courses:
                    if not lead.is_converted:
                        # Convert the Lead to a Contact
                        lead = self._convert_lead(lead)
                        salesforce_updated = True

                    for course in courses:
                        salesforce_updated = self._sync_opportunity(lead, course) or salesforce_updated

                # Update sync status/count for summary output
                if salesforce_updated:
                    status_count[STATUS_SYNCHRONIZED] += 1
                    status = STATUS_SYNCHRONIZED
                else:
                    status_count[STATUS_IN_SYNC] += 1
            except Exception:  # pylint: disable=broad-except
                # Output stacktrace and update sync status/count for summary output
                traceback.print_exc(file=self.stdout)
                status_count[STATUS_FAILED] += 1
                status = STATUS_FAILED

            # Output the sync status of this user
            self.stdout.write(
                '{user}: {status}'.format(
                    user=username,
                    status=status
                )
            )

        self.stdout.write(
            'Finished processing {total_users} user{pluralize_total_users} '
            'for site {site} and org{pluralize_orgs} {orgs}.'.format(
                total_users=total_users,
                pluralize_total_users=pluralize_total_users,
                site=site_domain,
                orgs=','.join(orgs),
                pluralize_orgs=pluralize_orgs,
            )
        )

        return status_count

    def _convert_lead(self, lead):
        """
        Converts Lead to Contact and Account objects in Salesforce. Salesforce does not
        automatically populate custom fields on the Contact object with data from the
        Lead object, so we must do that here.
        """
        _ = convert_lead(lead, doNotCreateOpportunity=True)
        lead = Lead.objects.get(username=lead.username)

        contact = lead.converted_contact
        contact.language = lead.language
        contact.country = lead.country
        contact.year_of_birth = lead.year_of_birth
        contact.pi_utm_campaign = lead.pi_utm_campaign
        contact.pi_utm_content = lead.pi_utm_content
        contact.pi_utm_medium = lead.pi_utm_medium
        contact.pi_utm_source = lead.pi_utm_source
        contact.pi_utm_term = lead.pi_utm_term
        contact.save()

        return lead

    def _create_lead(self, user):
        """
        Creates a new Lead object in Salesforce. If UTM parameters are available for
        the user account, creates a Campaign object in Salesforce if one does not
        already exist and associates it with the Lead object.
        """
        username = user['username']
        lead = Lead(username=username, company=username)
        self._update_lead_or_contact(lead, user)

        tracking_data = user['tracking']
        utm_campaign = tracking_data.get('utm_campaign')
        if utm_campaign:
            campaign, _ = self._get_or_create(Campaign.__name__, name=utm_campaign)
            CampaignMember.objects.create(campaign=campaign, lead=lead)

            lead.campaign = campaign
            lead.pi_utm_campaign = utm_campaign
            lead.pi_utm_content = tracking_data.get('utm_content')
            lead.pi_utm_medium = tracking_data.get('utm_medium')
            lead.pi_utm_source = tracking_data.get('utm_source')
            lead.pi_utm_term = tracking_data.get('utm_term')
            lead.save()

        # Set this value here instead of making a GET request
        # to pull the newly created Lead.
        lead.is_converted = False

        return lead

    def _get_or_create(self, model_name, **kwargs):
        """
        Wrapper for Salesforce model manager get_or_create which caches
        the Salesforce objects in a local cache stored in an instance
        variable on the command class.
        """
        cache_key = '|'.join([str(value) for _, value in kwargs.items()])
        created = False
        obj = self.cache[model_name].get(cache_key)
        if not obj:
            obj, created = globals()[model_name].objects.get_or_create(**kwargs)
            self.cache[model_name][cache_key] = obj

        return obj, created

    def _get_or_create_pricebook_entry(self, pricebook, product, unit_price):
        """
        Gets or creates a PricebookEntry model using the given Pricebook and Product
        models with the given unit price.
        """
        created = False
        try:
            pricebook_entry = PricebookEntry.objects.get(
                pricebook2=pricebook,
                product2=product,
                is_active=True,
            )

            # Sometimes the price of a course will get changed by
            # the course team resulting in course purchase data
            # associated with the same course with different prices.
            # This will set the unit price on the PricebookEntry to
            # the maximum price found for the Product.
            if pricebook_entry.unit_price < unit_price:
                pricebook_entry.unit_price = unit_price
                pricebook_entry.save()
        except PricebookEntry.DoesNotExist:
            pricebook_entry = PricebookEntry.objects.create(
                pricebook2=pricebook,
                product2=product,
                is_active=True,
                unit_price=unit_price
            )
            created = True

        return pricebook_entry, created

    def _sync_opportunity(self, lead, course_purchase_data):
        """
        Creates or updates an Opportunity object in Salesforce for the course purchase
        associated with the given Lead.

        Arguments:
            lead (Lead): The lead associated with the course purchase.
            course_purchase_data (dict): Dictionary containing the course purchase details.

        Returns:
            boolean, True if an Opportunity object was created in Salesforce, otherwise False.
        """
        course_id = course_purchase_data['course_id']
        quantity = course_purchase_data['quantity']
        unit_price = course_purchase_data['unit_price']
        total_price = unit_price * quantity
        paid_date = course_purchase_data['purchase_date']
        opportunity, created = Opportunity.objects.get_or_create(
            account=lead.converted_account,
            name=course_id,
            amount=total_price,
            close_date=paid_date,
            paid_date=paid_date,
            stage_name='Paid',
        )
        if created:
            quantity = course_purchase_data['quantity']
            list_price = course_purchase_data['list_price']
            unit_price = course_purchase_data['unit_price']
            coupon_codes = course_purchase_data['coupon_codes']
            discount_code = None
            if coupon_codes:
                discount_code, _ = DiscountCode.objects.get_or_create(name=coupon_codes[0])

            product, _ = self._get_or_create(Product2.__name__, name=course_id)
            pricebook_entry, _ = self._get_or_create_pricebook_entry(self.pricebook, product, list_price)

            OpportunityContactRole.objects.create(
                opportunity=opportunity,
                contact=lead.converted_contact,
                role='Participant',
                is_primary=True
            )

            OpportunityLineItem.objects.create(
                opportunity=opportunity,
                pricebook_entry=pricebook_entry,
                quantity=quantity,
                list_price=list_price,
                total_price=total_price,
                discount_code=discount_code,
            )

        return created

    def _update_field(self, model, field, value):
        """
        Updates the model field if it has changed.

        Arguments:
            model (Lead or Contact): Lead or Contact model which will be updated.
            field (string): Name of the field which will be updated.
            value (string): The new value of the field.

        Returns:
            boolean, True if the field was updated, False if the field was not updated.
        """
        if getattr(model, field) != value:
            setattr(model, field, value)
            return True
        return False

    def _update_lead_or_contact(self, model, user_data):
        """
        Updates a Lead or Contact model with the user account data.

        Arguments:
            model (Lead or Contact): Lead or Contact model which will be updated.
            user_data (dict): Dictionary containing user account and associated course purchase data.

        Returns:
            boolean, True if the model was updated, False if the model was not updated.
        """
        first_name, last_name = parse_user_full_name(user_data['full_name'])
        fields = (
            'email',
            'first_name',
            'last_name',
            'country',
            'year_of_birth',
            'language',
            'level_of_education',
            'interest',
            'gender',
            'registration_date',
        )
        data = (
            user_data['email'],
            first_name,
            last_name,
            COUNTRIES_BY_CODE.get((user_data['country'] or '').upper()),
            str(user_data['year_of_birth']),
            settings.LANGUAGES_BY_CODE.get(user_data['language']),
            EDUCATION_BY_CODE.get((user_data['level_of_education'] or '').lower()),
            user_data['goals'].strip() or None,
            (user_data['gender'] or '').upper() or None,
            # Truncate microseconds because Salesforce DateTime fields do not support microsecond precision
            pytz.utc.localize(user_data['registration_date'].replace(microsecond=0)),
        )

        model_updated = False
        for field, value in izip(fields, data):
            model_updated = self._update_field(model, field, value) or model_updated

        if model_updated:
            model.save()

        return model_updated

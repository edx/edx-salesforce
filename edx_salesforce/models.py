# -*- coding: utf-8 -*-
"""Database models for edx_salesforce."""

from __future__ import absolute_import, unicode_literals

from salesforce import models

from edx_salesforce.choices import COUNTRIES


class Account(models.Model):
    """Model that maps to Salesforce Account/Organization object."""

    name = models.CharField(max_length=255, verbose_name='Account Name')

    class Meta(models.Model.Meta):
        db_table = 'Account'
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'

    def __unicode__(self):
        """Return unicode representation of object."""
        return self.name


class Campaign(models.Model):
    """Model that maps to Salesforce Campaign object."""

    name = models.CharField(max_length=80)

    class Meta(models.Model.Meta):
        db_table = 'Campaign'
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'

    def __unicode__(self):
        """Return unicode representation of object."""
        return self.name


class CampaignMember(models.Model):
    """Model that maps to Salesforce CampaignMember object."""

    campaign = models.ForeignKey(Campaign, models.DO_NOTHING)
    lead = models.ForeignKey('Lead', models.DO_NOTHING)

    class Meta(models.Model.Meta):
        db_table = 'CampaignMember'
        verbose_name = 'Campaign Member'
        verbose_name_plural = 'Campaign Members'

    def __unicode__(self):
        """Return unicode representation of object."""
        return '{}:{}'.format(self.campaign, self.lead)


class Contact(models.Model):
    """Model that maps to Salesforce Contact object."""

    account = models.ForeignKey(Account, models.DO_NOTHING, blank=True, null=True)
    last_name = models.CharField(max_length=80)
    first_name = models.CharField(max_length=40, blank=True, null=True)
    name = models.CharField(max_length=121, verbose_name='Full Name', sf_read_only=models.READ_ONLY)
    email = models.EmailField()
    year_of_birth = models.CharField(custom=True, db_column='Year_of_Birth__c', max_length=255,
                                     verbose_name='Year of Birth', blank=True, null=True)
    language = models.CharField(custom=True, max_length=255, blank=True, null=True)
    country = models.CharField(custom=True, max_length=255, choices=COUNTRIES, blank=True, null=True)
    pi_utm_campaign = models.CharField(db_column='pi__utm_campaign__c', custom=True, max_length=255,
                                       verbose_name='Google Analytics Campaign', blank=True, null=True)
    pi_utm_content = models.CharField(db_column='pi__utm_content__c', custom=True, max_length=255,
                                      verbose_name='Google Analytics Content', blank=True, null=True)
    pi_utm_medium = models.CharField(db_column='pi__utm_medium__c', custom=True, max_length=255,
                                     verbose_name='Google Analytics Medium', blank=True, null=True)
    pi_utm_source = models.CharField(db_column='pi__utm_source__c', custom=True, max_length=255,
                                     verbose_name='Google Analytics Source', blank=True, null=True)
    pi_utm_term = models.CharField(db_column='pi__utm_term__c', custom=True, max_length=255,
                                   verbose_name='Google Analytics Term', blank=True, null=True)
    registration_date = models.DateTimeField(custom=True, db_column='Registration_Date__c',
                                             verbose_name='Registration Date', blank=True, null=True)
    level_of_education = models.CharField(custom=True, db_column='Level_of_Education__c', max_length=255,
                                          verbose_name='Level of Education', blank=True, null=True)
    interest = models.TextField(custom=True, blank=True)
    gender = models.CharField(custom=True, max_length=255, blank=True, null=True)

    class Meta(models.Model.Meta):
        db_table = 'Contact'
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'

    def __unicode__(self):
        """Return unicode representation of object."""
        return self.name


class DiscountCode(models.Model):
    """Model that maps to Salesforce DiscountCode object."""

    name = models.CharField(max_length=80, verbose_name='Discount Code Name')

    class Meta(models.Model.Meta):
        db_table = 'Discount_Code__c'
        verbose_name = 'Discount Code'
        verbose_name_plural = 'Discount Codes'

    def __unicode__(self):
        """Return unicode representation of object."""
        return self.name


class Lead(models.Model):
    """Model that maps to Salesforce Lead object."""

    last_name = models.CharField(max_length=80)
    first_name = models.CharField(max_length=40, blank=True, null=True)
    company = models.CharField(max_length=255, verbose_name='Organization')
    email = models.EmailField()
    status = models.CharField(max_length=40, default=models.DEFAULTED_ON_CREATE)
    is_converted = models.BooleanField(verbose_name='Converted', sf_read_only=models.NOT_UPDATEABLE,
                                       default=models.DEFAULTED_ON_CREATE)
    converted_account = models.ForeignKey(Account, models.DO_NOTHING, sf_read_only=models.READ_ONLY, blank=True,
                                          null=True)
    converted_contact = models.ForeignKey(Contact, models.DO_NOTHING, sf_read_only=models.READ_ONLY, blank=True,
                                          null=True)
    username = models.CharField(custom=True, max_length=100)
    year_of_birth = models.CharField(custom=True, db_column='Year_of_Birth__c', max_length=255,
                                     verbose_name='Year of Birth',
                                     blank=True, null=True)
    language = models.CharField(custom=True, max_length=255, blank=True, null=True)
    country = models.CharField(db_column='Country__c', custom=True, max_length=255, choices=COUNTRIES, blank=True,
                               null=True)
    pi_utm_campaign = models.CharField(db_column='pi__utm_campaign__c', custom=True, max_length=255,
                                       verbose_name='Google Analytics Campaign', blank=True, null=True)
    pi_utm_content = models.CharField(db_column='pi__utm_content__c', custom=True, max_length=255,
                                      verbose_name='Google Analytics Content', blank=True, null=True)
    pi_utm_medium = models.CharField(db_column='pi__utm_medium__c', custom=True, max_length=255,
                                     verbose_name='Google Analytics Medium', blank=True, null=True)
    pi_utm_source = models.CharField(db_column='pi__utm_source__c', custom=True, max_length=255,
                                     verbose_name='Google Analytics Source', blank=True, null=True)
    pi_utm_term = models.CharField(db_column='pi__utm_term__c', custom=True, max_length=255,
                                   verbose_name='Google Analytics Term', blank=True, null=True)
    programs = models.CharField(custom=True, max_length=4099, default='OpenClassroom')
    registration_date = models.DateTimeField(custom=True, db_column='Registration_Date__c',
                                             verbose_name='Registration Date', blank=True, null=True)
    level_of_education = models.CharField(custom=True, db_column='Level_of_Education__c', max_length=255,
                                          verbose_name='Level of Education', blank=True, null=True)
    interest = models.TextField(custom=True, blank=True)
    gender = models.CharField(custom=True, max_length=255, blank=True, null=True)

    class Meta(models.Model.Meta):
        db_table = 'Lead'
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'

    def __unicode__(self):
        """Return unicode representation of object."""
        return self.username


class Opportunity(models.Model):
    """Model that maps to Salesforce Opportunity object."""

    account = models.ForeignKey(Account, models.DO_NOTHING, blank=True, null=True)
    name = models.CharField(max_length=120)
    stage_name = models.CharField(max_length=40, verbose_name='Stage')
    amount = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    close_date = models.DateField(verbose_name='Close Date')
    paid_date = models.DateField(db_column='Paid_Date__c', custom=True, verbose_name='Paid Date')
    campaign = models.ForeignKey(Campaign, models.DO_NOTHING, blank=True, null=True)

    class Meta(models.Model.Meta):
        db_table = 'Opportunity'
        verbose_name = 'Opportunity'
        verbose_name_plural = 'Opportunities'

    def __unicode__(self):
        """Return unicode representation of object."""
        return self.name


class OpportunityContactRole(models.Model):
    """Model that maps to Salesforce OpportunityContactRole object."""

    opportunity = models.ForeignKey(Opportunity, models.DO_NOTHING, sf_read_only=models.NOT_UPDATEABLE)
    contact = models.ForeignKey(Contact, models.DO_NOTHING)
    role = models.CharField(max_length=40, blank=True, null=True)
    is_primary = models.BooleanField(verbose_name='Primary', default=models.DEFAULTED_ON_CREATE)

    class Meta(models.Model.Meta):
        db_table = 'OpportunityContactRole'
        verbose_name = 'Opportunity Contact Role'
        verbose_name_plural = 'Opportunity Contact Role'

    def __unicode__(self):
        """Return unicode representation of object."""
        return '{}:{}'.format(self.opportunity, self.contact)


class OpportunityLineItem(models.Model):
    """Model that maps to Salesforce OpportunityLineItem object."""

    opportunity = models.ForeignKey(Opportunity, models.DO_NOTHING)
    pricebook_entry = models.ForeignKey('PricebookEntry', models.DO_NOTHING, sf_read_only=models.NOT_UPDATEABLE)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    total_price = models.DecimalField(max_digits=18, decimal_places=2, default=models.DEFAULTED_ON_CREATE,
                                      blank=True, null=True)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2, verbose_name='Sales Price',
                                     default=models.DEFAULTED_ON_CREATE, blank=True, null=True)
    list_price = models.DecimalField(max_digits=18, decimal_places=2, sf_read_only=models.READ_ONLY,
                                     blank=True, null=True)
    discount_code = models.ForeignKey(DiscountCode, models.DO_NOTHING, db_column='Discount_Code__c', custom=True,
                                      blank=True, null=True)

    class Meta(models.Model.Meta):
        db_table = 'OpportunityLineItem'
        verbose_name = 'Opportunity Product'
        verbose_name_plural = 'Opportunity Product'

    def __unicode__(self):
        """Return unicode representation of object."""
        return '{}:{}'.format(self.opportunity, self.pricebook_entry)


class Pricebook2(models.Model):
    """Model that maps to Salesforce Pricebook2 object."""

    name = models.CharField(max_length=255, verbose_name='Price Book Name')
    is_standard = models.BooleanField(verbose_name='Is Standard Price Book')

    class Meta(models.Model.Meta):
        db_table = 'Pricebook2'
        verbose_name = 'Price Book'
        verbose_name_plural = 'Price Books'

    def __unicode__(self):
        """Return unicode representation of object."""
        return self.name


class PricebookEntry(models.Model):
    """Model that maps to Salesforce PricebookEntry object."""

    pricebook2 = models.ForeignKey(Pricebook2, models.DO_NOTHING, sf_read_only=models.NOT_UPDATEABLE)
    product2 = models.ForeignKey('Product2', models.DO_NOTHING, sf_read_only=models.NOT_UPDATEABLE)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2, verbose_name='List Price')
    is_active = models.BooleanField(verbose_name='Active', default=models.DEFAULTED_ON_CREATE)

    class Meta(models.Model.Meta):
        db_table = 'PricebookEntry'
        verbose_name = 'Price Book Entry'
        verbose_name_plural = 'Price Book Entries'

    def __unicode__(self):
        """Return unicode representation of object."""
        return '{}:{}'.format(self.pricebook2, self.product2)


class Product2(models.Model):
    """Model that maps to Salesforce Product2 object."""

    name = models.CharField(max_length=255, verbose_name='Product Name')

    class Meta(models.Model.Meta):
        db_table = 'Product2'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __unicode__(self):
        """Return unicode representation of object."""
        return self.name

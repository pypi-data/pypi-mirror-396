from lxml import etree

from accounting_vod.builder import build_xml
from accounting_vod.definitions import construct_vod_json


class Partner:
    def __init__(self, code, name, address, zip_code, city, country, tax_number, tax_payer=True):
        self.code = code
        self.name = name
        self.address = address or ''
        self.zip_code = zip_code or ''
        self.city = city or ''
        self.country = country or ''
        self.tax_number = tax_number or ''
        self.tax_payer = tax_payer


class Entry:
    def __init__(self,
                 entry_type,   # one from the VOD standard - 'Ne_gre_v_knjigo'
                 document_type,   # IR - izdani racun, PR - prejeti racun, BL - blagajna, T - temeljnica
                 account_code,
                 cost_code=None,   # stroskovno mesto
                 analytic1=None,
                 analytic2=None,
                 analytic3=None,
                 analytic4=None,
                 analytic5=None,
                 analytic6=None,
                 debit=None,
                 credit=None,
                 currency_debit=None,
                 currency_credit=None,
                 currency=None,
                 vat_base=None,
                 opening_entry=False,
                 partner=None):
        self.entry_type = entry_type
        self.document_type = document_type
        self.account_code = account_code
        self.cost_code = cost_code
        self.analytic1 = analytic1
        self.analytic2 = analytic2
        self.analytic3 = analytic3
        self.analytic4 = analytic4
        self.analytic5 = analytic5
        self.analytic6 = analytic6
        self.debit = debit
        self.credit = credit
        self.currency_debit = currency_debit
        self.currency_credit = currency_credit
        self.currency = currency
        self.vat_base = vat_base
        self.opening_entry = opening_entry
        self.partner = partner


class Attachment:
    def __init__(self, id, base64_content, content_type='PDF'):
        self.id = id
        self.base64_content = base64_content
        self.content_type = content_type

class Document:
    TYPE_PREJETI_RACUN = 'Prejeti_racun'
    TYPE_PREJETI_BREMEPIS = 'Prejeti_bremepis'
    TYPE_PREJET_AVANSNI_RACUN = 'Prejet_avansni_racun'
    TYPE_PREJETI_ECL = 'PrejetiECL'
    TYPE_PREJETI_NEDAVCNI_RACUN = 'Prejeti_nedavcni_racun'
    TYPE_PREJETI_RACUN_SAMOOBDAVCITEV = 'Prejeti_racun_samoobdavcitev'
    TYPE_IZDANI_RACUN = 'Izdani_racun'
    TYPE_IZDANI_DOBROPIS = 'Izdani_dobropis'
    TYPE_IZDANI_AVANSNI_RACUN = 'Izdani_avansni_racun'
    TYPE_TEMELJNICA = 'Temeljnica'

    MARKET_HOME = 'Domac'
    MARKET_EU = 'EU'
    MARKET_OTHER = 'Tretji_svet'

    def __init__(self,
                 document_type,
                 market,
                 document_number,
                 date_document,
                 date_of_service,
                 date_of_entry,
                 date_issued_received,
                 date_vat=None,
                 date_due=None,
                 description=None
                 ):
        self.document_type = document_type
        self.market = market
        self.document_number = document_number
        self.date_document = date_document
        self.date_of_service = date_of_service
        self.date_of_entry = date_of_entry
        self.date_issued_received = date_issued_received
        self.date_vat = date_vat
        self.date_due = date_due
        self.description = description

        self.partner = None
        self.attachment = None
        self.entries = []

    def add_partner(self, code, name, address, zip_code, city, country, tax_number, tax_payer=True):
        """
        Add partner to the document if only one partner is present.

        :param code:
        :param name:
        :param address:
        :param zip_code:
        :param city:
        :param country:
        :param tax_number:
        :param tax_payer:
        :return:
        """
        self.partner = Partner(code=code, name=name, address=address, zip_code=zip_code, city=city,
                               country=country, tax_number=tax_number, tax_payer=tax_payer)

        return self.partner

    def set_attachment(self, attachment: Attachment):
        self.attachment = attachment

    def add_journal_entry(self,
                          entry_type,  # one from the VOD standard - 'Ne_gre_v_knjigo'
                          document_type,  # IR - izdani racun, PR - prejeti racun, BL - blagajna, T - temeljnica
                          account_code,
                          cost_code=None,  # stroskovno mesto
                          analytic1=None,
                          analytic2=None,
                          analytic3=None,
                          analytic4=None,
                          analytic5=None,
                          analytic6=None,
                          debit=None,
                          credit=None,
                          currency_debit=None,
                          currency_credit=None,
                          currency=None,
                          vat_base=None,
                          opening_entry=False,
                          partner=None):
        entry = Entry(entry_type=entry_type,
                      document_type=document_type,
                      account_code=account_code,
                      cost_code=cost_code,
                      analytic1=analytic1,
                      analytic2=analytic2,
                      analytic3=analytic3,
                      analytic4=analytic4,
                      analytic5=analytic5,
                      analytic6=analytic6,
                      debit=debit,
                      credit=credit,
                      currency_debit=currency_debit,
                      currency_credit=currency_credit,
                      currency=currency,
                      vat_base=vat_base,
                      opening_entry=opening_entry,
                      partner=partner)

        self.entries.append(entry)

        return entry


class VODExport:
    def __init__(self, app_name, app_version, app_author):
        self.app_name = app_name
        self.app_version = app_version
        self.app_author = app_author

        self.documents = []

    def add_document(self, document):
        self.documents.append(document)

    def render_xml(self):
        xml_content = build_xml(construct_vod_json(self))

        return ("%s%s" % ('<?xml version="1.0" encoding="UTF-8"?>\n',
                          etree.tostring(xml_content,
                                         pretty_print=True,
                                         xml_declaration=False,
                                         ).decode('utf-8')))

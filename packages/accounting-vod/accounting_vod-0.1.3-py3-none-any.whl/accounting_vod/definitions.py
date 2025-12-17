import textwrap


def construct_vod_json(vod_export):
    data = {
        '_name': 'Prenos',
        'header': {
            '_name': 'Glava',
            'app': {
                '_name': 'Program',
                '_value': vod_export.app_name,
            },
            'version': {
                '_name': 'Program_verzija',
                '_value': vod_export.app_version,
            },
            'author': {
                '_name': 'Program_avtor',
                '_value': vod_export.app_author,
            },
            'xml_version': {
                '_name': 'Verzija_xml',
                '_value': '0.1',
            }
        },
        'body': {
            '_name': 'Telo',
        }
    }

    for i, document in enumerate(vod_export.documents):
        data['body'][f'document_{i}'] = build_document_json(document)

    return data


def build_document_json(document):
    data = {
        '_name': 'Dokument',
        'document_type': {
            '_name': 'Dokument',
            '_value': document.document_type
        },
        'market': {
            '_name': 'Trg',
            '_value': document.market
        },
        'document_number': {
            '_name': 'Stevilka_dokumenta',
            '_value': document.document_number
        },
        'date_document': {
            '_name': 'Datum_dokumenta',
            '_value': document.date_document.isoformat()
        },
        'date_of_service': {
            '_name': 'Datum_dur',
            '_value': document.date_of_service.isoformat()
        },
        'accounting_period': {
            '_name': 'Obracunsko_obdobje',
            'month': {
                '_name': 'Mesec',
                '_value': str(document.date_of_service.month)
            },
            'year': {
                '_name': 'Leto',
                '_value': str(document.date_of_service.year)
            },
        },
        'date_of_entry': {
            '_name': 'Datum_knjizenja',
            '_value': document.date_of_entry.isoformat()
        },
        'date_issued_received': {
            '_name': 'Datum_prejema_izdaje',
            '_value': document.date_issued_received.isoformat()
        },
    }

    if document.date_vat:
        data['date_vat'] = {
            '_name': 'Datum_ddv',
            '_value': document.date_vat.isoformat()
        }

    if document.date_due:
        data['date_due'] = {
            '_name': 'Datum_zapadlosti',
            '_value': document.date_due.isoformat()
        }

    if document.partner:
        data['partner'] = build_partner_json(document.partner)

    if document.attachment:
        data['attachment'] = {
            '_name': 'Sken',
            'attachment_id': {
                '_name': 'Sken_ID',
                '_value': str(document.attachment.id)
            },
            'attachment_part': {
                '_name': 'Slike',
                'attachment': {
                    '_name': 'Slika',
                    'format': {
                        '_name': 'Format',
                        '_value': document.attachment.content_type
                    },
                    'raw': {
                        '_name': 'RAW',
                        '_value': document.attachment.base64_content
                    }
                }
            }
        }

    for i, entry in enumerate(document.entries):
        data[f'entry_{i}'] = build_entry_json(entry)

    return data


def build_partner_json(partner):
    data = {
        '_name': 'Partner',
        '_sorting': ['Sifra', 'Naziv1', 'Naziv2', 'Naziv3', 'Naslov', 'Postna_stevilka', 'Kraj', 'Drzava',
                     'DDV_status', 'Identifikacijska_stevilka'],
        'code': {
            '_name': 'Sifra',
            '_value': partner.code
        },
        'address': {
            '_name': 'Naslov',
            '_value': partner.address[:35]
        },
        'zip': {
            '_name': 'Postna_stevilka',
            '_value': str(partner.zip_code)
        },
        'city': {
            '_name': 'Kraj',
            '_value': partner.city
        },
        'country': {
            '_name': 'Drzava',
            '_value': str(partner.country)
        },
        'tax_number': {
            '_name': 'Identifikacijska_stevilka',
            '_value': str(partner.tax_number)
        },
        'tax_payer': {
            '_name': 'DDV_status',
            '_value': 'Davcni_zavezanec' if partner.tax_payer else 'Nedavcni_zavezanec'
        },
    }

    business_name_split = textwrap.wrap(partner.name, 35, break_long_words=True)

    for i, bn_part in enumerate(business_name_split):
        i = i + 1  # Start from 1
        data[f"name_part_{i}"] = {
            '_name': f"Naziv{i}",
            '_value': bn_part
        }

        if i == 3:
            break  # Stop at max length



    return data


def build_entry_json(entry):
    data = {
        '_name': 'Knjizba',
        '_sorting': ['Vrsta_knjizbe', 'Vrsta_dokumenta', 'Konto', 'Partner', 'Stroskovno_mesto', 'Analitika1',
                     'Analitika2', 'Analitika3', 'Analitika4', 'Analitika5', 'Analitika6', 'Debet', 'Kredit',
                     'Valuta_debet', 'Valuta_kredit', 'Osnova', 'Otvoritev', 'Sifra_valute'],
        'entry_type': {
            '_name': 'Vrsta_knjizbe',
            '_value': entry.entry_type
        },
        'document_type': {
            '_name': 'Vrsta_dokumenta',
            '_value': entry.document_type
        },
        'account': {
            '_name': 'Konto',
            '_value': str(entry.account_code)
        },
        'opening': {
            '_name': 'Otvoritev',
            '_value': '1' if entry.opening_entry else '0'
        }
    }

    if entry.partner:
        data['partner'] = build_partner_json(entry.partner)

    if entry.cost_code:
        data['cost_code'] = {
            '_name': 'Stroskovno_mesto',
            '_value': str(entry.cost_code)
        }

    if entry.analytic1:
        data['analytic1'] = {
            '_name': 'Analitika1',
            '_value': str(entry.analytic1)
        }

    if entry.analytic2:
        data['analytic2'] = {
            '_name': 'Analitika2',
            '_value': str(entry.analytic2)
        }

    if entry.analytic3:
        data['analytic3'] = {
            '_name': 'Analitika3',
            '_value': str(entry.analytic3)
        }

    if entry.analytic4:
        data['analytic4'] = {
            '_name': 'Analitika4',
            '_value': str(entry.analytic4)
        }

    if entry.analytic5:
        data['analytic5'] = {
            '_name': 'Analitika5',
            '_value': str(entry.analytic5)
        }

    if entry.analytic6:
        data['analytic6'] = {
            '_name': 'Analitika6',
            '_value': str(entry.analytic6)
        }

    if entry.currency:
        data['currency'] = {
            '_name': 'Sifra_valute',
            '_value': str(currency_to_currency_code(entry.currency))
        }

    if entry.debit:
        data['debit'] = {
            '_name': 'Debet',
            '_value': str(entry.debit)
        }
        data['debit_currency'] = {
            '_name': 'Valuta_debet',
            '_value': str(entry.currency_debit)
        }
    else:
        data['credit'] = {
            '_name': 'Kredit',
            '_value': str(entry.credit)
        }
        data['debit_currency'] = {
            '_name': 'Valuta_kredit',
            '_value': str(entry.currency_credit)
        }

    if entry.vat_base:
        data['vat_base'] = {
            '_name': 'Osnova',
            '_value': str(entry.vat_base)
        }

    return data


def currency_to_currency_code(currency):
    if currency.upper() == 'USD':
        return 840
    elif currency.upper() == 'EUR':
        return 978

    return currency

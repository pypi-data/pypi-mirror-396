# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import os
from base64 import b64encode
from decimal import Decimal

import genshi
import genshi.template
from cryptography import x509
from cryptography.hazmat.primitives.serialization import Encoding
# XXX fix: https://genshi.edgewall.org/ticket/582
from genshi.template.astutil import ASTCodeGenerator, ASTTransformer
from lxml import etree
from signxml import DigestAlgorithm
from signxml.util import add_pem_header, ds_tag, xades_tag
from signxml.xades import (
    XAdESDataObjectFormat, XAdESSignaturePolicy, XAdESSigner)

from trytond.model import Model
from trytond.pool import Pool
from trytond.rpc import RPC
from trytond.tools import cached_property
from trytond.transaction import Transaction

if not hasattr(ASTCodeGenerator, 'visit_NameConstant'):
    def visit_NameConstant(self, node):
        if node.value is None:
            self._write('None')
        elif node.value is True:
            self._write('True')
        elif node.value is False:
            self._write('False')
        else:
            raise Exception("Unknown NameConstant %r" % (node.value,))
    ASTCodeGenerator.visit_NameConstant = visit_NameConstant
if not hasattr(ASTTransformer, 'visit_NameConstant'):
    # Re-use visit_Name because _clone is deleted
    ASTTransformer.visit_NameConstant = ASTTransformer.visit_Name

loader = genshi.template.TemplateLoader(
    os.path.join(os.path.dirname(__file__), 'template'),
    auto_reload=True)


def remove_comment(stream):
    for kind, data, pos in stream:
        if kind is genshi.core.COMMENT:
            continue
        yield kind, data, pos


def strip_spaces(str):
    return ''.join(str.split(' '))


class Invoice(Model):
    "EDocument Spanish Facturae Invoice"
    __name__ = 'edocument.es.facturae.invoice'
    __no_slots__ = True  # to work with cached_property

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.__rpc__.update({
                'render': RPC(instantiate=0),
                })

    def __init__(self, invoice):
        super().__init__()
        pool = Pool()
        Invoice = pool.get('account.invoice')
        Lang = pool.get('ir.lang')
        lang = None
        if int(invoice) >= 0:
            invoice = Invoice(int(invoice))
            lang = invoice.party_lang
            with Transaction().set_context(language=invoice.party_lang):
                self.invoice = invoice.__class__(int(invoice))
        else:
            self.invoice = invoice
        self.lang = Lang.get(lang)

    def render(self, version):
        if self.invoice.state not in {'posted', 'paid'}:
            raise ValueError("Invoice must be posted")
        tmpl = self._get_template(version)
        if not tmpl:
            raise NotImplementedError
        content = (tmpl.generate(
            this=self, Decimal=Decimal, strip_spaces=strip_spaces)
            .filter(remove_comment)
            .render().encode('utf-8'))
        key = self.invoice.company.es_facturae_private_key
        cert = self.invoice.company.es_facturae_certificate
        if key and cert:
            # XXX Remove me when
            # https://github.com/XML-Security/signxml/issues/281 is merged
            signer = FacturaeSigner(**self._get_xades_signature_options(
                version))
            root = etree.fromstring(content)
            signed = signer.sign(root, cert=cert, key=key)
            return etree.tostring(
                signed, xml_declaration=True, encoding='UTF-8')
        return content

    def _get_xades_signature_options(self, version):

        signature_policy = XAdESSignaturePolicy(
            Identifier=('http://www.facturae.es/politica_de_firma_'
                'formato_facturae/politica_de_firma_formato_facturae'
                '_v3_1.pdf'),
            Description=("Política de firma electrónica para facturación "
                "electrónica con formato Facturae"),
            DigestMethod=DigestAlgorithm.SHA1,
            DigestValue='Ohixl6upD6av8N7pEvDABhEL6hM=',
        )
        c14n_algorithm = 'http://www.w3.org/TR/2001/REC-xml-c14n-20010315'
        role = 'emisor' if self.invoice.type == 'out' else 'receptor'
        return {
            'signature_policy': signature_policy,
            'claimed_roles': [role],
            'data_object_format': XAdESDataObjectFormat(
                Description="Factura electrónica",
                MimeType="text/xml",
                ),
            'c14n_algorithm': c14n_algorithm,
            'add_legacy_certificate': True,
            }

    def _get_template(self, version):
        return loader.load(os.path.join(version, 'Facturae.xml'))

    def format_date(self, date, format=None):
        return self.lang.strftime(date, format=format)

    @cached_property
    def batch_identifier(self):
        parts = []
        if self.seller_tax_identifier:
            parts.append(self.seller_tax_identifier.es_code())
        parts.append(self.invoice.number)
        return ''.join(parts)

    @cached_property
    def lines(self):
        return [l for l in self.invoice.lines if l.type == 'line']

    @cached_property
    def seller_party(self):
        if self.invoice.type == 'out':
            return self.invoice.company.party
        else:
            return self.invoice.party

    @cached_property
    def seller_address(self):
        if self.invoice.type == 'out':
            return self.invoice.company.party.address_get('invoice')
        else:
            return self.invoice.invoice_address

    @cached_property
    def seller_tax_identifier(self):
        if self.invoice.type == 'out':
            return self.invoice.tax_identifier
        else:
            return self.invoice.party_tax_identifier

    @cached_property
    def seller_administrative_centers(self):
        if self.invoice.type == 'out':
            return (
                self.invoice.company.party.es_facturae_administrative_centers)
        else:
            return self.invoice.es_facturae_administrative_centers

    @cached_property
    def buyer_party(self):
        if self.invoice.type == 'out':
            return self.invoice.party
        else:
            return self.invoice.company.party

    @cached_property
    def buyer_address(self):
        if self.invoice.type == 'out':
            return self.invoice.invoice_address
        else:
            return self.invoice.company.party.address_get('invoice')

    @cached_property
    def buyer_tax_identifier(self):
        if self.invoice.type == 'out':
            return self.invoice.party_tax_identifier
        else:
            return self.invoice.tax_identifier

    @cached_property
    def buyer_administrative_centers(self):
        if self.invoice.type == 'out':
            return self.invoice.es_facturae_administrative_centers
        else:
            return (
                self.invoice.company.party.es_facturae_administrative_centers)

    @cached_property
    def invoice_number(self):
        return self.invoice.number

    @cached_property
    def invoice_series_code(self):
        return ''

    @cached_property
    def invoice_document_type(self):
        return 'FC'

    @cached_property
    def invoice_class(self):
        if self.invoice.es_facturae_corrective_invoices:
            return 'OR'
        return 'OO'

    @cached_property
    def operation_date(self):
        pass

    @cached_property
    def invoicing_start_date(self):
        pass

    @cached_property
    def invoicing_end_date(self):
        pass

    @cached_property
    def place_of_issue_post_code(self):
        pass

    @cached_property
    def place_of_issue_description(self):
        pass

    @cached_property
    def exchange_rate(self):
        pass

    @cached_property
    def exchange_rate_date(self):
        pass

    @cached_property
    def invoice_receiver_transaction_reference(self):
        pass

    @cached_property
    def invoice_file_reference(self):
        pass

    @cached_property
    def delivery_notes_references(self):
        return []

    @cached_property
    def invoice_description(self):
        return self.invoice.description

    @cached_property
    def additional_information(self):
        return self.invoice.comment

    @cached_property
    def payment_means(self):
        if self.invoice and self.invoice.payment_term:
            return self.invoice.payment_term.es_facturae_type

    @cached_property
    def account_to_be_credited(self):
        # Account only required for 04 payment means
        if self.payment_means != '04':
            return
        if self.invoice.type == 'out':
            party = self.invoice.company.party
        else:
            party = self.invoice.party
        for account in getattr(party, 'bank_accounts', []):
            if account.iban:
                for number in self.numbers:
                    if number.type == 'iban':
                        return number.number_compact
        return ''

    def item_description(self, line):
        parts = []
        if line.product:
            parts.append(line.product.rec_name)
        if line.description:
            parts.extend(line.description.split('\n'))
        if not parts:
            parts.append(line.account.rec_name)
        return '\n'.join(parts)

    def item_start_period(self, line):
        pass

    def item_end_period(self, line):
        pass

    def item_file_reference(self, line):
        pass

    def item_file_date(self, line):
        pass

    def sequence_number(self, line):
        pass

    def issuer_contract_reference(self, line):
        pass

    def issuer_contract_date(self, line):
        pass

    def issuer_transaction_reference(self, line):
        pass

    def issuer_transaction_date(self, line):
        pass

    def receiver_contract_reference(self, line):
        pass

    def receiver_contract_date(self, line):
        pass

    def receiver_transaction_reference(self, line):
        pass

    def receiver_transaction_date(self, line):
        pass


class FacturaeSigner(XAdESSigner):
    """
    Custom signer that emits both SigningCertificate (SHA1 + issuer/serial)
    and SigningCertificateV2 (digest with configured algorithm) with issuer
    in fixed C,O,OU,CN order to satisfy CAOC/VALid2 and FACE.
    """

    def __init__(self, **kwargs):
        self._add_legacy_certificate = kwargs.pop(
            'add_legacy_certificate', False)
        super().__init__(**kwargs)

    def add_signing_certificate(self,
            signed_signature_properties, sig_root, signing_settings):
        if (not self._add_legacy_certificate
                or signed_signature_properties.find(
                    "xades:SigningCertificate",
                    namespaces=self.namespaces)) is not None:
            return

        signing_cert = etree.SubElement(
            signed_signature_properties, xades_tag("SigningCertificate"),
            nsmap=self.namespaces
        )
        signing_cert_v2 = etree.SubElement(
            signed_signature_properties, xades_tag("SigningCertificateV2"),
            nsmap=self.namespaces
        )
        assert signing_settings.cert_chain is not None
        for cert in signing_settings.cert_chain:
            if isinstance(cert, x509.Certificate):
                loaded_cert = cert
            else:
                loaded_cert = x509.load_pem_x509_certificate(
                    add_pem_header(cert))
            der = loaded_cert.public_bytes(Encoding.DER)
            sha1 = self._get_digest(der, algorithm=DigestAlgorithm.SHA1)
            shaX = self._get_digest(der, algorithm=self.digest_alg)

            # Legacy block for CAOC/VALid2
            cert_node = etree.SubElement(signing_cert, xades_tag("Cert"),
                nsmap=self.namespaces)
            cert_digest = etree.SubElement(cert_node, xades_tag("CertDigest"),
                nsmap=self.namespaces)
            etree.SubElement(cert_digest, ds_tag("DigestMethod"),
                nsmap=self.namespaces,
                            Algorithm=DigestAlgorithm.SHA1.value)
            etree.SubElement(cert_digest, ds_tag("DigestValue"),
                nsmap=self.namespaces).text = b64encode(sha1).decode()
            issuer_serial = etree.SubElement(
                cert_node, xades_tag("IssuerSerial"), nsmap=self.namespaces)

            def _issuer_attr(issuer, oid):
                attrs = issuer.get_attributes_for_oid(oid)
                return attrs[0].value if attrs else None

            # Some certificates miss optional attributes (e.g. OU), so pick
            # only the ones that are present while keeping the expected order.
            issuer_parts = []
            for label, oid in (
                    ("C", x509.NameOID.COUNTRY_NAME),
                    ("O", x509.NameOID.ORGANIZATION_NAME),
                    ("OU", x509.NameOID.ORGANIZATIONAL_UNIT_NAME),
                    ("CN", x509.NameOID.COMMON_NAME)):
                value = _issuer_attr(loaded_cert.issuer, oid)
                if value is not None:
                    issuer_parts.append(f"{label}={value}")
            etree.SubElement(issuer_serial, ds_tag("X509IssuerName"),
                nsmap=self.namespaces).text = ",".join(issuer_parts)
            etree.SubElement(issuer_serial, ds_tag("X509SerialNumber"),
                nsmap=self.namespaces).text = str(
                loaded_cert.serial_number)

            # V2 block for FACE/modern validators
            cert_node_v2 = etree.SubElement(signing_cert_v2, xades_tag("Cert"),
                nsmap=self.namespaces)
            cert_digest_v2 = etree.SubElement(
                cert_node_v2, xades_tag("CertDigest"), nsmap=self.namespaces)
            etree.SubElement(cert_digest_v2, ds_tag("DigestMethod"),
                nsmap=self.namespaces,
                            Algorithm=self.digest_alg.value)
            etree.SubElement(cert_digest_v2, ds_tag("DigestValue"),
                nsmap=self.namespaces).text = b64encode(
                shaX).decode()

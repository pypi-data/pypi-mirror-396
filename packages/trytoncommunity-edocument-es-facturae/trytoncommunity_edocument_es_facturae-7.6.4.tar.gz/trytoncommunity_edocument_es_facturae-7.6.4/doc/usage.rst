*****
Usage
*****

The module adds the datatypes required to generate Spanish Electronic Invoices
following `Facturae <https://www.facturae.gob.es/>`_ format.

Generate facturae signature
===========================

Each facturae invoice can be optionally signed by using XADES encription.
To activate the encription a private key and a certificate must be added
to the `Company <company:model-company.company>` used to generate the invoice.
When no encription keys the invoice will be generated without XADES Encription.


Set party's default administrative centers
==========================================

The default `Administrative Centers <model-party.address>` for a party can
be set on its form. The administrative centers will be copied to the invoice
when selecting its party.

******
Design
******

The *Edocument Spanish Facturae* adds some new concepts and extends some
existing concepts.


Accounting Models
=================

A new facturae types is added to the following models:

    * `Taxes <account:model-account.tax>`
    * `Payment Term <account_invoice:model-account.invoice>`


.. _model-edocument.es_facturae.administrative_center:

Administrative Center
=====================

An administrative center is a represented by a party address a role and
and optional description.

.. _model-party.party:

Parties
=======

For each invoice it is possible to define it's administrative centers.
The administrative centers are used to generate the facturae invoices.

.. _report-edocument.es.facturae.invoice:

Facturae Edocument
===================

The facturae edocument can be used to render a facturae invoice using
supported versions.

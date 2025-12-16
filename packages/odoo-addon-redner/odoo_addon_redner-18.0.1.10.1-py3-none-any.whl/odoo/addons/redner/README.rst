======
Redner
======

.. |maturity| image:: https://img.shields.io/badge/maturity-Stable-green.png
    :target: https://odoo-community.org/page/development-status
    :alt: Stable
.. |license| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Ruff
.. |biome| image:: https://img.shields.io/badge/Biome-60a5fa?style=flat&logo=biome
    :target: https://biomejs.dev
    :alt: Biome

|maturity| |license| |ruff| |biome|

Produce reports & emails with Rednerd_.

Rednerd_ is an innovative solution to produce transactional emails
and documents in PDF or HTML format.

It's designed to help applications or websites that need to send transactional
email like password resets, order confirmations, and welcome messages.

With Rednerd_, you can create clear, professional reports and responsive email templates.
The module supports email templates designed in the Mailjet app, using MJML or Mustache.

Seamless Integration with Odoo ERP
==================================

Rednerd is fully integrated with Odoo ERP, allowing you to customize your MJML email templates directly in Odoo before sending the final version to Rednerd.

Document Rendering Made Easy
============================

This solution also enables automatic rendering of PDF or HTML. Quotes, invoices, or any other document can be automatically generated from your application data.

How To Get Started?
===================

Go to https://redner.orbeet.io/sign-in to create your account and set up your API key to connect Rednerd to your application.
Alternatively check our step-by-step tutorials_.

Once your account is ready, configure the module with the following ``ir.config_parameter``::

  redner.server_url = https://redner.orbeet.io
  redner.api_key = <your API key here>
  redner.account = <your account name>
  redner.timeout = 20

``redner.timeout`` is in seconds; defaults to 20 seconds per redner call.

**Pro tip**: You can use mjml-app_ to prototype your email templates.

Documentation
=============

If you need further information concerning Redner integration with Odoo ERP, you can check our step-by-step tutorials_.
Feel free to visit Orbeet_ website to discover all our solutions.

UI Changes
==========

* Setting > Redner > Templates

Note: When you have existing templates you want to register onto a new
redner server (or with a new user), multi-select them and click
"Send to redner server".

.. _mjml-app: http://mjmlio.github.io/mjml-app/
.. _Rednerd: https://orus.io/orus-io/rednerd

Credits
=======

Authors
-------

XCG SAS, part of Orbeet_.

.. _Orbeet: https://orbeet.io/
.. _tutorials: https://orbeet.io/services/generateur-documents-redner/api-key/

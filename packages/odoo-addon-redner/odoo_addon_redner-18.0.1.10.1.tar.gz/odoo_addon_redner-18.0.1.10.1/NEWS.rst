Changelog
=========

18.0.1.10.1
-----------

Fix the import wizard (avoid add a line).

Fix saving redner templates.

Improve redner message output to user.

Fix duplicating redner templates.

Fix writing to a non-saved template.

18.0.1.10.0
-----------

Improve import from redner server wizard.

Add path for redner templates action.

18.0.1.9.3
----------

Hide view in redner on redner template when using a Unix socket to connect to redner.

18.0.1.9.2
----------

Added URL sanitize to avoid potential SSRF.

Added default timeout on API calls to avoid potential infinite call.

18.0.1.9.1
----------

Replace all use of mktemp.

18.0.1.9.0
----------

Migrate to converter 18.0.7 API.
Update copyright and author to XCG SAS.
Fix pylint warnings and Remove type: ignore annotations.

18.0.1.8.3
----------

typst template are now text/typst instead of application/typst

18.0.1.8.2
-----------

- account_move redner emails: fix monkeypatch
  for regular mail_templates

18.0.1.8.1
----------

- account_move redner emails: fix monkeypatch

18.0.1.8.0
----------

- monkey patch 'account_move_send' to resolve
  account move preview and email when using redner templates

- redner-template: add default "New" description
  to override the required error when importing from redner

18.0.1.7.0
----------

Res config: add redner integration parameters (server_url, account, api_key)

Template locale is by default user locale, not fr_FR

Update Redner config parameter names in the README

Add more export formats from Typst

Improve substitution management in ir.actions.report and mail.template with value_type functionality.

18.0.1.6.0
----------

Declare compatibility with changes in converter 18.0.6.0.0.

requests_unixsocket is now an optional dependency, only needed when connecting to redner on a unix socket.

18.0.1.5.0
----------

Add typst language to redner odoo.

18.0.1.4.1
----------

Declare compatibility with changes in converter 18.0.5.0.0.

18.0.1.4.0
----------

Compatibility with changes in converter 18.0.4.0.0.

18.0.1.3.0
----------

Add neutralize script that remove configuration values.

18.0.1.2.2
----------

Improve _set_value_from_template for redner integration.

18.0.1.2.1
----------

eslint fixes.

18.0.1.2.0
----------

Improve dynamic placeholder implementation.

18.0.1.1.2
----------

Remove the hard requirement for python-magic by reusing odoo guess mimetype code and compatibility code between
different versions of python-magic.
Including the python-magic library is still recommended as Odoo uses it when available.

18.0.1.1.1
----------

Add missing python-magic requirement for package.

18.0.1.1.0
----------

Add dynamic expression button for substitution line and new converter features.

18.0.1.0.5
----------

Declare compatibility with odoo-addon-converter 18.0.3 series.

18.0.1.0.4
----------

Refactor redner.template model to improve template management.

18.0.1.0.3
----------

mail_template: add `find_or_create_partners` parameter to `_generate_template`.

18.0.1.0.2
----------

- Fix: ensure Redner instance reflects updated system parameters.
- Add python-magic as external dependency and fix print-paper-size metadata.
- Restriction Added: Disallow the deletion of a template if its source is Redner.
(Deletion is still allowed for templates created in Odoo but not for those originating from Redner.)
- Implement caching and optimization for Redner template handling.
- test: Fix timing discrepancy in Redner template version field during tests.

18.0.1.0.1
----------

Fix: Update test cases to match the API call structure.

18.0.1.0.0
----------

Initial version.

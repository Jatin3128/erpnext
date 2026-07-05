# Product Configuration Refactor Plan

Mission: make the Product Configuration engine simple to use with fewer clicks.
UX first. Dropping advanced features is acceptable. Everything about a product
reachable from the Template. Flow: Template > Configure > Product Configuration
> Calculate > Components > Create BOM > BOM.

Protocol: one item per iteration. TDD (test first). After each item run both
test modules, run pre-commit on changed files, then git add. Never commit,
never push, no PR. Tick items here with a one-line note of what changed and
which files were touched.

Tests:

```
bench --site test.site run-tests --module erpnext.manufacturing.doctype.product_configuration.test_product_configuration
bench --site test.site run-tests --module erpnext.manufacturing.doctype.product_configuration.test_product_configuration_formula
```

## R. Research

- [x] R0. Studied Odoo, SAP LO-VC, Salesforce CPQ, Tacton, Epicor CPQ (KBMax),
  Infor CPQ, DriveWorks, Shopify options. Wrote PC_RESEARCH.md; appended D4
  (auto rule summary) and promoted the E group to in scope. Files:
  PC_RESEARCH.md, PC_REFACTOR_PLAN.md. No product code.

## A. Remove complexity

- [x] A1. Removed the Expression condition mode: dropped condition_expression
  field, the Expression select option, and both depends_on gates from
  product_configuration_rule.json; deleted the Expression branch in
  rule_matches and its fetch in apply_rules (product_configuration.py);
  removed expression validation in product_configuration_rule.py; rewrote the
  Large Glass test rule to a structured Width > 1000 condition
  (test_product_configuration.py).
- [x] A2. variable_name: scrub fallback already existed; added identifier
  validation (isidentifier with a clear error) in
  product_configuration_attribute.py, made the field read_only in
  product_configuration_attribute.json, added
  test_variable_name_is_derived_and_validated (derivation + invalid name) in
  test_product_configuration.py.
- [x] A3. Template variables_section is now collapsible, labeled "Advanced
  (optional)", table relabeled "Derived Variables", description carries the
  area = width * height example. JSON only
  (product_configuration_template.json); nothing testable server-side, both
  modules still green.

## B. One place to build a product

- [x] B1. Added product_configuration_template_dashboard.py with fieldname
  "template": Rules (Product Configuration Rule) and, one line extra for
  hub-navigation, Configurations (Product Configuration). The connection's "+"
  gives one-click Add Rule with template preset. Test
  test_template_dashboard_links_rules goes through meta.get_dashboard_data().
- [x] B2. New product_configuration_template.js adds a "New Rule" button on
  saved templates that opens a new Rule with template preset via
  frappe.new_doc. JS wiring only, no server logic, so no server test; both
  modules still green, prettier and eslint pass.
- [x] B3. Template now has a "Configure" button opening a dialog built from
  whitelisted get_attribute_fields (one field per attribute: value_type as
  fieldtype, select options, default, mandatory, description) and submitting
  to whitelisted make_configuration(values) which creates, calculates, saves,
  and returns the Product Configuration name; JS routes to it. Files:
  product_configuration_template.py, product_configuration_template.js, test
  test_make_configuration_creates_and_calculates.

## C. Workflow buttons

- [x] C1. Added whitelisted create_bom() on Product Configuration: builds a
  draft BOM for template.configurable_item from components (company from
  default company, else the item's Item Default), friendly throws when the
  template item is unset or components are empty, sets status "BOM Created"
  and stores the link in the new read-only bom field. JS shows a primary
  "Create BOM" button when Calculated and routes to the BOM. Files:
  product_configuration.py/.js/.json, test_create_bom_guards_and_output.
- [x] C2. Renamed the button to "Calculate" and styled it primary while status
  is Draft; Create BOM stays the primary once Calculated. Auto-fetch on
  template select unchanged. product_configuration.js only.
- [x] C3. Added product_configuration_dashboard.py: internal link BOM via the
  bom field under a "Manufacture" connections group. Test
  test_configuration_dashboard_links_bom via meta.get_dashboard_data().

## D. Understand it at a glance

- [x] D1. Description pass across all ten doctype JSONs: template/status/bom/
  tables on Product Configuration; configurable_item (updated stale text) and
  attributes on Template; template/condition_logic (documents the empty-rows
  always-match behavior)/outputs on Rule; value_type/uom/default_value/
  description on Attribute; value on Attribute Value; source_rule on
  Component; operator and value (comma-list for in/not in) on Rule Condition;
  zero-skip note on Rule Output quantity_formula; mandatory/default/min/max on
  Template Attribute; variable_name on Template Variable. JSON only.
- [x] D2. Appended the full function list to the two formula field
  descriptions: quantity_formula (product_configuration_rule_output.json) and
  formula (product_configuration_template_variable.json). JSON only.
- [x] D3. Product Configuration validate now defaults title to the template
  name; title field description added. Files: product_configuration.py/.json,
  assert added to test_make_configuration_creates_and_calculates.
- [x] D4. Rule validate now writes an auto-generated read-only summary field
  ("If Material == Wood: add CEILING(area) x Frame", "Always: add ..." when
  unconditional), joined with and/or per condition_logic, shown in list view.
  Files: product_configuration_rule.py/.json, test
  test_rule_summary_is_generated.

## E. Guardrails (in scope per research: upfront validation is core
configurator UX, see PC_RESEARCH.md)

- [x] E1. calculate_components now calls validate_mandatory_values, which
  throws one error listing every mandatory attribute without a value
  (template_attributes query extended with the mandatory flag). Files:
  product_configuration.py, test test_calculate_requires_mandatory_values.
- [x] E2. calculate_components now also runs validate_value_limits: numeric
  values checked against the template row's min/max (0 means no limit, JSON
  descriptions updated) and Select values against the attribute's options,
  all violations reported in one message. Reuses attribute_masters from the
  template module. Files: product_configuration.py,
  product_configuration_template_attribute.json, test
  test_calculate_enforces_limits_and_select_options.
- [x] E3. build_context now throws "Formula for variable X failed: name 'y'
  is not defined" instead of silently storing 0 when a derived formula fails.
  Files: formula.py, test test_unknown_variable_in_derived_formula_raises in
  test_product_configuration_formula.py.

## Log

- 2026-07-03: pre-commit was not installed on this machine; installed it into
  the bench virtualenv (env/bin/pre-commit). Hook envs are cached.
- 2026-07-03: bench redis was down (this bench uses ports 13003/11003);
  started redis-server for config/redis_cache.conf and config/redis_queue.conf
  as daemons. Without redis, document inserts in tests fail on the global
  search queue assert.
- 2026-07-03: test.site did not exist and develop.local cannot run the suite
  (its real Fiscal Year 2026-2027 overlaps the ERPNext test fixtures). Created
  test.site on a scoped DB (db test_site_db, user test_site_db, admin password
  "admin") via bench new-site --no-setup-db, with allow_tests true. A
  full-privilege DB user was denied by policy, so the DB and scoped user were
  created directly via the unix_socket mariadb account.
- 2026-07-03: baseline on test.site: both test modules green (4 + 4 tests).

# Product Configurator Research (R0)

How best-in-class configurators and CPQ tools solve what the Product
Configuration engine does, and what is worth borrowing. Guardrail: an idea is
borrowed only if it reduces clicks or increases clarity without adding a
concept a first-time user must learn. Simplicity beats feature parity.

## Odoo Product Configurator

- What: adding a configurable product to a sales order opens one modal with
  every attribute, its allowed values, live price, and exclusions enforced in
  real time.
- Borrow: the single-dialog entry point at the moment of need. This is exactly
  plan item B3 (Configure dialog on the Template), with defaults pre-filled so
  most configurations are two or three edits and one click.
- Reject: automatic variant generation and the exclusion matrix. Both add
  concepts (variants, exclusion rules) our target user never asked for.

## SAP Variant Configuration (LO-VC)

- What: characteristics plus coded "object dependencies" (preconditions,
  selection conditions, procedures) driving a super BOM whose lines carry
  selection conditions.
- Borrow: the super BOM idea, a component is included when its condition
  holds, is exactly our Rule model. Keep conditions structured rows, never
  code.
- Reject: dependency code. Free-text expression conditions are what makes
  LO-VC expert-only, which validates removing our Expression mode (A1).

## Salesforce CPQ

- What: bundles with features, options, and option constraints, all built
  point-and-click by admins; guided selling via question screens.
- Borrow: point-and-click rule authoring (validates A1 and the structured
  conditions table) and help text on every non-obvious field (D1).
- Reject: the price rules engine and quote chain, out of scope.

## Tacton CPQ

- What: constraint-based solver, "no dead ends": the user picks in any order
  and the engine keeps every partial configuration valid, showing violations
  immediately instead of at the end.
- Borrow: fail early with one clear message listing every violated input
  before calculating. This validates E1 and E2 as core UX rather than stretch,
  and E3 (name the unknown variable instead of treating it as 0).
- Reject: the constraint solver itself, far beyond scope.

## Epicor CPQ (KBMax)

- What: "Snap", a drag-and-drop block editor so non-programmers read and write
  rules as plain statements, validated in real time with click-to-fix errors.
- Borrow: rules a non-engineer can read at a glance. We cannot build a block
  editor, but we can auto-generate a one-line plain-language summary per rule
  (new item D4) so the list view reads like sentences.
- Reject: the visual editor and 3D configuration.

## Infor CPQ

- What: per-product-family rulesets with wizard-style option screens.
- Borrow: one place per product family to manage everything, which validates
  the Template as hub (B1, B2, B3).
- Reject: multi-screen wizards; one dialog is enough at our scale.

## DriveWorks

- What: form-driven inputs, then one action generates models, drawings, BOMs,
  and documents, with status visible on the source record.
- Borrow: one button generates the downstream artifact and the source doc
  shows what was created (validates C1 Create BOM with stored link and status,
  and C3 dashboard link).
- Reject: CAD and document generation.

## Shopify product options

- What: the simplicity bar. An option is a label, a type, values, and a short
  help text. Nothing else.
- Borrow: aggressive minimalism in the attribute model and a short example on
  every field whose label is not self-explanatory (D1, D2).
- Reject: nothing; this is the bar to stay under.

## Ideas appended to the plan

- D4 (from Epicor Snap and Salesforce point-and-click): auto-generate a
  read-only plain-language summary on each Rule from its conditions and
  outputs, shown in the list view. Zero new inputs, pure clarity gain.
- E group note (from Tacton): upfront input validation with one complete,
  named-field error message is core configurator UX. E1-E3 are treated as in
  scope, not stretch.

Rejected overall: variants, exclusion matrices, price/quote logic, constraint
solvers, visual editors, multi-step wizards. Each adds a concept a first-time
user would have to learn.

## Sources

- [Odoo: product variants on quotations and sales orders](https://www.odoo.com/documentation/19.0/applications/sales/sales/sales_quotations/orders_and_variants.html)
- [Odoo 19 product configurator overview](https://octurasolutions.com/resources/odoo-19-product-configurator-dynamic-attributes-variants-and-custom-options)
- [Tacton: constraint-based vs rules-based configuration](https://www.tacton.com/cpq-blog/constraint-based-vs-rules-based-configuration-the-advantage-for-complex-manufacturing/)
- [Tacton CPQ configurator](https://www.tacton.com/buyer-engagement-platform/configuration/)
- [Epicor CPQ Snap rules engine](https://kbmax.com/configure-price-quote-technology/advanced-cpq-rules/)
- [Epicor CPQ guide](https://www.cpqconsultant.com/blog/epicor-cpq-guide)

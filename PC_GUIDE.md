# Product Configuration: a short guide

Define a configurable product once, then punch in dimensions and choices to get
a calculated component list and a draft BOM. One flow, mostly buttons:

Template > Configure > Product Configuration > Calculate > Create BOM > BOM

The running example below is a made-to-measure window.

## 1. Attributes (the questions you ask)

Create a Product Configuration Attribute for each input:

| Attribute | Value Type | Extras |
| --- | --- | --- |
| Width | Float | UOM: Meter |
| Height | Float | UOM: Meter |
| Material | Select | Options: Wood and Aluminium, one per line |

Each attribute gets a variable name for formulas, derived automatically from
the name (Width becomes `width`, Panel Count becomes `panel_count`). The field
is read only, so you never have to invent one.

## 2. Template (one place for the whole product)

Create a Product Configuration Template "Window":

- Configurable Item: the finished Item the BOM will be built for.
- Attributes: add Width, Height, Material. Per row you can set a default
  (e.g. Width 1200), Mandatory, and Min/Max for numbers (0 means no limit).
- Advanced (optional), collapsed by default: derived variables, e.g.
  `area = width * height`, which rules can then reuse.

Everything else starts from this form: the Connections section shows the
template's Rules and Configurations with one-click "+", and there are two
buttons: New Rule and Configure.

## 3. Rules (when X, add Y)

A Product Configuration Rule maps conditions to components:

- Condition Logic: "All conditions" (every row must match) or "Any condition"
  (one match is enough). No condition rows means the rule always applies.
- Conditions: rows like `Material == Wood` or `Width > 1000`. The in and
  not in operators compare against a comma-separated list: `Wood, Aluminium`.
- Outputs: component items with a quantity formula, e.g. `CEILING(area)` or
  plain `2`. A result of 0 or less skips the component.

Example rules for the window:

| Rule | Condition | Output |
| --- | --- | --- |
| Base Frame | always | 1 x Frame |
| Wood Frame | Material == Wood | CEILING(area) x Frame |
| Large Glass | Width > 1000 | 2 x Glass |

Each rule shows an auto-generated summary you can read at a glance, e.g.
"If Material == Wood: add CEILING(area) x Frame". Formulas support IF, AND,
OR, NOT, MIN, MAX, SUM, ABS, ROUND, ROUNDUP, ROUNDDOWN, CEILING, FLOOR, INT,
MOD, SQRT, POWER.

## 4. Configure (one dialog instead of three forms)

Click Configure on the Template. A dialog shows one field per attribute with
the right input type, options, defaults, and help text. Submitting it creates
the Product Configuration, calculates the components, and opens the result.

Example: Width 2, Height 3, Material Wood gives Frame 7 (CEILING(6) from Wood
Frame plus 1 from Base Frame, aggregated into one row).

## 5. Product Configuration and the BOM

The configuration document shows the inputs, the calculated components, and
where each component came from (Source Rule). Buttons:

- Calculate (primary while Draft): re-applies the rules to the values.
- Create BOM (primary once Calculated): builds a draft BOM for the template's
  Configurable Item from the components, links it on the form, and sets the
  status to BOM Created. The BOM also appears in Connections.

## Guardrails

Calculate fails early with one clear message instead of calculating nonsense:

- Missing mandatory values: "Fill values for the mandatory attributes: Width".
- Out-of-range or invalid choices, all collected at once: "Width must be at
  least 100; Material must be one of Wood, Aluminium".
- A broken formula names its variable: "Formula for variable area failed:
  name 'heigth' is not defined".
- Rules with invalid quantity formulas are rejected when you save the rule.

## What the refactor changed

- Removed the free-text Expression condition mode; conditions are structured
  rows only.
- Variable names are auto-derived and validated, not typed by hand.
- The Template is the hub: dashboard links, New Rule, and the Configure
  quick-entry dialog.
- One-button chain: Configure creates and calculates; Create BOM builds and
  links the BOM.
- Every non-obvious field has a description with an example; rules carry an
  auto summary.
- Upfront validation of mandatory values, min/max, select options, and
  formula errors.

Details per change are in PC_REFACTOR_PLAN.md; the competitor research that
shaped the UX is in PC_RESEARCH.md.

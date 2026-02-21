import frappe
from frappe import _
from frappe.utils import flt


def run(self):
	"""
	Dry-run critical on_submit validations during save/validate.

	Rules:
	- Skips incomplete drafts to avoid noise on fresh forms
	- Never writes to DB, never posts GL/SLE entries
	"""
	if not self.customer or not self.items:
		return

	self.check_prev_docstatus()
	self.validate_pos_paid_amount()
	_validate_asset_split(self)

	if self.update_stock:
		_validate_stock_availability(self)
		_validate_serial_and_batch_fields(self)
		_validate_packed_items(self)

	_validate_gl_preconditions(self)
	_check_credit_limit_warn(self)


def _validate_asset_split(self):
	"""
	Replicates split_asset_based_on_sale_qty() check without splitting.
	"""
	if self.is_return:
		return

	for item in self.items:
		if not item.is_fixed_asset or not item.asset:
			continue

		actual_qty = frappe.db.get_value("Asset", item.asset, "asset_quantity")

		if actual_qty is None:
			frappe.throw(
				_("Row #{0}: Asset {1} does not exist or has been deleted.").format(
					item.idx, frappe.bold(item.asset)
				),
				title=_("Pre-Submission Validation"),
			)

		if flt(item.qty) > flt(actual_qty):
			frappe.throw(
				_(
					"Row #{0}: Sell quantity ({1}) cannot exceed the asset quantity. "
					"Asset {2} has only {3} item(s) available."
				).format(item.idx, item.qty, frappe.bold(item.asset), actual_qty),
				title=_("Pre-Submission Validation"),
			)


def _validate_stock_availability(self):
	"""
	Checks available stock without creating Stock Ledger Entries.
	"""
	from erpnext.stock.utils import get_stock_balance

	allow_negative_stock = frappe.get_cached_value("Stock Settings", None, "allow_negative_stock")
	if allow_negative_stock:
		return

	for item in self.items:
		if not item.item_code or not item.qty:
			continue

		is_stock_item = frappe.get_cached_value("Item", item.item_code, "is_stock_item")
		if not is_stock_item:
			continue

		allow_negative_stock = frappe.get_cached_value("Item", item.item_code, "allow_negative_stock")
		if allow_negative_stock:
			continue

		# Items with bundles are validated by the bundle mechanism, skip here
		if item.get("serial_and_batch_bundle"):
			continue

		if not item.warehouse:
			continue

		available_qty = get_stock_balance(
			item.item_code,
			item.warehouse,
			self.posting_date,
			self.posting_time or "00:00:00",
		)

		if flt(available_qty) < flt(item.stock_qty):
			frappe.throw(
				_(
					"Row #{0}: Insufficient stock for Item {1} in Warehouse {2}. "
					"Available: {3} {4}, Required: {5} {4}."
				).format(
					item.idx,
					frappe.bold(item.item_code),
					frappe.bold(item.warehouse),
					available_qty,
					item.stock_uom,
					item.stock_qty,
				),
				title=_("Pre-Submission Validation"),
			)


def _validate_serial_and_batch_fields(self):
	"""
	Validates serial/batch requirements without creating bundles.

	Handles both legacy fields (serial_no, batch_no) and the modern
	serial_and_batch_bundle flow. A missing bundle or legacy field
	is only an error if the item actually requires one.
	"""
	# safe to call — it's a pure validation with no side effects
	self.validate_standalone_serial_nos_customer()

	for item in self.items:
		if not item.item_code:
			continue

		has_serial = frappe.get_cached_value("Item", item.item_code, "has_serial_no")
		has_batch = frappe.get_cached_value("Item", item.item_code, "has_batch_no")

		if not has_serial and not has_batch:
			continue

		# Modern bundle flow takes priority — if bundle exists, we're good
		if item.get("serial_and_batch_bundle"):
			continue

		# Fall back to legacy field checks
		if has_serial and not item.get("serial_no"):
			frappe.throw(
				_(
					"Row #{0}: Serial No is required for Item {1}. "
					"Please set a Serial No or Serial and Batch Bundle."
				).format(item.idx, frappe.bold(item.item_code)),
				title=_("Pre-Submission Validation"),
			)

		if has_batch and not item.get("batch_no"):
			frappe.throw(
				_(
					"Row #{0}: Batch No is required for Item {1}. "
					"Please set a Batch No or Serial and Batch Bundle."
				).format(item.idx, frappe.bold(item.item_code)),
				title=_("Pre-Submission Validation"),
			)


def _validate_packed_items(self):
	"""
	Validates packed item integrity without triggering bundle creation.
	Only runs if packed_items is already populated (update_packing_list
	runs in validate() before this, so it should be).
	"""
	for packed in self.get("packed_items") or []:
		if not packed.item_code:
			continue

		if flt(packed.qty) <= 0:
			frappe.throw(
				_("Row #{0} (Packed Item): Quantity must be greater than zero for Item {1}.").format(
					packed.idx, frappe.bold(packed.item_code)
				),
				title=_("Pre-Submission Validation"),
			)

		if not packed.warehouse:
			frappe.throw(
				_("Row #{0} (Packed Item): Warehouse is required for Item {1}.").format(
					packed.idx, frappe.bold(packed.item_code)
				),
				title=_("Pre-Submission Validation"),
			)


def _validate_gl_preconditions(self):
	"""
	Builds the full GL entry map without posting anything.
	"""
	if not self.company or not self.debit_to:
		return

	try:
		self.get_gl_entries()
	except frappe.ValidationError as e:
		frappe.msgprint(
			msg=_(
				"A GL account issue was detected that will block submission: {0}"
				"<br><br>Please fix this before submitting."
			).format(str(e)),
			title=_("Pre-Submit Warning: GL Accounts"),
			indicator="orange",
		)
	except Exception as e:
		# Unexpected errors — surface as warning, don't block save
		frappe.msgprint(
			msg=_("An unexpected error occurred during GL validation: {0}").format(str(e)),
			title=_("Pre-Submit Warning"),
			indicator="orange",
		)


def _check_credit_limit_warn(self):
	"""
	Warns if the customer's credit limit would be breached on submit.

	Not a hard block because:
	- Credit limit enforcement can be bypassed by authorized users
	- The actual block at submit time is intentional (requires approver)
	- We don't want to prevent saving a draft when the user may still
	  be adjusting quantities or getting approval in parallel
	"""
	if self.is_return:
		return

	try:
		self.check_credit_limit()
	except frappe.ValidationError as e:
		frappe.msgprint(
			msg=_(
				"Credit limit warning — this customer's credit limit would be exceeded "
				"and submission may be blocked: {0}"
			).format(str(e)),
			title=_("Pre-Submit Warning: Credit Limit"),
			indicator="orange",
		)

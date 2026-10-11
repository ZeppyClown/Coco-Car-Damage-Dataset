# Workshop invoicing and GST

F13 adds standalone SGD billing to `/workshop`. It uses reviewed completed-work records and deterministic decimal arithmetic. It does not need AI or the old financial software. The original record CSV remains `workshop-demo-v1`, with unchanged columns and bytes; invoices are separate documents.

On 12 October 2026 the user confirmed **GST-registered; quoted prices include GST**. The UI defaults to inclusive pricing. This is a company setting supplied by the user; its registration number and exact billing identity have not been independently verified or configured. Real issuance defaults off. Fictional records always produce prominently labelled **DEMO** invoices.

## Create an invoice

1. Create or reopen a job. Enter the actual line amounts, select **Completed work**, resolve descriptions/prices/currency, save and confirm. A quote or approved scope cannot be invoiced. A missing amount is unknown, not zero. The currency must be SGD.
2. Open its reviewed history and choose **Prepare invoice** on the current version. A newer saved draft must be reviewed first. Cancelled rows remain in the source record but are excluded from billing.
3. For a fictional demonstration, enter an explicitly fictional supplier name, address and GST number, plus fictional customer billing name/address. The example number is not a valid company registration. For real records the supplier comes from the server's configured profile and must match it on issuance.
4. Check whether the captured amounts include GST. Default: **Include GST**. Every item amount is an already captured line total; there is no unit-price/quantity multiplication. Enter an explicit invoice discount in the same pricing basis, or keep `0.00`. The system does not guess a discount from handwritten notes or written adjustments.
5. Choose **Preview invoice totals**. This creates no invoice or payment record. Check the subtotal, discount, net amount, GST and payable amount. Changes invalidate the preview and issuance acknowledgement. Source written totals remain observations; they are not automatically substituted for calculated totals.
6. Acknowledge the billing details and choose **Issue invoice**. It requires today's Singapore date and the current saved/reviewed completed-work version. Fictional output is labelled DEMO and never suitable for payment or tax claims. A real record is blocked while real issuance is disabled or company configuration is missing.
7. Open **Open issued invoice / Print / Save as PDF**. Browser Print can save a PDF; there is no PDF-generation dependency or external service. Reopen the job later to retrieve the same issued document.

Issuance records the authenticated account and server UTC time, a unique identifying number, the source job/revision, billing inputs, calculated amounts and exact printable HTML. An issued invoice is not a payment receipt. No customer email, payment request or IRAS submission is sent.

## Calculation contract

Current standard Singapore GST is 9%, effective from 1 January 2024. This module supports current local standard-rated repair supplies, or ordinary invoices for a supplier declared not GST-registered. It does not support historical transition cases, exports, exempt/mixed supplies or foreign-currency conversion. [IRAS current GST rate](https://www.iras.gov.sg/taxes/goods-services-tax-(gst)/charging-gst-(output-tax)/when-to-charge-goods-and-services-tax-(gst)/prevailing-rate-of-9), [IRAS when to charge GST](https://www.iras.gov.sg/taxes/goods-services-tax-(gst)/charging-gst-(output-tax)/when-to-charge-goods-and-services-tax-(gst)).

The application consistently uses **invoice-subtotal rounding**, one of IRAS's accepted methods. It rounds the calculated GST once to the nearest cent, with decimal half-up rounding. No cash rounding is applied. [IRAS calculation and rounding guidance](https://www.iras.gov.sg/taxes/goods-services-tax-(gst)/basics-of-gst/invoicing-price-display-and-record-keeping/invoicing-customers).

Let `B = sum(active confirmed line amounts) - explicit discount`:

| Supplier / pricing | GST | Net | Payable |
|---|---|---|---|
| Registered, inclusive | round(`B × 9 / 109`, 2 decimals) | `B − GST` | `B` |
| Registered, exclusive | round(`B × 0.09`, 2 decimals) | `B` | `B + GST` |
| Not registered | `0.00`, labelled not applicable | `B` | `B` |

Examples checked by tests:

| Inputs | Net | GST | Payable |
|---|---:|---:|---:|
| SGD 109 inclusive | 100.00 | 9.00 | 109.00 |
| SGD 100 exclusive | 100.00 | 9.00 | 109.00 |
| SGD 25.10 inclusive | 23.03 | 2.07 | 25.10 |
| Three SGD 1.28 lines exclusive | 3.84 | 0.35 | 4.19 |
| SGD 109 inclusive, discount 10.90 inclusive | 90.00 | 8.10 | 98.10 |

Money requires decimal strings, whole integers or Decimal values; binary floats, booleans, nonfinite values and more than two fractional places are rejected. Discount cannot exceed subtotal. Subtotal/payable must stay below SGD 10 billion, the existing money contract limit. Unknown registration is not treated as non-registration or a zero-rated supply.

## Identity, correction and recovery

- One invoice per job UUID. A PostgreSQL job lock serialises issuance with draft saves/reviews. Concurrent identical requests reuse one invoice; different billing inputs conflict with409. Repeating the exact request returns its original number/time/account/HTML.
- Numbers use `DEMO-INV-` or `INV-` followed by the invoice UUID in uppercase hexadecimal. The identifier is unique; no company-specific sequential numbering scheme is assumed.
- PostgreSQL rejects updates/deletes to issued invoice rows. Editing a job leaves the original invoice intact and cannot issue a second bill for that job. **Credit notes/cancellation/replacement billing are not implemented.** Add a linked credit-note workflow before handling those cases; never edit the original financial evidence or create a duplicate job to bypass the guard.
- The full snapshot and HTML are stored transactionally in `workshop_invoices`. A failed commit leaves no partial invoice. Issued print responses verify the stored HTML SHA-256 and fail503 if it is corrupt. They do not regenerate historical bytes after code/profile changes.
- Printable names/addresses/descriptions are HTML-escaped. The print route has no scripts, uses restrictive CSP/no-store/nosniff, and inherits existing account/origin checks. No new access roles are introduced.
- Additive migration **`20261012_invoices`** follows `20261011_auth`. Existing reviewed records, source references and demo exports are preserved. Invoice HTML lives in the database and is recovered by its dump; source images/record CSVs still require the separate private file backup. The actual disposable recovery test now restores invoice identity, amounts, HTML and its mutation guard as well as earlier records/files. This remains a quiescent local drill, not an automated production backup.

## Billing configuration

Leave these defaults until company details are established:

```dotenv
WORKSHOP_REAL_INVOICES_ENABLED=false
# WORKSHOP_BILLING_SUPPLIER is unset
```

`WORKSHOP_BILLING_SUPPLIER` is a validated JSON object in the ignored private environment file:

```dotenv
# Fictional example only; do not use as a real company profile.
WORKSHOP_BILLING_SUPPLIER='{"name":"Fictional Workshop","address":"1 Fictional Street (DEMO)","gst_status":"registered","gst_registration_number":"FICTIONAL-NOT-A-REGISTRATION"}'
```

A registered profile requires a nonblank GST number. A `not_registered` profile must set that number to null. Presence/shape are checked; no external registration lookup is performed. With the actual supplier verified and the operating scope agreed, `WORKSHOP_REAL_INVOICES_ENABLED=true` permits issuance for private-source jobs using that exact profile. Restart the local process after configuration changes. Changing the profile never rewrites old invoices. The real issue/retry endpoint still requires enabled billing and a matching current profile; saved invoices remain retrievable through the read/print routes. Keep completed answers/profile/customer records private; leave real issuance off in the normal fictional demo.

The full tax-invoice layout includes supplier and customer names/addresses, supplier GST number, invoice date/identifier, descriptions, tax rate and net/GST/payable totals. Full details are required even for small invoices; the app does not switch to a simplified layout at SGD 1,000. These layout checks do not certify legal compliance for every transaction. [IRAS invoice requirements](https://www.iras.gov.sg/taxes/goods-services-tax-(gst)/basics-of-gst/invoicing-price-display-and-record-keeping/invoicing-customers).

InvoiceNow is a separate submission requirement with phased applicability. A printable PDF does not provide it. New voluntary registrations from 1 April 2026 are included; existing businesses' dates depend on the applicable phase/IRAS notification. Obtain Yap Motor's actual date before selecting live billing operations. No Peppol/InvoiceNow connection or submission is implemented. [IRAS GST InvoiceNow requirement](https://www.iras.gov.sg/taxes/goods-services-tax-(gst)/gst-invoicenow-requirement).

## Questions to take to the company — keep filled answers private

| Input | Current answer | Company answer / evidence to return privately |
|---|---|---|
| GST registered? | User: yes, 12 October 2026 | Confirm actual registration details/status |
| Are quoted prices inclusive? | User: yes, 12 October 2026 | Confirm exceptions, if any |
| Exact supplier billing name | Pending | … |
| Business address on invoices | Pending | … |
| GST registration number | Pending | … |
| IRAS InvoiceNow implementation date/notification | Pending | … |
| Typical invoice numbering and discount/correction rules | Prototype UUID numbering; explicit discount; no credit notes | … |
| Who invoices, when work becomes billable, and permitted company operating scope | Pending actual operator/operation; prototype requires reviewed completed work | … |

## Interface and verification

All routes are under authenticated `/api/v1/workshop`:

| Route | Result |
|---|---|
| `GET /billing-settings` | Real issuance flag and configured supplier, or null |
| `POST /revisions/{id}/invoice-preview` | Validated `InvoiceRequest` → totals; no invoice write |
| `POST /revisions/{id}/invoice` | `{invoice: InvoiceRequest, acknowledged: true}` → immutable issue/reuse |
| `GET /jobs/{id}/invoice` | This job's invoice, or404 |
| `GET /invoices/{id}` | Stored invoice metadata/snapshot |
| `GET /invoices/{id}/print` | Exact checksum-verified printable HTML |

Run the money/API cases with `tests/unit/test_workshop_invoice.py`, the PostgreSQL migration/concurrency/recovery cases with `tests/integration/test_workshop_postgres.py`, and the expanded `tests/browser/workshop.cjs` harness using the operating guide's local setup. See [actual results and fictional invoice artifacts](WORKSHOP_VERIFICATION_REPORT.md) and the [master ledger](WORKSHOP_MASTER_PLAN.md) for the latest executed counts and limitations.

This feature does not implement payments, receivables, purchase/input-tax records, GST returns, a general ledger, credit notes or InvoiceNow submission. It adds invoicing/GST calculation and immutable output to the selected record workflow, not an entire accounting package.

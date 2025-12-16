"""Constants and type definitions for the Addepy SDK."""
from typing import Literal, Set

# Polling defaults
DEFAULT_INITIAL_WAIT: float = 30.0  # seconds
DEFAULT_MAX_WAIT: float = 300.0  # 5 minutes
DEFAULT_BACKOFF_FACTOR: float = 1.5
DEFAULT_TIMEOUT: float = 1200.0  # 20 minutes

# Pagination defaults
DEFAULT_PAGE_LIMIT: int = 500
MAX_PAGE_LIMIT: int = 2000

# Import job completed statuses (stops polling)
IMPORT_COMPLETED_STATUSES: Set[str] = {
    "ERRORS_READY_FOR_REVIEW",
    "WARNINGS_READY_FOR_REVIEW",
    "ERRORS_AND_WARNINGS_READY_FOR_REVIEW",
    "DRY_RUN_SUCCESSFUL",
    "IMPORT_SUCCESSFUL",
    "VALIDATION_FAILED",
    "IMPORT_FAILED",
}

# Import statuses where results are available
IMPORT_RESULT_READY_STATUSES: Set[str] = {
    "ERRORS_READY_FOR_REVIEW",
    "WARNINGS_READY_FOR_REVIEW",
    "ERRORS_AND_WARNINGS_READY_FOR_REVIEW",
    "DRY_RUN_SUCCESSFUL",
    "IMPORT_SUCCESSFUL",
}

# Valid import types for POST requests
VALID_POST_IMPORT_TYPES: Set[str] = {
    "ATTRIBUTES",
    "BENCHMARKS",
    "BENCHMARK_ASSOCIATIONS",
    "CONTACTS",
    "COST_BASIS",
    "ESTIMATED_RETURNS",
    "GROUPS",
    "HISTORICAL_PRICES",
    "MANAGE_INVESTMENTS",
    "MANAGE_OWNERSHIP",
    "MANUAL_ADJUSTMENTS",
    "CONSTITUENTS",
    "POSITION_VALUATIONS",
    "SUMMARY_DATA",
    "TARGET_ALLOCATIONS",
    "TOTAL_OUTSTANDING_SHARES",
    "TRANSACTIONS",
    "DELETE_TRANSACTIONS",
    "VALUES_AND_FLOWS",
}

# Valid import types for DELETE requests
VALID_DELETE_IMPORT_TYPES: Set[str] = {"DELETE_TRANSACTIONS"}

# All valid import types
ALL_VALID_IMPORT_TYPES: Set[str] = VALID_POST_IMPORT_TYPES | VALID_DELETE_IMPORT_TYPES

# Type literal for static type checking
AddeparImportType = Literal[
    "ATTRIBUTES",
    "BENCHMARKS",
    "BENCHMARK_ASSOCIATIONS",
    "CONTACTS",
    "COST_BASIS",
    "ESTIMATED_RETURNS",
    "GROUPS",
    "HISTORICAL_PRICES",
    "MANAGE_INVESTMENTS",
    "MANAGE_OWNERSHIP",
    "MANUAL_ADJUSTMENTS",
    "CONSTITUENTS",
    "POSITION_VALUATIONS",
    "SUMMARY_DATA",
    "TARGET_ALLOCATIONS",
    "TOTAL_OUTSTANDING_SHARES",
    "TRANSACTIONS",
    "DELETE_TRANSACTIONS",
    "VALUES_AND_FLOWS",
]

# Default content type for Addepar API (JSON:API)
DEFAULT_CONTENT_TYPE = "application/vnd.api+json"

# =============================================================================
# Type Literals for IDE autocomplete support
# =============================================================================

# Portfolio type for queries
PortfolioType = Literal[
    "ENTITY",
    "ENTITY_FUNDS",
    "GROUP",
    "GROUP_FUNDS",
    "FIRM",
    "FIRM_ACCOUNTS",
    "FIRM_CLIENTS",
    "FIRM_HOUSEHOLDS",
    "FIRM_UNVERIFIED_ACCOUNTS",
]

# Output format type (includes JSON)
OutputType = Literal["JSON", "CSV", "TSV", "XLSX"]

# Transaction output format (no JSON option)
TransactionOutputType = Literal["CSV", "TSV", "XLSX"]

# Benchmark types
BenchmarkType = Literal[
    "blended",
    "imported",
    "fixed_return",
    "portfolio_benchmark",
    "security_benchmark",
]

# Benchmark matching type
MatchingType = Literal["PATH", "PDN"]

# Snapshot type
SnapshotType = Literal["snapshot", "valuation"]

# User login method
LoginMethod = Literal["email_password", "saml"]

# Client portal publishing scope
PortalPublishing = Literal["do_not_publish", "use_contact_preference", "publish"]

# Contact notification scope
ContactNotification = Literal["do_not_notify", "use_contact_preference", "notify"]

# Audit object types
AuditObjectType = Literal["login_attempt", "attribute", "transaction", "permission"]

# Audit user types
AuditUserType = Literal["firmusers", "addeparusers", "anyone", "custom"]

# Audit actions
AuditAction = Literal["Add", "Modify", "Remove"]

# Underlying type for forward/futures contracts
UnderlyingType = Literal[
    "INTEREST_RATE",
    "CURRENCY",
    "COMMODITY",
    "SECURITY",
    "INDEX",
]

# Attribute usage filter
AttributeUsage = Literal[
    "columns",
    "groupings",
    "filters",
    "position_custom_attributes",
    "entity_custom_attributes",
    "entity_attributes",
]

# Attribute output type filter
AttributeOutputType = Literal[
    "Word",
    "Boolean",
    "Percent",
    "Date",
    "Currency",
    "List",
    "Number",
]

# Transaction type (all 76 supported types)
TransactionType = Literal[
    "account_fee",
    "account_fee_advisor",
    "account_fee_bank",
    "account_fee_custodian",
    "account_fee_management",
    "account_fee_professional",
    "account_fee_reimbursement",
    "account_fee_reimbursement_advisor",
    "account_fee_reimbursement_bank",
    "account_fee_reimbursement_custodian",
    "account_fee_reimbursement_management",
    "account_fee_reimbursement_professional",
    "adjustment",
    "buy",
    "capital_call",
    "cash_dividend",
    "cash_in_lieu",
    "change_in_unrealized_gain",
    "commitment",
    "commitment_reduction",
    "contribution",
    "conversion",
    "corporate_action",
    "cost_adjustment",
    "cover_short",
    "deposit",
    "distribution",
    "exercise_call",
    "exercise_put",
    "expense",
    "expense_allocated",
    "expiration",
    "fee",
    "fee_reimbursement",
    "fund_redemption",
    "gain",
    "generic_flow",
    "inception",
    "income",
    "income_allocated",
    "interest_expense",
    "interest_income",
    "journal_in",
    "journal_out",
    "loan_issued",
    "loan_taken",
    "lookthrough_adjustment",
    "mark_to_market",
    "payment_made_in_lieu_of_dividend",
    "payment_received_in_lieu_of_dividend",
    "proceeds_adjustment",
    "recalled_contribution",
    "redemption",
    "reinvestment",
    "sell",
    "sell_short",
    "snapshot",
    "spinoff",
    "stock_dividend",
    "stock_reverse_split",
    "stock_split",
    "tax",
    "tax_refund",
    "tax_withholding",
    "tax_withholding_refund",
    "transfer",
    "transfer_in",
    "transfer_out",
    "unfunded_adjustment",
    "valuation",
    "withdrawal",
    "write_option",
    "written_exercise_call",
    "written_exercise_put",
    "written_expiration",
]

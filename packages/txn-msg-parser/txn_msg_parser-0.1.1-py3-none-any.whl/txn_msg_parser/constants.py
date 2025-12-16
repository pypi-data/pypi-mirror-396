DEFAULT_MODEL = "deepseek-r1:8b"
DEFAULT_HOST = "http://localhost:11434"

OUTPUT_FORMAT = {
    "account": "string",
    "amount": "int",
    "txn_type": "debit|credit",
    "payee": "string|null",
    "payer": "string|null",
    "category": "string|null",
}

DEFAULT_CATEGORIES = ["Salary", "EMI", "Food", "Travel", "Bills", "Shopping"]

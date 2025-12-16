from typing import List

from txn_msg_parser.ai import AIFactory
from txn_msg_parser.constants import DEFAULT_CATEGORIES, DEFAULT_HOST, DEFAULT_MODEL
from txn_msg_parser.prompt import PromptGenFactory


class TxnText:
    sender: str | None
    text: str
    date: str | None
    type: str | None
    id: str | None


class Txn:
    account: str
    amount: int
    txn_type: str
    payee: str | None
    payer: str | None
    category: str
    full_text: str
    date: str | None
    id: str | None

    def __init__(self, dictionary):
        self.account = dictionary.get("account")
        self.amount = int(dictionary.get("amount"))
        self.txn_type = dictionary.get("txn_type")
        self.payee = dictionary.get("payee", "")
        self.payer = dictionary.get("payer", "")
        self.category = dictionary.get("category", "")


class TextParser:
    def __init__(self, accounts: List[str], categories: List[str] = DEFAULT_CATEGORIES, model=DEFAULT_MODEL, ollama_host=DEFAULT_HOST):
        self.prompt_gen = PromptGenFactory()
        self.ai = AIFactory(model=model, host=ollama_host)
        self.categories = categories
        self.accounts = accounts

    def _convert_txn_text_to_txn(self, txn_text: dict) -> dict:
        prompt = self.prompt_gen.get_sms_txn_parsing_prompt(
            txn_text, self.categories, self.accounts
        )
        return self.ai.ask(prompt)

    def _validate_text(self, text: TxnText):
        if not text.text:
            raise Exception("Text missing")

    def parse_text(self, text: TxnText) -> Txn:
        self._validate_text(text)
        txn_dict = self._convert_txn_text_to_txn(text.__dict__)
        txn = Txn(txn_dict)
        txn.full_text = text.text
        txn.date = text.date
        txn.id = text.id
        return txn

    def parse_texts(self, texts: List[TxnText]) -> List[Txn]:
        txns = [self.parse_text(text) for text in texts]
        return txns

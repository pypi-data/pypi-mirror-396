import json
from typing import List
from txn_msg_parser.constants import OUTPUT_FORMAT
from txn_msg_parser.training_data.sms_training import sms_training_data


class PromptGenFactory:
    def get_sms_txn_parsing_prompt(
        self, input_dict: dict, categories: List[str], accounts: List[str]
    ) -> str:
        sms_training_data_json = json.dumps(sms_training_data)
        input_json = json.dumps(input_dict)
        output_format_json = json.dumps(OUTPUT_FORMAT)
        prompt = f"""
Refer to these examples and learn how to convert a transaction SMS object to transaction JSON object.

<context>
1. Account -> From "sender" key. Valid values: {accounts}
2. Amount -> From "text" key. Keep it as int. Multiply the value by 100. Examples: 100.5 -> 10050, 145 -> 14500, 42523.47 -> 4252347
3. Transaction type -> From "text" key. Value values: "credit", "debit"
4. Payee -> From "text" key, String about who is receiving payment. Null for credit type
5. Payer -> From "text" key, String about who sent the payment. Null for debit type
6. Category -> From "text" key, One word category for txn. Valid categories: {categories}
</context>

<examples>
{sms_training_data_json}
</examples>

SMS input JSON to convert:
<input>
{input_json}
</input>

Reply only in JSON.
Output JSON format:
<output-format>
{output_format_json}
</output-format>

"""
        return prompt

from datetime import date
from typing import Dict, List

from dict2xml import dict2xml as dict_to_xml  # type: ignore[import-untyped]
from xmltodict import parse as xml_to_dict

from prisme.request import PrismeRequest, PrismeResponse
from prisme.util import parse_isodate


class PrismeSELAccountRequest(PrismeRequest):
    def __init__(
        self,
        customer_id_number: int | str,
        from_date: date,
        to_date: date,
        open_closed: int = 2,
    ):
        super().__init__()
        self.customer_id_number = str(customer_id_number)
        self.from_date = from_date
        self.to_date = to_date
        self.open_closed = open_closed

    wrap = "CustTable"

    open_closed_map = {0: "Åbne", 1: "Lukkede", 2: "Åbne og Lukkede"}

    @classmethod
    def method(cls) -> str:
        return "getAccountStatementSEL"

    @property
    def xml(self) -> str:
        return dict_to_xml(
            {
                "CustIdentificationNumber": self.prepare(self.customer_id_number),
                "FromDate": self.prepare(self.from_date),
                "ToDate": self.prepare(self.to_date),
                "CustInterestCalc": self.open_closed_map[self.open_closed],
            },
            wrap=self.wrap,
        )

    @classmethod
    def response_class(cls) -> type[PrismeResponse]:
        return PrismeSELAccountResponse


class PrismeSELAccountResponseTransaction(object):
    def __init__(self, data):
        self.data = data
        self.account_number = data["AccountNum"]
        self.transaction_date = parse_isodate(data["TransDate"])
        self.accounting_date = parse_isodate(data["AccountingDate"])
        self.debitor_group_id = data["CustGroup"]
        self.debitor_group_name = data["CustGroupName"]
        self.voucher = data["Voucher"]
        self.text = data["Txt"]
        self.payment_code = data["CustPaymCode"]
        self.payment_code_name = data["CustPaymDescription"]
        amount = data["AmountCur"]
        try:
            self.amount = float(amount)
        except (ValueError, TypeError):
            self.amount = 0
        self.remaining_amount = data["RemainAmountCur"]
        self.due_date = data["DueDate"]
        self.closed_date = data["Closed"]
        self.last_settlement_voucher = data["LastSettleVoucher"]
        self.collection_letter_date = data["CollectionLetterDate"]
        self.collection_letter_code = data["CollectionLetterCode"]
        self.claim_type_code = data["ClaimTypeCode"]
        self.invoice_number = data["Invoice"]
        self.transaction_type = data["TransType"]
        self.rate_number = data.get("RateNmb")
        self.extern_invoice_number = data.get("ExternalInvoiceNumber")


class PrismeSELAccountResponse(PrismeResponse):
    itemclass = PrismeSELAccountResponseTransaction

    def __init__(self, request: PrismeSELAccountRequest, xml: str):
        self.request = request
        self.xml: str = xml
        self.transactions: List[PrismeSELAccountResponseTransaction] = []
        if xml is not None:
            self.data: Dict = xml_to_dict(xml)
            transactions = self.data["CustTable"]["CustTrans"]
            if type(transactions) is not list:
                transactions = [transactions]
            self.transactions = [self.itemclass(x) for x in transactions]

    def __iter__(self):
        yield from self.transactions

    def __len__(self) -> int:
        return len(self.transactions)

    def __getitem__(self, item) -> PrismeSELAccountResponseTransaction:
        return self.transactions[item]

import logging
from datetime import date
from typing import Any, List

from requests import Session
from zeep import Client
from zeep.transports import Transport

from prisme.account import PrismeSELAccountRequest, PrismeSELAccountResponse
from prisme.exceptions import PrismeException
from prisme.request import PrismeRequestType, PrismeResponseType

logger = logging.getLogger(__name__)


class Prisme(object):

    def __init__(self, wsdl_file: str, auth: dict, proxy: dict | None = None):
        self._client: Client | None = None
        self.wsdl_file: str = wsdl_file
        self.auth: dict = auth
        self.proxy: dict | None = proxy

    @property
    def client(self) -> Client:
        if self._client is None:
            session = Session()
            if self.proxy:
                socks = self.proxy.get("socks")
                if socks:
                    proxy = f"socks5://{socks}"
                    session.proxies = {"http": proxy, "https": proxy}

            if self.auth:
                if "basic" in self.auth:
                    basic_settings = self.auth["basic"]
                    session.auth = (
                        f'{basic_settings["username"]}@{basic_settings["domain"]}',
                        basic_settings["password"],
                    )
            try:
                self._client = Client(
                    wsdl=self.wsdl_file,
                    transport=Transport(
                        session=session, timeout=3600, operation_timeout=3600
                    ),
                )
                self._client.set_ns_prefix(
                    "tns",
                    "http://schemas.datacontract.org/2004/07/Dynamics.Ax.Application",
                )
            except Exception as e:
                logger.error("Failed connecting to prisme: %s" % str(e))
                raise e
        assert self._client is not None
        return self._client

    def create_request_header(
        self, method: str, area: str = "SULLISSIVIK", client_version: int = 1
    ):
        request_header_class = self.client.get_type("tns:GWSRequestHeaderDCFUJ")
        return request_header_class(
            clientVersion=client_version, area=area, method=method
        )

    def create_request_body(self, xml: str | List[str]):
        if type(xml) is not list:
            xml = [str(xml)]
        item_class = self.client.get_type("tns:GWSRequestXMLDCFUJ")
        container_class = self.client.get_type("tns:ArrayOfGWSRequestXMLDCFUJ")
        return container_class(list([item_class(xml=x) for x in xml]))

    def get_server_version(self):
        response = self.client.service.getServerVersion(
            self.create_request_header("getServerVersion")
        )
        return {
            "version": response.serverVersion,
            "description": response.serverVersionDescription,
        }

    def process_service(
        self, request_object: PrismeRequestType, debug_context: Any = None
    ) -> List[PrismeResponseType]:
        if debug_context is not None:
            log_context = str(debug_context) + " "
        else:
            log_context = ""
        try:
            soap_request_class = self.client.get_type("tns:GWSRequestDCFUJ")
            response_class: type[PrismeResponseType] = request_object.response_class()
            request = soap_request_class(
                requestHeader=self.create_request_header(request_object.method()),
                xmlCollection=self.create_request_body(request_object.xml),
            )
            logger.debug(
                "%sSending to %s:\n%s"
                % (log_context, request_object.method(), request_object.xml)
            )
            # soap_response is of type GWSReplyDCFUJ,
            # a dynamically specified class from the WDSL
            soap_response = self.client.service.processService(request)

            # soap_response.status is of type GWSReplyStatusDCFUJ
            if soap_response.status.replyCode != 0:
                raise PrismeException(
                    soap_response.status.replyCode,
                    soap_response.status.replyText,
                    debug_context,
                )

            outputs: List[PrismeResponseType] = []
            # soap_response_item is of type GWSReplyInstanceDCFUJ
            for (
                soap_response_item
            ) in soap_response.instanceCollection.GWSReplyInstanceDCFUJ:
                if soap_response_item.replyCode == 0:
                    logger.debug(
                        "%sReceiving from %s:\n%s"
                        % (log_context, request_object.method(), soap_response_item.xml)
                    )
                    outputs.append(
                        response_class(request_object, soap_response_item.xml)
                    )
                else:
                    raise PrismeException(
                        soap_response_item.replyCode,
                        soap_response_item.replyText,
                        debug_context,
                    )
            return outputs
        except Exception as e:
            logger.error(
                "%sError in process_service for %s: %s"
                % (log_context, request_object.method(), str(e))
            )
            raise e

    def get_account_data(
        self,
        cvr: str | int,
        date_from: date,
        date_to: date,
        debug_context: Any = None,
    ) -> List[PrismeSELAccountResponse]:
        if debug_context is None:
            debug_context = {"method": "get_account_data", "cvr": cvr}
        return self.process_service(
            PrismeSELAccountRequest(cvr, date_from, date_to), debug_context
        )

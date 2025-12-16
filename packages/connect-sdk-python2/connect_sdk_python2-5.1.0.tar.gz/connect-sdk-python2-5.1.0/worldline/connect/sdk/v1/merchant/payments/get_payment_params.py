# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.communication.param_request import ParamRequest
from worldline.connect.sdk.communication.request_param import RequestParam


class GetPaymentParams(ParamRequest):
    """
    Query parameters for Get payment

    See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/payments/get.html
    """

    __return_operations = None

    @property
    def return_operations(self):
        """
        | If set to true, in the response of this call you will get an array called operations, that will include objects for captures and refunds associated with the given paymentId.

        Type: bool
        """
        return self.__return_operations

    @return_operations.setter
    def return_operations(self, value):
        self.__return_operations = value

    def to_request_parameters(self):
        """
        :return: list[RequestParam]
        """
        result = []
        if self.return_operations is not None:
            result.append(RequestParam("returnOperations", str(self.return_operations)))
        return result

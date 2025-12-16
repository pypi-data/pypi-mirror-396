# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.domain.data_object import DataObject


class RefundReferences(DataObject):

    __descriptor = None
    __merchant_reference = None

    @property
    def descriptor(self):
        """
        | Descriptive text that is used towards customer during refund. The maximum allowed length varies per payment product:   
        
        * Wero - 50 characters

        Type: str
        """
        return self.__descriptor

    @descriptor.setter
    def descriptor(self, value):
        self.__descriptor = value

    @property
    def merchant_reference(self):
        """
        | Note that the maximum length of this field for transactions processed on the GlobalCollect platform is 30. Your unique reference of the transaction that is also returned in our report files. This is almost always used for your reconciliation of our report files.

        Type: str
        """
        return self.__merchant_reference

    @merchant_reference.setter
    def merchant_reference(self, value):
        self.__merchant_reference = value

    def to_dictionary(self):
        dictionary = super(RefundReferences, self).to_dictionary()
        if self.descriptor is not None:
            dictionary['descriptor'] = self.descriptor
        if self.merchant_reference is not None:
            dictionary['merchantReference'] = self.merchant_reference
        return dictionary

    def from_dictionary(self, dictionary):
        super(RefundReferences, self).from_dictionary(dictionary)
        if 'descriptor' in dictionary:
            self.descriptor = dictionary['descriptor']
        if 'merchantReference' in dictionary:
            self.merchant_reference = dictionary['merchantReference']
        return self

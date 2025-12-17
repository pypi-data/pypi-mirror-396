#  Copyright (c) 2025.  Miguel Hatrick <miguel@dacosys.com> for DACOSYS (www.dacosys.com)
#
#  This script is confidential and proprietary information of DACOSYS.
#  Unauthorized use, distribution, or modification of this script is strictly prohibited.
from enum import Enum
from typing import Any, Optional, Union

from requests import Response

from api_test_toolbox.assertion.toolbox_assertion import WrongObjectEnumValueAssertionError, WrongResultLengthAssertionError, WrongStatusAssertionError
from api_test_toolbox.enum.result_status_code_operator import ResultStatusCodeOperator


class ResultToolbox:
    __response: Response
    __result_item_position: int = 0
    __response_json: list[dict] = None

    def __init__(self, response, result_item_position: int = 0):
        self.__response = response
        self.__result_item_position = result_item_position

    def validate_response(self,
                          expected_result: Union[int, list[tuple[ResultStatusCodeOperator, int]], None] = None,
                          expected_list_length: Optional[int] = None) -> None:
        """
Goto function; validates the status code and length. And get the result in one go.
        :param expected_result: Codes that we expect to receive or avoid
        :param expected_list_length: The number of items we expect to receive. If `None` is selected, this is not checked
        """
        codes_to_check: list[tuple[ResultStatusCodeOperator, int]] = []
        if expected_result is None:
            codes_to_check.append((ResultStatusCodeOperator.Equal, 200))
        elif isinstance(expected_result, int):
            codes_to_check.append((ResultStatusCodeOperator.Equal, expected_result))
        else:
            codes_to_check.extend(expected_result)

        expected_code_list = [expected_result for operator, expected_result in codes_to_check if operator.value == ResultStatusCodeOperator.Equal.value]
        avoid_code_list = [expected_result for operator, expected_result in codes_to_check if operator.value == ResultStatusCodeOperator.Not_Equal.value]

        error_message: str = ''

        if len(expected_code_list) > 0 and self.__response.status_code not in expected_code_list:
            error_message += (
                f"Response Status is NOT in the expected list.\n"
                f"Expected IN: {','.join([str(x) for x in expected_code_list])}"
            )

        if len(avoid_code_list) > 0 and self.__response.status_code in avoid_code_list:
            error_message += (
                f"Response status IN the avoid list.\n"
                f"Expected NOT IN: {expected_result}"
            )

        if len(error_message) > 0:
            error_message_general = (
                f"{error_message}\n"
                f"Received: {self.__response.status_code}\n"
            )
            self.__raise_assert_validation_error(
                assertion_type=WrongStatusAssertionError,
                title="Result Status code error",
                message=error_message_general
            )

        # Run length validation
        self.validate_result_length(expected_list_length=expected_list_length)

    def validate_result_length(self, expected_list_length: Optional[int] = None):
        if expected_list_length is None:
            return

            # Validate just in case
        assert isinstance(expected_list_length, int)
        assert expected_list_length >= 0

        content_length = self.get_response_len()

        if content_length != expected_list_length:
            error_message = (
                f"Expected result length: {expected_list_length}\n"
                f"Actual result length: ⚠ {content_length}"
            )
            self.__raise_assert_validation_error(
                assertion_type=WrongResultLengthAssertionError,
                title="Wrong json object result length.",
                message=error_message)

    def get_response_len(self) -> int:
        """
Return the JSON response list length
        :return:
        """
        return len(self.full_json_response)

    def get_response_item_dict(self, result_item_position: Optional[int] = None) -> dict:
        """
Get the dict of a single item in the response JSON
        :param result_item_position: 0 based position index of the data we want to retrieve
        :return:
        """
        if result_item_position is not None:
            self.__result_item_position = result_item_position

        if self.get_response_len() < (self.__result_item_position + 1):
            self.__raise_assert_validation_error(
                assertion_type=WrongResultLengthAssertionError,
                title='ResultToolbox index out of range',
                message=f"{self.get_response_len()} != {self.__result_item_position + 1}"
            )

        return self.full_json_response[self.__result_item_position]

    @property
    def full_json_response(self):
        """
Return the full JSON response
        :return:
        """

        if self.__response_json is None:
            self.__response_json = self.__response.json()

        return self.__response_json

    def validate_status(self, status_value: Any, status_field_name: str = None, result_item_position: Optional[int] = None) -> None:
        """
Validate if the status field has the desired value on the current position.
        :param status_value: Enum value to check against
        :param status_field_name: Field name to search for in the result dict. 'status' if None is defined
        :param result_item_position: Which item to check in the result. If `None` is provided, it will get element 0 from the list
        :return:
        """

        enum_status_class = status_value.__class__
        if not issubclass(enum_status_class, Enum):
            raise ValueError('status_value must be derived from an Enum')

        if status_field_name is None:
            status_field_name = 'status'

        current_dict = self.get_response_item_dict(result_item_position=result_item_position)

        current_status = enum_status_class(current_dict[status_field_name])

        if current_status != status_value:
            error_message = (
                f"Expected: {status_value}\n"
                f"Received: ⚠ {current_status}"
            )
            self.__raise_assert_validation_error(
                assertion_type=WrongObjectEnumValueAssertionError,
                title="Current object has a status mismatch.",
                message=error_message,
            )

    def __raise_assert_validation_error(self, assertion_type: Any, title: str, message: str):
        if not issubclass(assertion_type, AssertionError):
            raise ValueError('assertion_type must be derived from an AssertionError')

        endpoint = f"Endpoint: {self.__response.request.url}"
        content = f"Content: {self.__response.content.decode('utf-8') if self.__response.content else 'No content'}"

        raise assertion_type(f"⛔ {title} ⛔\n\n"
                              f"{message}\n"
                              f"{endpoint}\n"
                              f"{content}")

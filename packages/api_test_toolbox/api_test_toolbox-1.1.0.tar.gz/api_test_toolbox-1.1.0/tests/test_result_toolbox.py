import dill
import pytest
from data.warehouse_movement_status_enum import WarehouseMovementStatusEnum

from api_test_toolbox.assertion.toolbox_assertion import WrongObjectEnumValueAssertionError, WrongResultLengthAssertionError, WrongStatusAssertionError
from api_test_toolbox.enum.result_status_code_operator import ResultStatusCodeOperator
from api_test_toolbox.result_toolbox import ResultToolbox


def test_basic():
    from data.item_data import item1_data

    # Item 1 data is ResultStatus 200 and length 1
    response_object = dill.loads(item1_data)
    toolbox = ResultToolbox(response_object)

    # Will by default look for a 200
    toolbox.validate_response()

def test_assert_result_code_short_format():
    from data.item_data import item1_data

    # Item 1 data is ResultStatus 200 and length 1
    response_object = dill.loads(item1_data)
    toolbox = ResultToolbox(response_object)

    pytest.raises(WrongStatusAssertionError, toolbox.validate_response, expected_result=400)
    pytest.raises(WrongResultLengthAssertionError, toolbox.validate_response, expected_result=200, expected_list_length=2)

    toolbox.validate_response(expected_result=200)
    toolbox.validate_response(expected_result=200, expected_list_length=1)


def test_assert_result_code_long_format():
    from data.item_data import item1_data

    # Item 1 data is ResultStatus 200 and length 1
    response_object = dill.loads(item1_data)
    toolbox = ResultToolbox(response_object)

    pytest.raises(WrongStatusAssertionError, toolbox.validate_response, expected_result=[(ResultStatusCodeOperator.Not_Equal, 200)])

    pytest.raises(WrongStatusAssertionError, toolbox.validate_response, expected_result=[(ResultStatusCodeOperator.Equal, 400)])
    pytest.raises(WrongResultLengthAssertionError, toolbox.validate_response, expected_result=[(ResultStatusCodeOperator.Equal, 200)], expected_list_length=2)
    pytest.raises(WrongResultLengthAssertionError, toolbox.validate_response, expected_result=[(ResultStatusCodeOperator.Equal, 200), (ResultStatusCodeOperator.Equal, 400)],
                  expected_list_length=2)

    toolbox.validate_response(expected_result=[(ResultStatusCodeOperator.Equal, 200)])
    toolbox.validate_response(expected_result=[(ResultStatusCodeOperator.Equal, 200), (ResultStatusCodeOperator.Equal, 400)])

    toolbox.validate_response(expected_result=[(ResultStatusCodeOperator.Equal, 200)], expected_list_length=1)
    toolbox.validate_response(expected_result=[(ResultStatusCodeOperator.Equal, 200), (ResultStatusCodeOperator.Equal, 201)], expected_list_length=1)

    toolbox.validate_response(expected_result=[(ResultStatusCodeOperator.Equal, 200), (ResultStatusCodeOperator.Not_Equal, 201)], expected_list_length=1)


def test_check_qty_with_3_size_item_data():
    from data.item_data import item_3_data

    # Item 1 data is ResultStatus 200 and length 1
    response_object = dill.loads(item_3_data)
    toolbox = ResultToolbox(response_object)

    pytest.raises(WrongResultLengthAssertionError, toolbox.validate_response, expected_result=[(ResultStatusCodeOperator.Equal, 200)], expected_list_length=1)
    toolbox.validate_response(expected_result=[(ResultStatusCodeOperator.Equal, 200)])

    toolbox.validate_response(expected_result=[(ResultStatusCodeOperator.Equal, 200)], expected_list_length=3)
    toolbox.validate_response(expected_result=[(ResultStatusCodeOperator.Equal, 200), (ResultStatusCodeOperator.Equal, 201)], expected_list_length=3)

    toolbox.validate_response(expected_result=[(ResultStatusCodeOperator.Equal, 200), (ResultStatusCodeOperator.Not_Equal, 201)], expected_list_length=3)


def test_get_dicts_by_position():
    """
Grab the dict by position and raise exception if we go over the list length
    """
    from data.item_data import item_3_data

    # Item 1 data is ResultStatus 200 and length 1
    response_object = dill.loads(item_3_data)
    toolbox = ResultToolbox(response_object)

    for i in range(0, 3):
        toolbox.get_response_item_dict(result_item_position=i)

    pytest.raises(WrongResultLengthAssertionError, toolbox.get_response_item_dict, result_item_position=3)


def test_invalid_movement():
    from data.warehouse_movement import invalid_movement

    # ResultStatus 422 and length 1
    response_object = dill.loads(invalid_movement)
    toolbox = ResultToolbox(response_object)

    toolbox.validate_response(expected_result=[(ResultStatusCodeOperator.Equal, 422)])
    toolbox.validate_response(expected_result=[(ResultStatusCodeOperator.Equal, 422)], expected_list_length=1)

    toolbox.validate_response(expected_result=[(ResultStatusCodeOperator.Not_Equal, 200)])

    pytest.raises(WrongStatusAssertionError, toolbox.validate_response, expected_result=[(ResultStatusCodeOperator.Equal, 200)], expected_list_length=1)
    pytest.raises(WrongStatusAssertionError, toolbox.validate_response, expected_result=[(ResultStatusCodeOperator.Equal, 200)])

    pytest.raises(WrongResultLengthAssertionError, toolbox.validate_response, expected_result=[(ResultStatusCodeOperator.Equal, 422)], expected_list_length=3)


def test_valid_movement():
    from data.warehouse_movement import valid_movement

    # ResultStatus 200 and length 1
    response_object = dill.loads(valid_movement)
    toolbox = ResultToolbox(response_object)

    result_toolbox = ResultToolbox(response_object, result_item_position=0)
    result_toolbox.validate_response(expected_result=[(ResultStatusCodeOperator.Equal, 200)], expected_list_length=1)
    result_toolbox.validate_status(status_value=WarehouseMovementStatusEnum.COMPLETED)

    pytest.raises(WrongObjectEnumValueAssertionError, toolbox.validate_status, status_value=WarehouseMovementStatusEnum.CANCELED)

# Api test toolbox

## Description

The main aim of this library is to check the results for my FastAPI projects without repeating some basic logic.
Secondary AIM was to raise an exception with the request result data and status code. This avoids having to debug the test to find the real problem.

## Usage

You can check the tests for examples.

### Example test

```python
# We perform a request and get a result
response = test_client.client.post(
    "/warehouse_movement/add_multiple_internal",
    headers={"Authorization": f'Bearer {test_client.token}'},
    json={
        "warehouse_movement_ext_id": "string",
        "obs": "",
        "reference": "string",
        "priority": 'priority_3',
        "wac_content": [
            {
                "origin_warehouse_area_uuid": reception_add['content'][0]['destination_warehouse_area_uuid'],
                "origin_rack_uuid": reception_add['content'][0]['destination_rack_uuid']
            }
        ]
    }
)

# Create the result toolbox
result_toolbox = ResultToolbox(response)

# Validate the status and length
result_toolbox.validate_response(expected_result=[(ResultStatusCodeOperator.Equal, 200)], expected_list_length=1)

# Validate some enum (by default searches the 'status' but it could be any dict key
result_toolbox.validate_status(status_value=WarehouseMovementStatusEnum.COMPLETED)

# Return a value by zero index.
return result_toolbox.get_response_item_dict(0)
```

If a problem is found... The pytest log will show the following

```
E       AssertionError: ⛔ Result Status code error ⛔
E       
E       Response Status is NOT in the expected list.
E       Expected IN: 420
E       Received: 200
E       
E       Endpoint: http://testserver/warehouse_movement/add_multiple_internal
E       Content: [{"priority":"priority_3",.....}]
```
# CreateFulfillment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**bill_target_date** | **date** | The target date for the Fulfillment to be picked up by bill run for billing.  | [optional] 
**carrier** | **str** | The carrier of the Fulfillment. The available values can be configured in **Billing Settings** &gt; **Fulfillment Settings** through Zuora UI.  | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of a Fulfillment object.  | [optional] 
**description** | **str** | The description of the Fulfillment.  | [optional] 
**external_id** | **str** | The external id of the Fulfillment.  | [optional] 
**fulfillment_date** | **date** | The date of the Fulfillment.  | 
**fulfillment_location** | **str** | The fulfillment location of the Fulfillment. The available values can be configured in **Billing Settings** &gt; **Fulfillment Settings** through Zuora UI.  | [optional] 
**fulfillment_system** | **str** | The fulfillment system of the Fulfillment. The available values can be configured in **Billing Settings** &gt; **Fulfillment Settings** through Zuora UI.  | [optional] 
**fulfillment_type** | [**FulfillmentType**](FulfillmentType.md) |  | [optional] 
**order_line_item_id** | **str** | The reference id of the related Order Line Item.  | 
**quantity** | **float** | The quantity of the Fulfillment.  | 
**state** | [**FulfillmentState**](FulfillmentState.md) |  | [optional] 
**tracking_number** | **str** | The tracking number of the Fulfillment.  | [optional] 
**fulfillment_items** | [**List[FulfillmentItem]**](FulfillmentItem.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.create_fulfillment import CreateFulfillment

# TODO update the JSON string below
json = "{}"
# create an instance of CreateFulfillment from a JSON string
create_fulfillment_instance = CreateFulfillment.from_json(json)
# print the JSON string representation of the object
print(CreateFulfillment.to_json())

# convert the object into a dict
create_fulfillment_dict = create_fulfillment_instance.to_dict()
# create an instance of CreateFulfillment from a dict
create_fulfillment_from_dict = CreateFulfillment.from_dict(create_fulfillment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



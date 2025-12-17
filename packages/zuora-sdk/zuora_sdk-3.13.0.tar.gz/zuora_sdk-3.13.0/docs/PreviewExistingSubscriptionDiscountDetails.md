# PreviewExistingSubscriptionDiscountDetails


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**discount_charge_number** | **str** | The charge number of the discount. | [optional] 
**discount_rate** | **float** | The discount rate. | [optional] 
**discount_charge_name** | **str** | Discount charge name. | [optional] 
**service_start_date** | **date** | Start date of the service period for this discount charge. | [optional] 
**service_end_date** | **date** | End date of the service period for this discount charge. | [optional] 

## Example

```python
from zuora_sdk.models.preview_existing_subscription_discount_details import PreviewExistingSubscriptionDiscountDetails

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewExistingSubscriptionDiscountDetails from a JSON string
preview_existing_subscription_discount_details_instance = PreviewExistingSubscriptionDiscountDetails.from_json(json)
# print the JSON string representation of the object
print(PreviewExistingSubscriptionDiscountDetails.to_json())

# convert the object into a dict
preview_existing_subscription_discount_details_dict = preview_existing_subscription_discount_details_instance.to_dict()
# create an instance of PreviewExistingSubscriptionDiscountDetails from a dict
preview_existing_subscription_discount_details_from_dict = PreviewExistingSubscriptionDiscountDetails.from_dict(preview_existing_subscription_discount_details_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



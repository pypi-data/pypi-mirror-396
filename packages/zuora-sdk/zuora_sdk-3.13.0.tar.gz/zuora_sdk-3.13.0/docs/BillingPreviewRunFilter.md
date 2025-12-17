# BillingPreviewRunFilter


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**filter_type** | **str** | The type of filter to apply.  | 
**account_id** | **str** | The target account ID.  | 

## Example

```python
from zuora_sdk.models.billing_preview_run_filter import BillingPreviewRunFilter

# TODO update the JSON string below
json = "{}"
# create an instance of BillingPreviewRunFilter from a JSON string
billing_preview_run_filter_instance = BillingPreviewRunFilter.from_json(json)
# print the JSON string representation of the object
print(BillingPreviewRunFilter.to_json())

# convert the object into a dict
billing_preview_run_filter_dict = billing_preview_run_filter_instance.to_dict()
# create an instance of BillingPreviewRunFilter from a dict
billing_preview_run_filter_from_dict = BillingPreviewRunFilter.from_dict(billing_preview_run_filter_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



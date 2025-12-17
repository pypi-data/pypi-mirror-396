# RecurringCalculatedPricingOverride

Pricing information about a recurring charge that uses the \"calculated\" charge model. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**minimum_amount** | **float** | minimumAmount.  | [optional] 
**maximum_amount** | **float** | maximumAmount.  | [optional] 
**percentage** | **float** | percentage.  | [optional] 
**eligible_account_conditions** | **Dict[str, object]** | Container for eligibleAccountConditions. | [optional] 
**eligible_charge_conditions** | **Dict[str, object]** | Container for eligibleChargeConditions. | [optional] 
**clearing_existing_minimum_amount** | **bool** | Clear Existing MinimumAmount. | [optional] 
**clearing_existing_maximum_amount** | **bool** | Clear Existing MaximumAmount. | [optional] 

## Example

```python
from zuora_sdk.models.recurring_calculated_pricing_override import RecurringCalculatedPricingOverride

# TODO update the JSON string below
json = "{}"
# create an instance of RecurringCalculatedPricingOverride from a JSON string
recurring_calculated_pricing_override_instance = RecurringCalculatedPricingOverride.from_json(json)
# print the JSON string representation of the object
print(RecurringCalculatedPricingOverride.to_json())

# convert the object into a dict
recurring_calculated_pricing_override_dict = recurring_calculated_pricing_override_instance.to_dict()
# create an instance of RecurringCalculatedPricingOverride from a dict
recurring_calculated_pricing_override_from_dict = RecurringCalculatedPricingOverride.from_dict(recurring_calculated_pricing_override_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



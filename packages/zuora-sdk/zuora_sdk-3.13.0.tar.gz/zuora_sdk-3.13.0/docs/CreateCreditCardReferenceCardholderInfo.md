# CreateCreditCardReferenceCardholderInfo

Container for cardholder information. This container field is required for credit card payment methods. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**card_holder_name** | **str** | The card holder&#39;s full name as it appears on the card, e.g., \&quot;John J Smith\&quot;, 50 characters or less. | [optional] 

## Example

```python
from zuora_sdk.models.create_credit_card_reference_cardholder_info import CreateCreditCardReferenceCardholderInfo

# TODO update the JSON string below
json = "{}"
# create an instance of CreateCreditCardReferenceCardholderInfo from a JSON string
create_credit_card_reference_cardholder_info_instance = CreateCreditCardReferenceCardholderInfo.from_json(json)
# print the JSON string representation of the object
print(CreateCreditCardReferenceCardholderInfo.to_json())

# convert the object into a dict
create_credit_card_reference_cardholder_info_dict = create_credit_card_reference_cardholder_info_instance.to_dict()
# create an instance of CreateCreditCardReferenceCardholderInfo from a dict
create_credit_card_reference_cardholder_info_from_dict = CreateCreditCardReferenceCardholderInfo.from_dict(create_credit_card_reference_cardholder_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



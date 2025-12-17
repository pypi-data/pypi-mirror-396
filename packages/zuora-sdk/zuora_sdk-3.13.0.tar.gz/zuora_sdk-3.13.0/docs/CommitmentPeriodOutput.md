# CommitmentPeriodOutput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the period. | 
**start_date** | **date** | The start date of the period. | 
**end_date** | **date** | The end date of the period. The period end date is inclusive in the period, same as the commitment end date | 
**id** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.commitment_period_output import CommitmentPeriodOutput

# TODO update the JSON string below
json = "{}"
# create an instance of CommitmentPeriodOutput from a JSON string
commitment_period_output_instance = CommitmentPeriodOutput.from_json(json)
# print the JSON string representation of the object
print(CommitmentPeriodOutput.to_json())

# convert the object into a dict
commitment_period_output_dict = commitment_period_output_instance.to_dict()
# create an instance of CommitmentPeriodOutput from a dict
commitment_period_output_from_dict = CommitmentPeriodOutput.from_dict(commitment_period_output_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



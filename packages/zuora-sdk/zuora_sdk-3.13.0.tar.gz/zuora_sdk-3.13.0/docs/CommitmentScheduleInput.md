# CommitmentScheduleInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of each period in the schedule. | 
**amount_base** | [**AmountBaseEnum**](AmountBaseEnum.md) |  | [optional] 
**period_type** | [**PeriodTypeEnum**](PeriodTypeEnum.md) |  | [optional] 
**specific_period_length** | **int** | The specific period length of each period in the schedule. | [optional] 
**start_date** | **date** | The start date of the schedule. | 
**end_date** | **date** | The end date of the schedule. The schedule end date is inclusive in the schedule, same as the commitment end date | 

## Example

```python
from zuora_sdk.models.commitment_schedule_input import CommitmentScheduleInput

# TODO update the JSON string below
json = "{}"
# create an instance of CommitmentScheduleInput from a JSON string
commitment_schedule_input_instance = CommitmentScheduleInput.from_json(json)
# print the JSON string representation of the object
print(CommitmentScheduleInput.to_json())

# convert the object into a dict
commitment_schedule_input_dict = commitment_schedule_input_instance.to_dict()
# create an instance of CommitmentScheduleInput from a dict
commitment_schedule_input_from_dict = CommitmentScheduleInput.from_dict(commitment_schedule_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



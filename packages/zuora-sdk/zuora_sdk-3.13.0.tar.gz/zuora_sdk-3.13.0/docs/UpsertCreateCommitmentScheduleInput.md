# UpsertCreateCommitmentScheduleInput

Create a new schedule.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of each period in the schedule. | 
**amount_base** | [**AmountBaseEnum**](AmountBaseEnum.md) |  | [optional] 
**period_type** | [**PeriodTypeEnum**](PeriodTypeEnum.md) |  | [optional] 
**specific_period_length** | **int** | The specific period length of each period in the schedule. | [optional] 
**start_date** | **date** | The start date of the schedule. | 
**end_date** | **date** | The end date of the schedule. The schedule end date is inclusive in the schedule, same as the commitment end date | 
**action** | [**ActionType**](ActionType.md) |  | 

## Example

```python
from zuora_sdk.models.upsert_create_commitment_schedule_input import UpsertCreateCommitmentScheduleInput

# TODO update the JSON string below
json = "{}"
# create an instance of UpsertCreateCommitmentScheduleInput from a JSON string
upsert_create_commitment_schedule_input_instance = UpsertCreateCommitmentScheduleInput.from_json(json)
# print the JSON string representation of the object
print(UpsertCreateCommitmentScheduleInput.to_json())

# convert the object into a dict
upsert_create_commitment_schedule_input_dict = upsert_create_commitment_schedule_input_instance.to_dict()
# create an instance of UpsertCreateCommitmentScheduleInput from a dict
upsert_create_commitment_schedule_input_from_dict = UpsertCreateCommitmentScheduleInput.from_dict(upsert_create_commitment_schedule_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



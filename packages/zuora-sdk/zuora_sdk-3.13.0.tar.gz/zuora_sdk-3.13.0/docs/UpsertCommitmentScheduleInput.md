# UpsertCommitmentScheduleInput

Upsert an schedule, when the action is create, create a new schedule, when the action is update, update the schedule

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
**id** | **str** | The ID of the schedule. | 
**status** | [**CommitmentScheduleStatus**](CommitmentScheduleStatus.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.upsert_commitment_schedule_input import UpsertCommitmentScheduleInput

# TODO update the JSON string below
json = "{}"
# create an instance of UpsertCommitmentScheduleInput from a JSON string
upsert_commitment_schedule_input_instance = UpsertCommitmentScheduleInput.from_json(json)
# print the JSON string representation of the object
print(UpsertCommitmentScheduleInput.to_json())

# convert the object into a dict
upsert_commitment_schedule_input_dict = upsert_commitment_schedule_input_instance.to_dict()
# create an instance of UpsertCommitmentScheduleInput from a dict
upsert_commitment_schedule_input_from_dict = UpsertCommitmentScheduleInput.from_dict(upsert_commitment_schedule_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



# UpsertCreateCommitmentInputAllOfSchedules


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of each period in the schedule. | 
**amount_base** | [**AmountBaseEnum**](AmountBaseEnum.md) |  | [optional] 
**period_type** | [**PeriodTypeEnum**](PeriodTypeEnum.md) |  | [optional] 
**specific_period_length** | **int** | The specific period length of each period in the schedule. | [optional] 
**start_date** | **date** | The start date of the schedule. | 
**end_date** | **date** | The end date of the schedule. The schedule end date is inclusive in the schedule, same as the commitment end date | 
**action** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.upsert_create_commitment_input_all_of_schedules import UpsertCreateCommitmentInputAllOfSchedules

# TODO update the JSON string below
json = "{}"
# create an instance of UpsertCreateCommitmentInputAllOfSchedules from a JSON string
upsert_create_commitment_input_all_of_schedules_instance = UpsertCreateCommitmentInputAllOfSchedules.from_json(json)
# print the JSON string representation of the object
print(UpsertCreateCommitmentInputAllOfSchedules.to_json())

# convert the object into a dict
upsert_create_commitment_input_all_of_schedules_dict = upsert_create_commitment_input_all_of_schedules_instance.to_dict()
# create an instance of UpsertCreateCommitmentInputAllOfSchedules from a dict
upsert_create_commitment_input_all_of_schedules_from_dict = UpsertCreateCommitmentInputAllOfSchedules.from_dict(upsert_create_commitment_input_all_of_schedules_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



# UpsertUpdateCommitmentScheduleInput

Update an existing commitment schedule.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the schedule. | 
**amount** | **float** | The amount of each period in the schedule. | [optional] 
**action** | [**ActionType**](ActionType.md) |  | 
**status** | [**CommitmentScheduleStatus**](CommitmentScheduleStatus.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.upsert_update_commitment_schedule_input import UpsertUpdateCommitmentScheduleInput

# TODO update the JSON string below
json = "{}"
# create an instance of UpsertUpdateCommitmentScheduleInput from a JSON string
upsert_update_commitment_schedule_input_instance = UpsertUpdateCommitmentScheduleInput.from_json(json)
# print the JSON string representation of the object
print(UpsertUpdateCommitmentScheduleInput.to_json())

# convert the object into a dict
upsert_update_commitment_schedule_input_dict = upsert_update_commitment_schedule_input_instance.to_dict()
# create an instance of UpsertUpdateCommitmentScheduleInput from a dict
upsert_update_commitment_schedule_input_from_dict = UpsertUpdateCommitmentScheduleInput.from_dict(upsert_update_commitment_schedule_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



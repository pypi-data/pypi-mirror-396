# CommitmentOutputSchedulesInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the schedule. | [optional] 
**status** | [**CommitmentScheduleStatusOutput**](CommitmentScheduleStatusOutput.md) |  | [optional] 
**start_date** | **date** | The start date of the schedule. | [optional] 
**end_date** | **date** | The end date of the schedule. The schedule end date is inclusive in the schedule, same as the commitment end date. | [optional] 
**total_amount** | **float** | The total amount of the schedule. | [optional] 

## Example

```python
from zuora_sdk.models.commitment_output_schedules_inner import CommitmentOutputSchedulesInner

# TODO update the JSON string below
json = "{}"
# create an instance of CommitmentOutputSchedulesInner from a JSON string
commitment_output_schedules_inner_instance = CommitmentOutputSchedulesInner.from_json(json)
# print the JSON string representation of the object
print(CommitmentOutputSchedulesInner.to_json())

# convert the object into a dict
commitment_output_schedules_inner_dict = commitment_output_schedules_inner_instance.to_dict()
# create an instance of CommitmentOutputSchedulesInner from a dict
commitment_output_schedules_inner_from_dict = CommitmentOutputSchedulesInner.from_dict(commitment_output_schedules_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



# CommonRevenueAttributesOutput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**adjustment_liability_accounting_code** | **str** | The accounting code on the Commitment object for customers using [Zuora Billing - Revenue Integration](https://knowledgecenter.zuora.com/Zuora_Revenue/Zuora_Billing_-_Revenue_Integration).  | [optional] 
**adjustment_revenue_accounting_code** | **str** | The accounting code on the Commitment object for customers using [Zuora Billing - Revenue Integration](https://knowledgecenter.zuora.com/Zuora_Revenue/Zuora_Billing_-_Revenue_Integration).  | [optional] 
**contract_asset_accounting_code** | **str** | The accounting code on the Commitment object for customers using [Zuora Billing - Revenue Integration](https://knowledgecenter.zuora.com/Zuora_Revenue/Zuora_Billing_-_Revenue_Integration).  | [optional] 
**contract_liability_accounting_code** | **str** | The accounting code on the Commitment object for customers using [Zuora Billing - Revenue Integration](https://knowledgecenter.zuora.com/Zuora_Revenue/Zuora_Billing_-_Revenue_Integration).  | [optional] 
**contract_recognized_revenue_accounting_code** | **str** | The accounting code on the Commitment object for customers using [Zuora Billing - Revenue Integration](https://knowledgecenter.zuora.com/Zuora_Revenue/Zuora_Billing_-_Revenue_Integration).  | [optional] 
**deferred_revenue_accounting_code** | **str** | The deferred revenue accounting code for the Commitment.  | [optional] 
**exclude_item_billing_from_revenue_accounting** | **bool** | The flag to exclude Commitment related invoice items, invoice item adjustments, credit memo items, and debit memo items from revenue accounting.   **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.   | [optional] 
**is_allocation_eligible** | **bool** | This field is used to identify if the commitment is allocation eligible in revenue recognition.  **Note**: This feature is in the **Early Adopter** phase. If you want to use the feature, submit a request at &lt;a href&#x3D;\&quot;https://support.zuora.com/\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Zuora Global Support&lt;/a&gt;, and we will evaluate whether the feature is suitable for your use cases.  | [optional] 
**is_unbilled** | **bool** | This field is used to dictate how to perform the accounting during revenue recognition.  **Note**: This feature is in the **Early Adopter** phase. If you want to use the feature, submit a request at &lt;a href&#x3D;\&quot;https://support.zuora.com/\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Zuora Global Support&lt;/a&gt;, and we will evaluate whether the feature is suitable for your use cases.  | [optional] 
**recognized_revenue_accounting_code** | **str** | The recognized revenue accounting code for the Commitment.  | [optional] 
**revenue_recognition_rule** | **str** | The Revenue Recognition rule for the Commitment.  | [optional] 
**account_receivable_accounting_code** | **str** | The accounting code on the Commitment object for customers | [optional] 
**unbilled_receivables_accounting_code** | **str** | The accounting code on the Commitment object for customers using [Zuora Billing - Revenue Integration](https://knowledgecenter.zuora.com/Zuora_Revenue/Zuora_Billing_-_Revenue_Integration).  | [optional] 
**revenue_recognition_timing** | **str** | This field is used to dictate the type of revenue recognition timing. | [optional] 
**revenue_amortization_method** | **str** | This field is used to dictate the type of revenue amortization method. | [optional] 
**exclude_item_booking_from_revenue_accounting** | **bool** | The flag to exclude rate plan charges from revenue accounting. | [optional] [readonly] 

## Example

```python
from zuora_sdk.models.common_revenue_attributes_output import CommonRevenueAttributesOutput

# TODO update the JSON string below
json = "{}"
# create an instance of CommonRevenueAttributesOutput from a JSON string
common_revenue_attributes_output_instance = CommonRevenueAttributesOutput.from_json(json)
# print the JSON string representation of the object
print(CommonRevenueAttributesOutput.to_json())

# convert the object into a dict
common_revenue_attributes_output_dict = common_revenue_attributes_output_instance.to_dict()
# create an instance of CommonRevenueAttributesOutput from a dict
common_revenue_attributes_output_from_dict = CommonRevenueAttributesOutput.from_dict(common_revenue_attributes_output_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



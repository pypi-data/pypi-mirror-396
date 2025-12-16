

Public

# IOT Orders process in CPQ

| **SOQL<br/>Query** | **1) Salesforce inspector Soql :-** select createddate, Id, Name, Order\_\_c, Order\_\_r.csord\_\_Account\_\_r.name<br/>From CSPOFA\_\_Orchestration\_Process\_\_c<br/>where CSPOFA\_\_Orchestration\_Process\_Template\_\_r.name ='Order Fulfillment Process IoT'<br/>and CSPOFA\_\_Process\_On\_Hold\_\_c = true<br/>and Order\_\_r.csord\_\_Status2\_\_c <> 'Cancelled'<br/>and createddate > 2024-10-15T19:21:25.175+08:00<br/><br/><br/>Export Query Templates ▼ Query History ▼ Clear Saved Queries ▼ ☑ IOT Matching Save Query ▼	☐ Deleted/Archived Records? ☐ Tooling API?&#xA;CSPOFA\_\_Orchestration\_Process\_\_c&#xA;where CSPOFA\_\_Orchestration\_Process\_Template\_\_r.name ='Order Fulfillment Process IoT'&#xA;and CSPOFA\_\_Process\_On\_Hold\_\_c = true&#xA;and Order\_\_r.csord\_\_Status2\_\_c <> 'Cancelled'&#xA;and createddate > 2024-10-15T19:21:25.175+08:00&#xA;CSPOFA\_\_Orchestration\_Process\_\_c fields suggestions: --- \| SOQL Query \| Open the Orchestration Process record and copy the order id and paste in SOQL.&#xA;&#xA;\*\*2) Salesforce inspector Soql :-\*\* select createddate, Id, csord\_\_Status\_\_c, csord\_\_Subscription\_\_c, Contract\_Term\_\_c, Name, External\_ID\_\_c, SIM\_Serial\_Number\_\_c, APN\_Name\_\_c, APN\_Adress\_Type\_\_c, Commitment\_\_c, Commitment\_\_r.name,&#xA;csordtelcoa\_\_Replaced\_Service\_\_r.SIM\_Serial\_Number\_\_c,&#xA;csordtelcoa\_\_Replaced\_Service\_\_r.csordtelcoa\_\_Replaced\_Service\_\_r.SIM\_Serial\_Number\_\_c,&#xA;csord\_\_Identification\_\_c, csordtelcoa\_\_Product\_Configuration\_\_c,&#xA;csordtelcoa\_\_Product\_Configuration\_\_r.Type\_\_c,&#xA;Billing\_Account\_\_c, Commercial\_Product\_\_c&#xA;From csord\_\_Service\_\_c where csord\_\_Order\_\_c = ' \*\*a20Mg000002oKyTIAU\*\*'&#xA;and csordtelcoa\_\_Product\_Configuration\_\_r.Type\_\_c <> null \| \|------------\|-I have completed the transcription of the entire page. There is no additional content to transcribe beyond what was already output in the previous message. Public --- \*\*Export Query\*\* Templates ▼ Query History ▼ Clear Saved Queries ☑ IOT Patching Save Query ▼ ☐ Deleted/Archived Records? ☐ Tooling API? \`\`\` select createddate, Id, csord\_\_Status\_\_c, csord\_\_Subscription\_\_c, Contract\_Term\_\_c, Name, External\_ID\_\_c, SIM\_Serial\_Number\_\_c, APN\_Name\_\_c, APN\_Adress\_Type\_\_c, Commitment\_\_c, Commitment\_\_r.name, csordtelcoa\_\_Replaced\_Service\_\_r.SIM\_Serial\_Number\_\_c, csordtelcoa\_\_Replaced\_Service\_\_r.csordtelcoa\_\_Replaced\_Service\_\_r.SIM\_Serial\_Number\_\_c, csord\_\_Identification\_\_c, csordtelcoa\_\_Product\_Configuration\_\_c, csordtelcoa\_\_Product\_Configuration\_\_r.Type\_\_c, Billing\_Account\_\_c, Commercial\_Product\_\_c from csord\_\_Service\_\_c where csord\_\_Order\_\_c = 'a20Mg000002oKyTIAU' and csordtelcoa\_\_Product\_Configuration\_\_r.Type\_\_c is null \`\`\` csord\_\_Service\_\_c.csord\_\_Order\_\_c values (Press Ctrl+Space to load suggestions): \[Run Export] \[Export Query] \[Query Plan] csord\_\_Service\_\_c Field Info ⚙▼ \*\*Export Result\*\* Copy (Excel) Copy (CSV) Copy (JSON) ⬇ \[Delete Records] 🔍 Filter Result Exported 31 records 190.7ms StopId	csord\_\_Status\_\_c	csord\_\_Subscription\_\_c	Contract\_Term\_\_c	Name	External\_ID\_\_c	SIM\_Serial\_Number\_\_c	APN\_Name\_\_c	APN\_Adress\_Type\_\_c	Commitment\_\_ca23Mg000006bdGfIAI	Service Created	a26Mg000001DjRUIAK	12	601114266569 - Mobile Managed MM2M 15MB Plan (FUP)	601114266569	8960012201903524756	MACHINE1C	Dynamic	a2e2r0000006&#xA;a23Mg000006bdGgIAI	Service Created	a26Mg000001DjRmIAK	12	601114259087 - Mobile Managed MM2M 15MB Plan (FUP)	601114259087	8960012201903524723	MACHINE1C	Dynamic	a2e2r0000006&#xA;a23Mg000006bdGhIAI	Service Created	a26Mg000001DjRnIAK	12	601112351741 - Mobile Managed MM2M 15MB Plan (FUP)	601112351741	8960012201903524699	MACHINE1C	Dynamic	a2e2r0000006&#xA;a23Mg000006bdGiIAI	Service Created	a26Mg000001DjRoIAK	12	60142346893 - Mobile Managed MM2M 15MB Plan (FUP)	60142346893	8960012201903524673	MACHINE1C	Dynamic	a2e2r0000006&#xA;a23Mg000006bdGjIAI	Service Created	a26Mg000001DjRpIAK	12	601114220349 - Mobile Managed MM2M 15MB Plan (FUP)	601114220349	8960012201903524624	MACHINE1C	Dynamic	a2e2r0000006&#xA;a23Mg000006bdGkIAI	Service Created	a26Mg000001DjRqIAK	12	601172376416 - Mobile Managed MM2M 15MB Plan (FUP)	601172376416	8960012201903524574	MACHINE1C	Dynamic	a2e2r0000006&#xA;a23Mg000006bdGlIAI	Service Created	a26Mg000001DjRrIAK	12	60142695307 - Mobile Managed MM2M 5MB Plan (FUP)	60142695307	8960012201903524780	MACHINE1C	Dynamic	a2e2r0000006&#xA;a23Mg000006bdGmIAI	Service Created	a26Mg000001DjRsIAK	12	60142342419 - Mobile Managed MM2M 5MB Plan (FUP)	60142342419	8960012201903524772	MACHINE1C	Dynamic	a2e2r0000006&#xA;a23Mg000006bdGnIAI	Service Created	a26Mg000001DjRtIAK	12	601114398268 - Mobile Managed MM2M 5MB Plan (FUP)	601114398268	8960012201903524764	MACHINE1C	Dynamic	a2e2r0000006&#xA;a23Mg000006bdGoIAI	Service Created	a26Mg000001DjRuIAK	12	601114264986 - Mobile Managed MM2M 5MB Plan (FUP)	601114264986	8960012201903524749	MACHINE1C	Dynamic	a2e2r0000006&#xA;a23Mg000006bdGpIAI	Service Created	a26Mg000001DjRvIAK	12	601114261126 - Mobile Managed MM2M 5MB Plan (FUP)	601114261126	8960012201903524731	MACHINE1C	Dynamic	a2e2r0000006&#xA;a23Mg000006bdGqIAI	Service Created	a26Mg000001DjRwIAK	12	601112897351 - Mobile Managed MM2M 5MB Plan (FUP)	601112897351	8960012201903524715	MACHINE1C	Dynamic	a2e2r0000006 |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |


Public



---




Public

**Comparison Data**

Open the Basket with help of order id in CPQ.

| Export Query                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Templates ▼ Query History ▼ Clear Saved Queries ▼ ☑ IOT Patching Save Query ▼ ☐ Deleted/Archived Records? ☐ Tooling API?                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ```
select createddate, Id, csord__Status__c, csord__Subscription__c, Contract_Term__c, Name, External_ID__c, SIM_Serial_Number__c, APN_Name__c, APN_Adress_Type__c, Commitment__c,
Commitment__r.name,
csordtelcoa__Replaced_Service__r.SIM_Serial_Number__c,
csordtelcoa__Replaced_Service__r.csordtelcoa__Replaced_Service__r.SIM_Serial_Number__c, csord__Identification__c, csordtelcoa__Product_Configuration__c,
csordtelcoa__Product_Configuration__r.Type__c,
Billing_Account__c, Commercial_Product__c
from
csord__Service__c
where csord__Order__c = 'a20Mg000002oKyTIAU'
and csordtelcoa__Product_Configuration__r.Type__c <> null
``` |
| csord\_\_Service\_\_c.csord\_\_Order\_\_c values (Press Ctrl+Space to load suggestions): Run Export Export Query Query Plan csord\_\_Service\_\_c Field Info ▼ ▼                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |


| Export Result | Copy (Excel) Copy (CSV) Copy (JSON) ⬇ 🔍 Filter Result | Copy (Excel) Copy (CSV) Copy (JSON) ⬇ 🔍 Filter Result | Copy (Excel) Copy (CSV) Copy (JSON) ⬇ 🔍 Filter Result | Copy (Excel) Copy (CSV) Copy (JSON) ⬇ 🔍 Filter Result | Copy (Excel) Copy (CSV) Copy (JSON) ⬇ 🔍 Filter Result | Copy (Excel) Copy (CSV) Copy (JSON) ⬇ 🔍 Filter Result | Exported 31 records 190.7ms |
| ------------- | ------------------------------------------------------ | ------------------------------------------------------ | ------------------------------------------------------ | ------------------------------------------------------ | ------------------------------------------------------ | ------------------------------------------------------ | --------------------------- |


| \_\_Replaced\_Service\_\_r     | csord\_\_Identification\_\_c | csordtelcoa\_\_Product\_Configuration\_\_c | csordtelcoa\_\_Product\_Configuration\_\_r | csordtelcoa\_\_Product\_Configuration\_\_r.Type\_\_c | Billing\_Account\_\_c | Commercial\_Product\_\_c |
| ------------------------------ | ---------------------------- | ------------------------------------------ | ------------------------------------------ | ---------------------------------------------------- | --------------------- | ------------------------ |
| Service\_aOxMg0000045GgBIAU\_0 | a0xMg0000045GgBIAU           | cscfga\_\_Product\_Configuration\_\_c      | No Change                                  |                                                      | a382r000000DDZIAAO    | a2e2r0000006OnyAAE       |
| Service\_aOxMg0000045GgBIAU\_1 | a0xMg0000045GgBIAU           | cscfga\_\_Product\_Configuration\_\_c      | No Change                                  |                                                      | a382r000000DDZIAAO    | a2e2r0000006OnyAAE       |
| Service\_aOxMg0000045GgBIAU\_2 | a0xMg0000045GgBIAU           | cscfga\_\_Product\_Configuration\_\_c      | No Change                                  |                                                      | a382r000000DDZIAAO    | a2e2r0000006OnyAAE       |
| Service\_aOxMg0000045GgBIAU\_3 | a0xMg0000045GgBIAU           | cscfga\_\_Product\_Configuration\_\_c      | No Change                                  |                                                      | a382r000000DDZIAAO    | a2e2r0000006OnyAAE       |
| Service\_aOxMg0000045GgBIAU\_4 | a0xMg0000045GgBIAU           | cscfga\_\_Product\_Configuration\_\_c      | No Change                                  |                                                      | a382r000000DDZIAAO    | a2e2r0000006OnyAAE       |
| Service\_aOxMg0000045GgBIAU\_5 | a0xMg0000045GgBIAU           | cscfga\_\_Product\_Configuration\_\_c      | No Change                                  |                                                      | a382r000000DDZIAAO    | a2e2r0000006OnyAAE       |
| Service\_aOxMg0000045HQwIAM\_0 | a0xMg0000045HQwIAM           | cscfga\_\_Product\_Configuration\_\_c      | Downgrade                                  |                                                      | a382r000000DDZIAAO    | a2e2r0000006Oo4AAE       |
| Service\_aOxMg0000045HQwIAM\_1 | a0xMg0000045HQwIAM           | cscfga\_\_Product\_Configuration\_\_c      | Downgrade                                  |                                                      | a382r000000DDZIAAO    | a2e2r0000006Oo4AAE       |
| Service\_aOxMg0000045HQwIAM\_2 | a0xMg0000045HQwIAM           | cscfga\_\_Product\_Configuration\_\_c      | Downgrade                                  |                                                      | a382r000000DDZIAAO    | a2e2r0000006Oo4AAE       |
| Service\_aOxMg0000045HQwIAM\_3 | a0xMg0000045HQwIAM           | cscfga\_\_Product\_Configuration\_\_c      | Downgrade                                  |                                                      | a382r000000DDZIAAO    | a2e2r0000006Oo4AAE       |
| Service\_aOxMg0000045HQwIAM\_4 | a0xMg0000045HQwIAM           | cscfga\_\_Product\_Configuration\_\_c      | Downgrade                                  |                                                      | a382r000000DDZIAAO    | a2e2r0000006Oo4AAE       |
| Service\_aOxMg0000045HQwIAM\_5 | a0xMg0000045HQwIAM           | cscfga\_\_Product\_Configuration\_\_c      | Downgrade                                  |                                                      | a382r000000DDZIAAO    | a2e2r0000006Oo4AAE       |





---




Public

## Compare Basket data and CPQ data using SOQL

## Steps: -

### a) Check the number of Downgrade, Change APN, Terminate, Upgrade and Change service type should be same as basket

| Service\_\_csord\_\_Identification\_\_c | csordtelcoa\_\_Product\_Configuration\_\_c | csordtelcoa\_\_Product\_Configuration\_\_r | csordtelcoa\_\_Product\_Configuration\_\_r.Type\_\_c | Billing\_Account\_\_c | Commercial\_Product\_\_c | csordtelcoa\_\_Repla |
| --------------------------------------- | ------------------------------------------ | ------------------------------------------ | ---------------------------------------------------- | --------------------- | ------------------------ | -------------------- |
| Service\_a0xMg0000047PvRIAU\_0          | a0xMg0000047PgyIAE                         | .cscfga...\_Product\_Configuration....c    | No Change                                            | a82r000000F3sfAAC     | a2e2r0000006O04AAE       |                      |
| Service\_a0xMg0000047PvRIAU\_1          | a0xMg0000047PvRIAU                         | .cscfga..Product.Configuration.c           | Downgrade                                            | a82r000000DH4uAAG     | a2e2r0000006Oo4AAE       |                      |
| Service\_a0xMg0000047PvRIAU\_2          | a0xMg0000047PvRIAU                         | .cscfga....Product.Configuration....c      | Downgrade                                            | a82r000000DY8IAAW     | a2e2r0000006O04AAE       |                      |
| Service\_a0xMg0000047PvRIAU\_3          | a0xMg0000047PvRIAU                         | .cscfga...\_Product\_Configuration...\_    | Downgrade                                            | a82r000000EgvuAAC     | a2e2r0000006Oo4AAE       |                      |
| Service\_a0xMg0000047PvRIAU\_4          | a0xMg0000047PvRIAU                         | .cscfga..\_Product\_Configuration...       | Downgrade                                            | a82r000000DgvLAAS     | a2e2r0000006Oo4AAE       |                      |
| Service\_a0xMg0000047PvRIAU\_5          | a0xMg0000047PvRIAU                         | .cscfga...Product...Configuration...       | Downgrade                                            | a82r000000E1bAAAS     | a2e2r0000006O04AAE       |                      |
| Service\_a0xMg0000047QDBIA2\_0          | a0xMg0000047PiXIAU                         | .cscfga.Product..Configuration..c          | No Change                                            | a82r000000Fz1wAAC     | a2e2r0000006O04AAE       |                      |
| Service\_a0xMg0000047QJdIAM\_0          |                                            | .cscfga..\_Product\_Configuration....c     | No Change                                            | a82r000000DOxpAAG     | a2e2r0000006Oo4AAE       |                      |
| Service\_a0xMg0000047PNZIA2\_0          | a0xMg0000047PNZIA2                         | .cscfga.Product\_Configuration.c           | Modify                                               | a82r000000ElykAAC     |                          |                      |
| Service\_a0xMg0000047PgvIAE\_0          |                                            | .cscfga...roduct..Configuration....c       | Downgrade                                            |                       | a2e2r0000006OnyAAE       |                      |
| Service\_a0xMg0000047PgvIAE\_1          | a0xMg0000047PvRIAU                         | .cscfga...Product..Configuration...        | Downgrade                                            | a82r000000DY8IAAW     | a2e2r0000006OnyAAE       |                      |
| Service\_a0xMg0000047PgvIAE\_2          | a0xMg0000047PvRIAU                         | .cscfga...\_Product\_Configuration....c    | Downgrade                                            | a82r000000FxbvAAC     | a2e2r0000006OnyAAE       |                      |
| Service\_a0xMg0000047PgvIAE\_3          |                                            | .cscfga..\_Product.Configuration.c         | Downgrade                                            | a82r000000D62BAAS     | a2e2r0000006OnyAAE       |                      |
| Service\_a0xMg0000047PgvIAE\_4          | a0xMg0000047PvRIAU                         | .cscfga..Product..Configuration...         | Downgrade                                            | a82r000000Djr5AAC     | a2e2r0000006OpVAAE       |                      |
| Service\_a0xMg0000047PgvIAE\_5          | a0xMg0000047PvRIAU                         | .cscfga.Product.Configuration....          | Downgrade                                            | a82r000000DjxPAAS     | a2e2r0000006OnyAAE       |                      |
| Service\_a0xMg0000047PgvIAE\_6          | a0xMg0000047PvRIAU                         | .cscfga.Product\_Configuration...          | Downgrade                                            | a82r000000DGogAAG     | a2e2r0000006OnyAAE       |                      |


### b) External Id cannot be SVC%, must be valid MSISDN


---




csord__Service__c.csord__Order__c values (Press Ctrl+Space to load suggestions)

**Export Result** Copy (Excel) Copy (CSV) Copy (JSON) Delete Records Filter Result

Filtered 58 records out of 58 records 4653.2ms

| csord\_\_Status\_\_c | csord\_\_Subscription\_\_c | Contract\_Term\_\_c | Name                                               | External\_ID\_\_c | SIM\_Serial\_Number\_\_c | APN\_Name\_\_c | APN\_Address\_Type\_\_c | Commitment\_\_c    | Commitment     |
| -------------------- | -------------------------- | ------------------- | -------------------------------------------------- | ----------------- | ------------------------ | -------------- | ----------------------- | ------------------ | -------------- |
| Service Created      | a26Mg000001EA3lIAG         | 12                  | 601125785767 - Mobile Managed MM2M 15MB Plan (FUP) | 601125785767      | 8960012105838220796      |                |                         | a2e2r0000006QhkAAE | cspmb\_\_Price |
| Service Created      | a26Mg000001EA3mIAG         | 12                  | SVC-013063224 - Mobile Managed MM2M 5MB Plan (FUP) | SVC-013063224     | 8960012105838220747      |                |                         | a2e2r0000006QhkAAE | cspmb\_\_Price |
| Service Created      | a26Mg000001EA3nIAG         | 12                  | SVC-013063225 - Mobile Managed MM2M 5MB Plan (FUP) | SVC-013063225     | 8960012105838220630      |                |                         | a2e2r0000006QhkAAE | cspmb\_\_Price |
| Service Created      | a26Mg000001EA3oIAG         | 12                  | SVC-013063226 - Mobile Managed MM2M 5MB Plan (FUP) | SVC-013063226     | 8960012105838220622      |                |                         | a2e2r0000006QhkAAE | cspmb\_\_Price |
| Service Created      | a26Mg000001EA3pIAG         | 12                  | SVC-013063227 - Mobile Managed MM2M 5MB Plan (FUP) | SVC-013063227     | 8960012105838220796      |                |                         | a2e2r0000006QhkAAE | cspmb\_\_Price |
| Service Created      | a26Mg000001EA3qIAG         | 12                  | SVC-013063228 - Mobile Managed MM2M 5MB Plan (FUP) | SVC-013063228     | 8960012105838220812      |                |                         | a2e2r0000006QhkAAE | cspmb\_\_Price |
| Service Created      | a26Mg000001EA3rIAG         | 12                  | 60126934102 - Mobile Managed MM2M 15MB Plan (FUP)  | 60126934102       | 8960011911691239927      |                |                         | a2e2r0000006QhkAAE | cspmb\_\_Price |
| Service Created      | a26Mg000001EA3sIAG         | 12                  | 601125789545 - Mobile Managed MM2M 15MB Plan (FUP) | 601125789545      | 8960012105838220614      |                |                         | a2e2r0000006QhkAAE | cspmb\_\_Price |
| Service Created      | a26Mg000001EA29IAG         | 12                  | IoT Solution - MIG                                 | SVC-004640242     |                          |                |                         |                    |                |
| Service Created      | a26Mg000001EA2AIAW         |                     | 601125792870 - Mobile Managed MM2M 5MB Plan (FUP)  | 601125792870      | 8960012105838220747      |                |                         | a2e2r0000006Qf6AAE | cspmb\_\_Price |
| Service Created      | a26Mg000001EA2BIAW         |                     | 601125784893 - Mobile Managed MM2M 5MB Plan (FUP)  | 601125784893      | 8960012105838220762      |                |                         | a2e2r0000006Qf6AAE | cspmb\_\_Price |
| Service Created      | a26Mg000001EA2CIAW         |                     | 601125789846 - Mobile Managed MM2M 5MB Plan (FUP)  | 601125789846      | 8960012105838220713      |                |                         | a2e2r0000006Qf6AAE | cspmb\_\_Price |
| Service Created      | a26Mg000001EA2DIAW         |                     | 601125791418 - Mobile Managed MM2M 5MB Plan (FUP)  | 601125791418      | 8960012105838220739      |                |                         | a2e2r0000006Qf6AAE | cspmb\_\_Price |
| Service Created      | a26Mg000001EA2EIAW         |                     | 601125791586 - Mobile Managed MM2M 5MB Plan (FUP)  | 601125791586      | 8960012105838220697      |                |                         | a2e2r0000006Qf6AAE | cspmb\_\_Price |
| Service Created      | a26Mg000001EA2FIAW         |                     | 601125789904 - Mobile Managed MM2M 5MB Plan (FUP)  | 601125789904      | 8960012105838220689      |                |                         | a2e2r0000006Qf6AAE | cspmb\_\_Price |
| Service Created      | a26Mg000001EA2GIAW         |                     | 601125785206 - Mobile Managed MM2M 5MB Plan (FUP)  | 601125785206      | 8960012105838220770      |                |                         | a2e2r0000006Qf6AAE | cspmb\_\_Price |


## c) Check the SIM in CPQ, the same as Kenan for same MSISDN

- Kenan Component Details by External Id (Active) (MSISDN, ComponentName)
- Kenan All External Id by External Id (Active)
- Kenan Inventory (with history)
- Kenan Commitment Contract (count of active)
- Tertio SO by App Key
- Tertio SO by App Key (Latest only)
- Get Delivery Details from wM

8960012105838220747

List of items to process.

One line for each order.
No additional space and characters are allow.
No blank lines are allow.
Recomended max per submisison is 100 numbers.

Submit

Request =1 (KenanByExternalId3): 8960012105838220747
Retreived

| Idx | #input              | External Id         | Type | Active Date         | Subscriber No | Type            | External Id         | Type | Active Date         | Type                    |
| --- | ------------------- | ------------------- | ---- | ------------------- | ------------- | --------------- | ------------------- | ---- | ------------------- | ----------------------- |
| 1   | 8960012105838220747 | 8960012105838220747 | 12   | 2021-12-29 14:04:28 | 204258331     | SIM Card Number | 204258331.0         | 2    | 2021-12-29 00:00:00 | External Id             |
| 1   | 8960012105838220747 | 8960012105838220747 | 12   | 2021-12-29 14:04:28 | 204258331     | SIM Card Number | 8960012105838220747 | 2    | 2021-12-29 14:04:28 | SIM Card Number         |
| 1   | 8960012105838220747 | 8960012105838220747 | 12   | 2021-12-29 14:04:28 | 204258331     | SIM Card Number | 502121583822074     | 2    | 2021-12-29 14:04:28 | MSI                     |
| 1   | 8960012105838220747 | 8960012105838220747 | 12   | 2021-12-29 14:04:28 | 204258331     | SIM Card Number | 601125792870        | 3    | 2021-12-29 14:04:28 | MSISDN/Telephone Number |
| 1   | 8960012105838220747 | 8960012105838220747 | 12   | 2021-12-29 14:04:28 | 204258331     | SIM Card Number | 204258331 MACHINE1C | 92   | 2021-12-29 00:00:00 | APN                     |


## d) Commitment cannot be blank if blank and wrong manually patch as basket.

Public



---




Public

| csordtelcoa\_\_Product\_Configuration\_\_r.Type\_\_c,<br/>csord\_\_Service\_\_c.csord\_\_Order\_\_c values (Press Ctrl+Space to load suggestions): |                |                        |                    |                           |                                                 |                                       |                                                 |   | Run Export Query Plan csord\_\_Service\_\_c Field Info |   |   |
| -------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ---------------------- | ------------------ | ------------------------- | ----------------------------------------------- | ------------------------------------- | ----------------------------------------------- | - | ------------------------------------------------------ | - | - |
| Export Result Copy (Excel) Copy (CSV) Copy (JSON) Delete Records down Filtered 25 records out of 58 records 4653.2ms Stop                          |                |                        |                    |                           |                                                 |                                       |                                                 |   |                                                        |   |   |
| I\_Serial\_Number\_\_c                                                                                                                             | APN\_Name\_\_c | APN\_Adress\_Type\_\_c | Commitment\_c      | Commitment\_r             | Commitmentr.Name                                | csordtelcoa\_\_Replaced\_Service\_\_r | csordtelcoa\_\_Replaced\_Service\_\_r.SIM\_Seri |   |                                                        |   |   |
| G0012105838220747                                                                                                                                  |                |                        | a2e2r0000006QhkAAE | cspmb\_\_Price\_Item\_\_c | Mobile Managed MM2M 5MB Plan (FUP) x 12 months  |                                       |                                                 |   |                                                        |   |   |
| G0012105838220630                                                                                                                                  |                |                        | a2e2r0000006QhkAAE | cspmb\_\_Price\_Item\_\_c | Mobile Managed MM2M 5MB Plan (FUP) x 12 months  |                                       |                                                 |   |                                                        |   |   |
| G0012105838220622                                                                                                                                  |                |                        | a2e2r0000006QhkAAE | cspmb\_\_Price\_Item\_\_c | Mobile Managed MM2M 5MB Plan (FUP) x 12 months  |                                       |                                                 |   |                                                        |   |   |
| G0012105838220796                                                                                                                                  |                |                        | a2e2r0000006QhkAAE | cspmb\_\_Price\_Item\_\_c | Mobile Managed MM2M 5MB Plan (FUP) x 12 months  |                                       |                                                 |   |                                                        |   |   |
| G0012105838220812                                                                                                                                  |                |                        | a2e2r0000006QhkAAE | cspmb\_\_Price\_Item\_\_c | Mobile Managed MM2M 5MB Plan (FUP) x 12 months  |                                       |                                                 |   |                                                        |   |   |
| G0012105838220747                                                                                                                                  |                |                        | a2e2r0000006Qf6AAE | cspmb\_\_Price\_Item\_\_c | Mobile Managed MM2M 15MB Plan (FUP) x 12 months | csord\_\_Service\_\_c                 | 8960012105838220747                             |   |                                                        |   |   |
| G0012105838220762                                                                                                                                  |                |                        | a2e2r0000006Qf6AAE | cspmb\_\_Price\_Item\_\_c | Mobile Managed MM2M 15MB Plan (FUP) x 12 months | csord\_\_Service\_\_c                 | 8960012105838220762                             |   |                                                        |   |   |
| G0012105838220713                                                                                                                                  |                |                        | a2e2r0000006Qf6AAE | cspmb\_\_Price\_Item\_\_c | Mobile Managed MM2M 15MB Plan (FUP) x 12 months | csord\_\_Service\_\_c                 | 8960012105838220713                             |   |                                                        |   |   |
| G0012105838220739                                                                                                                                  |                |                        | a2e2r0000006Qf6AAE | cspmb\_\_Price\_Item\_\_c | Mobile Managed MM2M 15MB Plan (FUP) x 12 months | csord\_\_Service\_\_c                 | 8960012105838220739                             |   |                                                        |   |   |
| G0012105838220697                                                                                                                                  |                |                        | a2e2r0000006Qf6AAE | cspmb\_\_Price\_Item\_\_c | Mobile Managed MM2M 15MB Plan (FUP) x 12 months | csord\_\_Service\_\_c                 | 8960012105838220697                             |   |                                                        |   |   |
| G0012105838220689                                                                                                                                  |                |                        | a2e2r0000006Qf6AAE | cspmb\_\_Price\_Item\_\_c | Mobile Managed MM2M 15MB Plan (FUP) x 12 months | csord\_\_Service\_\_c                 | 8960012105838220689                             |   |                                                        |   |   |
| G0012105838220770                                                                                                                                  |                |                        | a2e2r0000006Qf6AAE | cspmb\_\_Price\_Item\_\_c | Mobile Managed MM2M 15MB Plan (FUP) x 12 months | csord\_\_Service\_\_c                 | 8960012105838220770                             |   |                                                        |   |   |
| G0012105838220846                                                                                                                                  |                |                        | a2e2r0000006Qf6AAE | cspmb\_\_Price\_Item\_\_c | Mobile Managed MM2M 15MB Plan (FUP) x 12 months | csord\_\_Service\_\_c                 | 8960012105838220846                             |   |                                                        |   |   |
| G0012105838220788                                                                                                                                  |                |                        | a2e2r0000006Qf6AAE | cspmb\_\_Price\_Item\_\_c | Mobile Managed MM2M 15MB Plan (FUP) x 12 months | csord\_\_Service\_\_c                 | 8960012105838220788                             |   |                                                        |   |   |
| G0012105838220838                                                                                                                                  |                |                        | a2e2r0000006Qf6AAE | cspmb\_\_Price\_Item\_\_c | Mobile Managed MM2M 15MB Plan (FUP) x 12 months | csord\_\_Service\_\_c                 | 8960012105838220838                             |   |                                                        |   |   |
| G0012105838220812                                                                                                                                  |                |                        | a2e2r0000006Qf6AAE | cspmb\_\_Price\_Item\_\_c | Mobile Managed MM2M 15MB Plan (FUP) x 12 months | csord\_\_Service\_\_c                 | 8960012105838220812                             |   |                                                        |   |   |


## e) Billing Account should be same as basket if not same and wrong patch correct BA in CPQ

| csord\_\_Service\_\_c fields suggestions: Run Export Query Plan csord\_\_Service\_\_c Field Info<br/>Account\_\_c Account\_\_r Actual\_Delivery\_Date\_\_c Actual\_Subsidy\_Derived\_\_c Admin\_PIC\_\_c Admin\_PIC\_\_r Advanced\_FI\_Doc\_Num\_\_c Aging\_Date\_Range\_\_c Aging\_Days\_\_c API\_Status\_\_c APN\_Adr |                                            |                                            |                                                      |                       |                                  |                            |                          |   |   |   |   |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ | ------------------------------------------ | ---------------------------------------------------- | --------------------- | -------------------------------- | -------------------------- | ------------------------ | - | - | - | - |
| Export Result Copy (Excel) Copy (CSV) Copy (JSON) Delete Records Filter Result: Exported 58 records 203.3ms Stop                                                                                                                                                                                                        |                                            |                                            |                                                      |                       |                                  |                            |                          |   |   |   |   |
|                                                                                                                                                                                                                                                                                                                         | csordtelcoa\_\_Product\_Configuration\_\_c | csordtelcoa\_\_Product\_Configuration\_\_r | csordtelcoa\_\_Product\_Configuration\_\_r.Type\_\_c | Billing\_Account\_\_c | Billing\_Account\_\_r            | Billing\_Account\_\_r.Name | Commercial\_Product\_\_c |   |   |   |   |
| 16                                                                                                                                                                                                                                                                                                                      | a0xMg0000047PiXIAU                         | cscfga\_\_Product\_Configuration\_\_c      | No Change                                            | a382r000000G4H9AAK    | csconta\_\_Billing\_Account\_\_c | BA-0946542                 | a2e2r0000006OnyAAE       |   |   |   |   |
| 17                                                                                                                                                                                                                                                                                                                      | a0xMg0000047PiXIAU                         | cscfga\_\_Product\_Configuration\_\_c      | No Change                                            | a382r00000OEfHFAAQ    | csconta\_\_Billing\_Account\_\_c | BA-0612140                 | a2e2r0000006OnyAAE       |   |   |   |   |
| 18                                                                                                                                                                                                                                                                                                                      | a0xMg0000047PiXIAU                         | cscfga\_\_Product\_Configuration\_\_c      | No Change                                            | a382r000000ELUnAAO    | csconta\_\_Billing\_Account\_\_c | BA-0536110                 | a2e2r0000006OnyAAE       |   |   |   |   |
| 19                                                                                                                                                                                                                                                                                                                      | a0xMg0000047PiXIAU                         | cscfga\_\_Product\_Configuration\_\_c      | No Change                                            | a382r000000DiZkAAK    | csconta\_\_Billing\_Account\_\_c | BA-0386521                 | a2e2r0000006OnyAAE       |   |   |   |   |
| 10                                                                                                                                                                                                                                                                                                                      | a0xMg0000047PiXIAU                         | cscfga\_\_Product\_Configuration\_\_c      | No Change                                            | a382r000000DWXhAAO    | csconta\_\_Billing\_Account\_\_c | BA-0340333                 | a2e2r0000006OnyAAE       |   |   |   |   |
| 11                                                                                                                                                                                                                                                                                                                      | a0xMg0000047PiXIAU                         | cscfga\_\_Product\_Configuration\_\_c      | No Change                                            | a382r000000G5OiAAK    | csconta\_\_Billing\_Account\_\_c | BA-0950855                 | a2e2r0000006OnyAAE       |   |   |   |   |
| 12                                                                                                                                                                                                                                                                                                                      | a0xMg0000047PiXIAU                         | cscfga\_\_Product\_Configuration\_\_c      | No Change                                            | a382r000000ENmkAAG    | csconta\_\_Billing\_Account\_\_c | BA-0544911                 | a2e2r0000006OnyAAE       |   |   |   |   |
| 13                                                                                                                                                                                                                                                                                                                      | a0xMg0000047PiXIAU                         | cscfga\_\_Product\_Configuration\_\_c      | No Change                                            | a382r000000DzTxAAK    | csconta\_\_Billing\_Account\_\_c | BA-0451505                 | a2e2r0000006OnyAAE       |   |   |   |   |
| 14                                                                                                                                                                                                                                                                                                                      | a0xMg0000047PiXIAU                         | cscfga\_\_Product\_Configuration\_\_c      | No Change                                            | a382r000000EmhkAAC    | csconta\_\_Billing\_Account\_\_c | BA-0640691                 | a2e2r0000006OnyAAE       |   |   |   |   |
| 15                                                                                                                                                                                                                                                                                                                      | a0xMg0000047PiXIAU                         | cscfga\_\_Product\_Configuration\_\_c      | No Change                                            | a382r000000EAKpAAO    | csconta\_\_Billing\_Account\_\_c | BA-0493218                 | a2e2r0000006OnyAAE       |   |   |   |   |
| 3                                                                                                                                                                                                                                                                                                                       | a0xMg0000047Pk9IAE                         | cscfga\_\_Product\_Configuration\_\_c      | No Change                                            | a382r000000FwGGAAC    | csconta\_\_Billing\_Account\_\_c | BA-0915735                 | a2e2r0000006OnyAAE       |   |   |   |   |
| 4                                                                                                                                                                                                                                                                                                                       | a0xMg0000047Pk9IAE                         | cscfga\_\_Product\_Configuration\_\_c      | No Change                                            | a382r000000FnxrAAC    | csconta\_\_Billing\_Account\_\_c | BA-0883847                 | a2e2r0000006OnyAAE       |   |   |   |   |
| 1                                                                                                                                                                                                                                                                                                                       | a0xMg0000047QJdIAM                         | cscfga\_\_Product\_Configuration\_\_c      | Downgrade                                            | a382r000000Fx1GAAS    | csconta\_\_Billing\_Account\_\_c | BA-0918649                 | a2e2r0000006OnyAAE       |   |   |   |   |
| 5                                                                                                                                                                                                                                                                                                                       | a0xMg0000047Pk9IAE                         | cscfga\_\_Product\_Configuration\_\_c      | No Change                                            | a382r00000OEIJuAAO    | csconta\_\_Billing\_Account\_\_c | BA-0523908                 | a2e2r0000006OnyAAE       |   |   |   |   |
| 6                                                                                                                                                                                                                                                                                                                       | a0xMg0000047Pk9IAE                         | cscfga\_\_Product\_Configuration\_\_c      | No Change                                            | a382r000000DoTqAAK    | csconta\_\_Billing\_Account\_\_c | BA-0409219                 | a2e2r0000006OnyAAE       |   |   |   |   |


## f) SIM Serial Number and IMSI should be same as basket


---




Public

**Workbench Script: -**

g) **APN Name should be same as basket**

![Order Enrichment Editor interface showing MAC Solution with IoT Service OE, displaying billing account BA-0267368, SIM serial number 8960012201903524723, APN Name MACHINE1C, and various service details including 128K USIM TRI SIM and MAXIS GSM]

h) **Check the Contract Term, APN Name and APN Adress Type in CPQ if blank and wrong manually**

| csord\_\_Status\_\_c | csord\_\_Subscription\_\_c | Contract\_Term\_\_c | Name                                               | External\_ID\_\_c | SIM\_Serial\_Number\_\_c | IMSI\_Number\_\_c | APN\_Name\_\_c | APN\_Adress\_Type\_\_c | Commitment\_\_c    |
| -------------------- | -------------------------- | ------------------- | -------------------------------------------------- | ----------------- | ------------------------ | ----------------- | -------------- | ---------------------- | ------------------ |
| Cancelled            | a26Mg000001EA3JIAG         | 12                  | 601125785767 - Mobile Managed MM2M 15MB Plan (FUP) | 601125785767      | 8960012105838220796      | 502121583822079   |                |                        | a2e2r0000006QhkAA  |
| Cancelled            | a26Mg000001EA3.mIAG        | 12                  | SVC-013063224 - Mobile Managed MM2M 5MB Plan (FUP) | SVC-013063224     | 8960012105838220747      | 502121583822074   |                |                        | a2e2r0000006QhkAA  |
| Cancelled            | a26Mg000001EA3nIAG         | 12                  | SVC-013063225 - Mobile Managed MM2M 5MB Plan (FUP) | SVC-013063225     | 8960012105838220630      | 502121583822063   |                |                        | a2e2r0000006QhkAA  |
| Cancelled            | a26Mg000001EA3oIAG         | 12                  | SVC-013063226 - Mobile Managed MM2M 5MB Plan (FUP) | SVC-013063226     | 8960012105838220622      | 502121583822062   |                |                        | a2e2r0000006QhkAA  |
| Cancelled            | a26Mg000001EA3pIAG         | 12                  | SVC-013063227 - Mobile Managed MM2M 5MB Plan (FUP) | SVC-013063227     | 8960012105838220796      | 502121583822079   |                |                        | a2e2r0000006QhkAAl |
| Cancelled            | a26Mg000001EA3gIAG         | 12                  | SVC-013063228 - Mobile Managed MM2M 5MB Plan (FUP) | SVC-013063228     | 8960012105838220812      | 502121583822081   |                |                        | a2e2r0000006QhkAA  |
| Cancelled            | a26Mg000001EA3rIAG         | 12                  | 60126934102 - Mobile Managed MM2M 15MB Plan (FUP)  | 60126934102       | 8960011911691239927      | 502121569123992   |                |                        | a2e2r0000006QhkAA  |
| Cancelled            |                            | 12                  | 601125789545 - Mobile Managed MM2M 15MB Plan (FUP) | 601125789545      | 8960012105838220614      | 502121583822061   |                |                        | a2e2r00,00006QhkAA |
| Cancelled            | a26Mg000001EA29IAG         | 12                  | IoT Solution - MIG                                 | SVC-004640242     |                          |                   |                |                        |                    |
| Cancelled            | a26Mg000001EA2AIAW         |                     | 601125792870 - Mobile Managed MM2M 5MB Plan (FUP)  | 601125792870      | 8960012105838220747      | 502121583822074   |                |                        | a2e2r0000006Qf6AAE |
| Cancelled            | a26Mg000001EA2BIAW         |                     | 601125784893 - Mobile Managed MM2M 5MB Plan (FUP)  | 601125784893      | 8960012105838220762      | 502121583822076   |                |                        | a2e2r0000006QfAAE  |
| Cancelled            | a26Mg000001EA2CIA.W.       |                     | 601125789846 - Mobile Managed MM2M 5MB Plan (FUP)  | 601125789846      | 8960012105838220713      | 502121583822071   |                |                        | a2e2r0000006Qf6AAE |
| Cancelled            | a26Mg000001EA2DIAW         |                     | 601125791418 - Mobile Managed MM2M 5MB Plan (FUP)  | 601125791418      | 8960012105838220739      | 502121583822073   |                |                        | a2e2r0000006Qf6AAE |
| Cancelled            | a26Mg000001EA2EIAW         |                     | 601125791586 - Mobile Managed MM2M 5MB Plan (FUP)  | 601125791586      | 8960012105838220697      | 502121583822069   |                |                        | a2e2r0000006Qf6AAF |
| Cancelled            | a26Mg000001EA2FIAW         |                     | 601125789904 - Mobile Managed MM2M 5MB Plan (FUP)  | 601125789904      | 8960012105838220689      | 502121583822068   |                |                        | a2e2r0000006Qf6AAE |





---



patch as basket.

Run this script in workbench with service id and Subscription id

## Start Script: -

```
List<Id> configList = new List<Id>();
    Set<Id> configSet = new Set<Id>();
    Map<Id,csord__Service__c> serviceList = new Map<Id,csord__Service__c>();
    //Map<Id,csord__Subscription__c> subscriptionList = new Map<Id,csord__Subscription__c>();
    Map<String,List<csord__Service__c>> pcGuidToServiceMap = new
Map<String,List<csord__Service__c>>();
    Map<String,List<csord__Subscription__c>> pcGuidToSubscriptionMap = new
```


---



```
Map<String,List<csord__Subscription__c>>();
    Map<String,List<csord__Service__c>> pcIdToServiceMap = new Map<String,List<csord__Service__c>>();
    Map<String,List<csord__Subscription__c>> pcIdToSubscriptionMap = new
Map<String,List<csord__Subscription__c>>();
    Map<String,List<String>> pcIdToSimMap = new Map<String,List<String>>();
    Map<String,String> simToServiceIdMap = new Map<String,String>();
    Map<String,csord__Service__c> serviceMap = new Map<String,csord__Service__c>();
    Map<String,String> simToSubscriptionIdMap = new Map<String,String>();
    Map<String,List<String>> pcIdSolnIdToServiceIdMap = new Map<String,List<String>>();
    Map<String,List<String>> pcIdToServiceIdMap = new Map<String,List<String>>();
    Map<String,List<String>> updatedPcIdToServiceIdMap = new Map<String,List<String>>();
    Map<String,List<String>> updatedPcIdToSubscriptionIdMap = new Map<String,List<String>>();
    Map<String,List<csord__Service__c>> updatedPcIdToServiceMap = new
Map<String,List<csord__Service__c>>();
    List<csord__Service__c> serviceToUpdateLst = new List<csord__Service__c>();
    List<csord__Subscription__c> subscriptionToUpdateLst= new List<csord__Subscription__c>();
List<Id> serviceIds = new List<Id>();
List<Id> subscriptionIds = new List<Id>();
serviceIds.add('a23Mg000002dBqUIAU');
subscriptionIds.add('a26Mg000000aTEoIAM');

List<csord__Subscription__c> subscriptionLst = [SELECT
Id,csord__Identification__c,csordtelcoa__Product_Configuration__c FROM csord__Subscription__c WHERE Id
IN :subscriptionIds];
    Map<Id,csord__Subscription__c> subscriptionList = new
Map<Id,csord__Subscription__c>(subscriptionLst);
    for (csord__Service__c servRec :[SELECT Id, Name , SIM_Serial_Number__c,
```

Public



---




Public

```java
csord__Identification__c,csord__Subscription__r.Id,csord__Subscription__c,csord__Subscription__r.csord__Iden
tification__c,cssdm__solution_association__c ,cssdm__solution_association__r.Id,
                        csordtelcoa__Product_Configuration__c,
                        csordtelcoa__Product_Configuration__r.Id,
                        csordtelcoa__Product_Configuration__r.GUID__c,
                        External_ID__c,
                        csordtelcoa__Product_Configuration__r.type__c,
                        csordtelcoa__Replaced_Service__r.csord__Identification__c,
                        csordtelcoa__Replaced_Service__r.SIM_Serial_Number__c,
                        csordtelcoa__Replaced_Service__r.External_ID__c,
                        csordtelcoa__Replaced_Service__r.Id,
                        csordtelcoa__Replaced_Service__r.csordtelcoa__Product_Configuration__r.GUID__c
FROM csord__Service__c WHERE Id IN :serviceIds]){
                configSet.add(servRec.csordtelcoa__Product_Configuration__c);
                serviceList.put(servRec.Id,servRec);
                //subscriptionList.put(servRec.csord__Subscription__r.Id,servRec.csord__Subscription__c);
                String solnIdToPCGuidKey = servRec.cssdm__solution_association__r.Id + '_' +
servRec.csordtelcoa__Product_Configuration__r.GUID__c;
                simToServiceIdMap.put(servRec.csordtelcoa__Replaced_Service__r.SIM_Serial_Number__c, servRec.Id);
                serviceMap.put(servRec.Id, servRec);
                simToSubscriptionIdMap.put(servRec.csordtelcoa__Replaced_Service__r.SIM_Serial_Number__c,
servRec.csord__Subscription__r.Id);
                if(!pcGuidToServiceMap.containsKey(solnIdToPCGuidKey)){
                        pcIdToSimMap.put(servRec.csordtelcoa__Product_Configuration__r.Id, new
List<String>{servRec.csordtelcoa__Replaced_Service__r.SIM_Serial_Number__c});
                        pcGuidToServiceMap.put(solnIdToPCGuidKey,new List<csord__Service__c> {servRec});
                        pcIdToServiceMap.put(servRec.csordtelcoa__Product_Configuration__r.Id, new
```


---




Public

```java
List<csord__Service__c> {servRec});
                pcGuidToSubscriptionMap.put(solnIdToPCGuidKey,new List<csord__Subscription__c>
{subscriptionList.get(servRec.csord__Subscription__c)});
                pcIdToSubscriptionMap.put(servRec.csordtelcoa__Product_Configuration__r.Id, new
List<csord__Subscription__c> {subscriptionList.get(servRec.csord__Subscription__c)});
            }
            else {
pcIdToSimMap.get(servRec.csordtelcoa__Product_Configuration__r.Id).add(servRec.csordtelcoa__Replaced_Se
rvice__r.SIM_Serial_Number__c);
                pcGuidToServiceMap.get(solnIdToPCGuidKey).add(servRec);
                pcIdToServiceMap.get(servRec.csordtelcoa__Product_Configuration__r.Id).add(servRec);
pcGuidToSubscriptionMap.get(solnIdToPCGuidKey).add(subscriptionList.get(servRec.csord__Subscription__c)
);
pcIdToSubscriptionMap.get(servRec.csordtelcoa__Product_Configuration__r.Id).add(subscriptionList.get(serv
Rec.csord__Subscription__c));
            }
        }
        configList.addAll(configSet);
        if(configList.size()>0){
            List<cscfga__Product_Configuration__c> updateConfigStatus = new
List<cscfga__Product_Configuration__c>();
            Map<Id, List<cssmgnt.ProductProcessingUtility.Component>> resMap =
cssmgnt.API_1.getOEData(configList);
            System.debug('<><><>Response for OE Data ::'+resMap);
            //if(attNames.size()>0){
            System.Debug('Configs Lists '+resMap.values());
            List <cssmgnt.ProductProcessingUtility.Component> compList;
```


---



```
List<cssmgnt.ProductProcessingUtility.Component> existingcompList;
List<cssmgnt.ProductProcessingUtility.Configuration> configListToDelete;

Map<Id, List<cssmgnt.ProductProcessingUtility.Component>> oeMap = new Map<Id,
List<cssmgnt.ProductProcessingUtility.Component>>();
    for(Id config: configList){
        compList = new List <cssmgnt.ProductProcessingUtility.Component> ();
        if(resMap.get(config) != null){
        for (cssmgnt.ProductProcessingUtility.Component component : resMap.get(config)) { //loop through
every "component" in this configuration
            //configListToDelete = new List<cssmgnt.ProductProcessingUtility.Configuration>();
            if(component.configurations.size()>0){
            for(cssmgnt.ProductProcessingUtility.Configuration configuration : component.configurations)
{ //loop through every configuration
                System.debug('<><><><>configuration ::'+configuration);
                String ICCId;
                String commercialConfigurationId;
                String otherDetailsStr = configuration.other;
                System.debug('<><><><>otherDetailsStr ::'+otherDetailsStr);
                Map<String, Object> otherDetails = (Map<String, Object>)
JSON.deserializeUntyped(otherDetailsStr);
                if (otherDetails.containsKey('dbDetails')) {
                    Map<String, Object> dbDetailsMap = (Map<String, Object>) otherDetails.get('dbDetails');
                    if (dbDetailsMap.containsKey('commercialConfigurationId')) {
                        commercialConfigurationId = (String) dbDetailsMap.get('commercialConfigurationId');
                        System.debug('<><><><>commercialConfigurationId ::'+commercialConfigurationId);
                    }
```

Public


---




Public

```java
               }
               for(Object attributeObj : configuration.attributes){
                cssmgnt.ProductProcessingUtility.Attribute attribute =
(cssmgnt.ProductProcessingUtility.Attribute)attributeObj;
                if(attribute.name == 'ICCID' && (attribute.value != '' && attribute.value != 'undefined')){
                 ICCId = attribute.value;
                }
               }
               if(!pcIdSolnIdToServiceIdMap.containsKey(commercialConfigurationId)){
                pcIdToServiceIdMap.put(config, new List<String>{ICCId});
                pcIdSolnIdToServiceIdMap.put(commercialConfigurationId,new List<String>{ICCId});
               }
               else {
                pcIdToServiceIdMap.get(config).add(ICCId);
                pcIdSolnIdToServiceIdMap.get(commercialConfigurationId).add(ICCId);
               }
       }       }
   }
   }} }
System.debug('<><><> pcIdToServiceIdMap Heroku::'+pcIdToServiceIdMap);
 System.debug('<><><> pcIdToSubscriptionMap Salesforce::'+pcIdToSubscriptionMap);
 System.debug('<><><> pcGuidToServiceMap Salesforce::'+pcGuidToServiceMap);
 for(String pcId : pcIdToServiceIdMap.keyset()){
  List<String> herokuValues = pcIdToServiceIdMap.get(pcId);
  List<String> salesforceValues = pcIdToSimMap.containsKey(pcId) ? pcIdToSimMap.get(pcId) : new
List<String>();
  for (String value : herokuValues) {
```


---



| After<br>script<br>running | String servId = simToServiceIdMap.get(value);<br>String subscriptionId = simToSubscriptionIdMap.get(value);<br>csord__Service__c servRec = serviceMap.get(value);<br>if(!updatedPcIdToServiceIdMap.containsKey(pcId)){<br>  updatedPcIdToServiceIdMap.put(pcId,new List<String>{servId});<br>  updatedPcIdToServiceMap.put(pcId,new List<csord__Service__c>{servRec});<br>  updatedPcIdToSubscriptionIdMap.put(pcId,new List<String>{subscriptionId});<br>}<br>else {<br>  updatedPcIdToServiceIdMap.get(pcId).add(servId);<br>  updatedPcIdToServiceMap.get(pcId).add(servRec);<br>  updatedPcIdToSubscriptionIdMap.get(pcId).add(subscriptionId);<br>} }    }<br>System.debug('<><><> updatedPcIdToServiceIdMap Salesforce::'+updatedPcIdToServiceIdMap);<br>System.debug('<><><> updatedPcIdToSubscriptionIdMap Salesforce::'+updatedPcIdToSubscriptionIdMap);<br>for(String prodConfigId : updatedPcIdToServiceIdMap.keyset()){<br>  List<String> correctedServiceIdLst = updatedPcIdToServiceIdMap.get(prodConfigId);<br>  for(String serviceId : correctedServiceIdLst){<br>    if(serviceMap.containsKey(serviceId) &&<br>serviceMap.get(serviceId).csordtelcoa__Product_Configuration__c != prodConfigId){<br>      csord__Service__c updateServicePcId = new csord__Service__c(Id=serviceId,<br>csordtelcoa__Product_Configuration__c = prodConfigId);<br>      csord__Subscription__c updateSubscriptionPcId = new<br>csord__Subscription__c(Id=serviceMap.get(serviceId).csord__Subscription__c,<br>csordtelcoa__Product_Configuration__c = prodConfigId);<br>      serviceToUpdateLst.add(updateServicePcId);<br>      subscriptionToUpdateLst.add(updateSubscriptionPcId); |
|---|---|

Public



---



```
} } }
if(!serviceToUpdateLst.isEmpty() && serviceToUpdateLst.size() > 0){
    update serviceToUpdateLst;
        System.debug('YJW serviceToUpdateLst ' + serviceToUpdateLst);
}
if(!subscriptionToUpdateLst.isEmpty() && subscriptionToUpdateLst.size() > 0){
    update subscriptionToUpdateLst;
        System.debug('YJW subscriptionToUpdateLst ' + subscriptionToUpdateLst);
}
```

**END Script**

**Mark Onhold checkbox = false of Orchestration Process: -**

Public



---




| Related                | Details                           |                                |                               |
| ---------------------- | --------------------------------- | ------------------------------ | ----------------------------- |
| Name                   | a1dMg000007vsm1                   | Orchestration Process Template | Order Fulfillment Process IOT |
| Type                   |                                   | Processing Mode                | Background                    |
| On Hold                |                                   | Order                          | ODR-ON01644352                |
| Priority               | 2 - Normal                        | Service                        |                               |
| Currency               | MYR - Malaysian Ringgit           | Deliverable                    |                               |
| Service Request        |                                   | Case                           |                               |
| Aging Date Range       | 0 days                            | Solution                       |                               |
| **OLA Details**        |                                   |                                |                               |
| In Jeopardy            |                                   | Target Date                    |                               |
|                        |                                   | Target Time                    |                               |
| **Evaluation Details** |                                   |                                |                               |
| Status                 | Complete                          | Confirmed Date                 |                               |
| State                  | TERMINATED                        | Actual Date                    | 06/08/2025                    |
| **Related Objects**    |                                   |                                |                               |
| Account                |                                   | Opportunity                    |                               |
| **System Information** |                                   |                                |                               |
| Created By             | CS Batch Engine, 06/08/2025 09:44 | Owner                          | CS Batch Engine               |


Also check the process visualizer to see if there are any step stuck and errors

**a1dMg000007vsm1**

COMPLETE · Created 4 hours ago

Auto layout | Fit layout | Restore layout | Show dependency logic | Save layout

Highlight steps

| Condition<br/>Evented Monitor Field<br/>Order Decomposed | Monitor Field<br/>Condition<br/>True | IOTCaseCreation<br/>IOT Case NRC Creation<br/>Blocked | Monitor Field<br/>Blocked | Update Field<br/>Blocked | Condition<br/>Complete | Condition<br/>Blocked | Subprocess<br/>Subprocess<br/>Blocked | Evented<br/>Blocked | Blocked |
| -------------------------------------------------------- | ------------------------------------ | ----------------------------------------------------- | ------------------------- | ------------------------ | ---------------------- | --------------------- | ------------------------------------- | ------------------- | ------- |



(available-indices)=
# Available Climate Indices

The following indices are available, categorized by the defining distribution.



## clix-meta (0.6.1)

(idx-fd)=
### fd
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of Frost Days (Tmin < 0C)    |
| Reference      | ETCCDI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | 0 degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | < |
:::


(idx-tnlt2)=
### tnlt2
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of weak Frost Days (Tmin < +2C)    |
| Reference      | ET-SCI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | 2 degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | < |
:::


(idx-tnltm2)=
### tnltm2
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of sharp Frost Days (Tmin < -2C)    |
| Reference      | ET-SCI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | -2 degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | < |
:::


(idx-tnltm20)=
### tnltm20
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | None    |
| Reference      | ET-SCI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | -20 degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | < |
:::


(idx-id)=
### id
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of sharp Ice Days (Tmax < 0C)    |
| Reference      | ETCCDI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | 0 degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | < |
:::


(idx-su)=
### su
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of Summer Days (Tmax > 25C)    |
| Reference      | ETCCDI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | 25 degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | > |
:::


(idx-txge30)=
### txge30
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of Hot Days (Tmax >= 35C)    |
| Reference      | ET-SCI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | 30 degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | >= |
:::


(idx-txge35)=
### txge35
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of Very Hot Days (Tmax >= 35C)    |
| Reference      | ET-SCI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | 35 degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | >= |
:::


(idx-tr)=
### tr
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of Tropical Nights (Tmin > 20C)    |
| Reference      | ETCCDI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | 20 degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | > |
:::


(idx-tmge5)=
### tmge5
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of days with Tmean >= 5C    |
| Reference      | ET-SCI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | 5 degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | >= |
:::


(idx-tmlt5)=
### tmlt5
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of days with Tmean < 5C    |
| Reference      | ET-SCI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | 5 degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | < |
:::


(idx-tmge10)=
### tmge10
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of days with Tmean >= 10C    |
| Reference      | ET-SCI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | 10 degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | >= |
:::


(idx-tmlt10)=
### tmlt10
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of days with Tmean < 10C    |
| Reference      | ET-SCI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | 10 degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | < |
:::


(idx-tngt{TT})=
### tngt{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of days with Tmin > {TT}C    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | > |
:::


(idx-tnlt{TT})=
### tnlt{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of days with Tmin < {TT}C    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | < |
:::


(idx-tnge{TT})=
### tnge{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of days with Tmin >= {TT}C    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | >= |
:::


(idx-tnle{TT})=
### tnle{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of days with Tmin <= {TT}C    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | <= |
:::


(idx-txgt{TT})=
### txgt{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of days with Tmax > {TT}C    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | > |
:::


(idx-txlt{TT})=
### txlt{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of days with Tmax < {TT}C    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | < |
:::


(idx-txge{TT})=
### txge{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of days with Tmax >= {TT}C    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | >= |
:::


(idx-txle{TT})=
### txle{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of days with Tmax <= {TT}C    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | <= |
:::


(idx-tmgt{TT})=
### tmgt{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of days with Tmean > {TT}C    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | > |
:::


(idx-tmlt{TT})=
### tmlt{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of days with Tmean < {TT}C    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | < |
:::


(idx-tmge{TT})=
### tmge{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of days with Tmean >= {TT}C    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | >= |
:::


(idx-tmle{TT})=
### tmle{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of days with Tmean <= {TT}C    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | <= |
:::


(idx-ctngt{TT})=
### ctngt{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum number of consecutive days with Tmin > {TT}C    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | spell_length |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | > |
| *statistic* |                  |
| kind         | reducer |
| reducer | max |
:::


(idx-cfd)=
### cfd
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum number of consecutive frost days (Tmin < 0 C)    |
| Reference      | ECA&D           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | spell_length |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | 0 degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | < |
| *statistic* |                  |
| kind         | reducer |
| reducer | max |
:::


(idx-csu)=
### csu
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum number of consecutive summer days (Tmax >25 C)    |
| Reference      | ECA&D           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | spell_length |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | 25 degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | > |
| *statistic* |                  |
| kind         | reducer |
| reducer | max |
:::


(idx-ctnlt{TT})=
### ctnlt{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum number of consecutive days with Tmin < {TT}C    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | spell_length |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | < |
| *statistic* |                  |
| kind         | reducer |
| reducer | max |
:::


(idx-ctnge{TT})=
### ctnge{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum number of consecutive days with Tmin >= {TT}C    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | spell_length |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | >= |
| *statistic* |                  |
| kind         | reducer |
| reducer | max |
:::


(idx-ctnle{TT})=
### ctnle{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum number of consecutive days with Tmin <= {TT}C    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | spell_length |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | <= |
| *statistic* |                  |
| kind         | reducer |
| reducer | max |
:::


(idx-ctxgt{TT})=
### ctxgt{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum number of consecutive days with Tmax > {TT}C    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | spell_length |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | > |
| *statistic* |                  |
| kind         | reducer |
| reducer | max |
:::


(idx-ctxlt{TT})=
### ctxlt{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum number of consecutive days with Tmax < {TT}C    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | spell_length |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | < |
| *statistic* |                  |
| kind         | reducer |
| reducer | max |
:::


(idx-ctxge{TT})=
### ctxge{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum number of consecutive days with Tmax >= {TT}C    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | spell_length |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | >= |
| *statistic* |                  |
| kind         | reducer |
| reducer | max |
:::


(idx-ctxle{TT})=
### ctxle{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum number of consecutive days with Tmax <= {TT}C    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | spell_length |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | <= |
| *statistic* |                  |
| kind         | reducer |
| reducer | max |
:::


(idx-ctmgt{TT})=
### ctmgt{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum number of consecutive days with Tmean > {TT}C    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | spell_length |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | > |
| *statistic* |                  |
| kind         | reducer |
| reducer | max |
:::


(idx-ctmlt{TT})=
### ctmlt{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum number of consecutive days with Tmean < {TT}C    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | spell_length |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | < |
| *statistic* |                  |
| kind         | reducer |
| reducer | max |
:::


(idx-ctmge{TT})=
### ctmge{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum number of consecutive days with Tmean >= {TT}C    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | spell_length |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | >= |
| *statistic* |                  |
| kind         | reducer |
| reducer | max |
:::


(idx-ctmle{TT})=
### ctmle{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum number of consecutive days with Tmean <= {TT}C    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | spell_length |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | <= |
| *statistic* |                  |
| kind         | reducer |
| reducer | max |
:::


(idx-txx)=
### txx
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum daily maximum temperature    |
| Reference      | ETCCDI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | max |
:::


(idx-tnx)=
### tnx
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum daily minimum temperature    |
| Reference      | ETCCDI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | max |
:::


(idx-txn)=
### txn
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Minimum daily maximum temperature    |
| Reference      | ETCCDI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | min |
:::


(idx-tnn)=
### tnn
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Minimum daily minimum temperature    |
| Reference      | ETCCDI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | min |
:::


(idx-txm)=
### txm
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Mean daily maximum temperature    |
| Reference      | ET-SCI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | mean |
:::


(idx-tnm)=
### tnm
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Mean daily minimum temperature    |
| Reference      | ET-SCI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | mean |
:::


(idx-tmx)=
### tmx
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum daily mean temperature    |
| Reference      | ET-SCI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | max |
:::


(idx-tmn)=
### tmn
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Minimum daily mean temperature    |
| Reference      | ET-SCI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | min |
:::


(idx-tmm)=
### tmm
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Mean daily mean temperature    |
| Reference      | ET-SCI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | mean |
:::


(idx-txmax)=
### txmax
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum daily maximum temperature    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | max |
:::


(idx-tnmax)=
### tnmax
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum daily minimum temperature    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | max |
:::


(idx-txmin)=
### txmin
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Minimum daily maximum temperature    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | min |
:::


(idx-tnmin)=
### tnmin
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Minimum daily minimum temperature    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | min |
:::


(idx-txmean)=
### txmean
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Mean daily maximum temperature    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | mean |
:::


(idx-tnmean)=
### tnmean
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Mean daily minimum temperature    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | mean |
:::


(idx-tmmax)=
### tmmax
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum daily mean temperature    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | max |
:::


(idx-tmmin)=
### tmmin
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Minimum daily mean temperature    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | min |
:::


(idx-tmmean)=
### tmmean
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Mean daily mean temperature    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | mean |
:::

<!---
(idx-wsdi)=
### wsdi
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Warm Spell Duration Index, count of days with at least 6 consecutive days when Tmax > 90th percentile    |
| Reference      | ETCCDI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_spell_duration |
| *spell_threshold* |                  |
| kind         | quantity |
| long name | Minimum spell duration |
| var_name | spell_threshold |
| standard_name | None |
| proposed_standard_name | None |
| value | 6 days|
| *spell_condition* |                  |
| kind         | operator |
| operator | >= |
| *percentile* |                  |
| kind         | quantity |
| long name | None |
| var_name | percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | 90 %|
| *percentile_condition* |                  |
| kind         | operator |
| operator | > |
| *reference_period* |                  |
| kind         | time_range |
| data | 1961/1990 |
:::


(idx-wsdi{ND})=
### wsdi{ND}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | User-defined Warm Spell Duration Index, count of days with at least {ND} consecutive days when Tmax > 90th percentile    |
| Reference      | ET-SCI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_spell_duration |
| *spell_threshold* |                  |
| kind         | quantity |
| long name | Minimum spell duration |
| var_name | spell_threshold |
| standard_name | None |
| proposed_standard_name | None |
| value | {ND} days|
| *spell_condition* |                  |
| kind         | operator |
| operator | >= |
| *percentile* |                  |
| kind         | quantity |
| long name | None |
| var_name | percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | 90 %|
| *percentile_condition* |                  |
| kind         | operator |
| operator | > |
| *reference_period* |                  |
| kind         | time_range |
| data | 1961/1990 |
:::


(idx-csdi)=
### csdi
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Cold Spell Duration Index, count of days with at least 6 consecutive days when Tmin < 10th percentile    |
| Reference      | ETCCDI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_spell_duration |
| *spell_threshold* |                  |
| kind         | quantity |
| long name | Minimum spell duration |
| var_name | spell_threshold |
| standard_name | None |
| proposed_standard_name | None |
| value | 6 days|
| *spell_condition* |                  |
| kind         | operator |
| operator | >= |
| *percentile* |                  |
| kind         | quantity |
| long name | None |
| var_name | percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | 10 %|
| *percentile_condition* |                  |
| kind         | operator |
| operator | < |
| *reference_period* |                  |
| kind         | time_range |
| data | 1961/1990 |
:::


(idx-csdi{ND})=
### csdi{ND}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | User-defined Cold Spell Duration Index, count of days with at least # consecutive days when Tmin < 10th percentile    |
| Reference      | ET-SCI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_spell_duration |
| *spell_threshold* |                  |
| kind         | quantity |
| long name | Minimum spell duration |
| var_name | spell_threshold |
| standard_name | None |
| proposed_standard_name | None |
| value | {ND} days|
| *spell_condition* |                  |
| kind         | operator |
| operator | >= |
| *percentile* |                  |
| kind         | quantity |
| long name | None |
| var_name | percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | 10 %|
| *percentile_condition* |                  |
| kind         | operator |
| operator | < |
| *reference_period* |                  |
| kind         | time_range |
| data | 1961/1990 |
:::

--->

(idx-tn10p)=
### tn10p
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Percentage of days when Tmin < 10th percentile    |
| Reference      | ETCCDI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_percentile_occurrences |
| *percentile* |                  |
| kind         | quantity |
| long name | None |
| var_name | percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | 10 %|
| *condition* |                  |
| kind         | operator |
| operator | < |
| *reference_period* |                  |
| kind         | time_range |
| data | 1961/1990 |
:::


(idx-tx10p)=
### tx10p
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Percentage of days when Tmax < 10th percentile    |
| Reference      | ETCCDI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_percentile_occurrences |
| *percentile* |                  |
| kind         | quantity |
| long name | None |
| var_name | percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | 10 %|
| *condition* |                  |
| kind         | operator |
| operator | < |
| *reference_period* |                  |
| kind         | time_range |
| data | 1961/1990 |
:::


(idx-tn90p)=
### tn90p
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Percentage of days when Tmin > 90th percentile    |
| Reference      | ETCCDI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_percentile_occurrences |
| *percentile* |                  |
| kind         | quantity |
| long name | None |
| var_name | percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | 90 %|
| *condition* |                  |
| kind         | operator |
| operator | > |
| *reference_period* |                  |
| kind         | time_range |
| data | 1961/1990 |
:::


(idx-tx90p)=
### tx90p
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Percentage of days when Tmax > 90th percentile    |
| Reference      | ETCCDI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_percentile_occurrences |
| *percentile* |                  |
| kind         | quantity |
| long name | None |
| var_name | percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | 90 %|
| *condition* |                  |
| kind         | operator |
| operator | > |
| *reference_period* |                  |
| kind         | time_range |
| data | 1961/1990 |
:::


(idx-tg10p)=
### tg10p
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Percentage of days when Tmean < 10th percentile    |
| Reference      | ECA&D           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_percentile_occurrences |
| *percentile* |                  |
| kind         | quantity |
| long name | None |
| var_name | percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | 10 %|
| *condition* |                  |
| kind         | operator |
| operator | < |
| *reference_period* |                  |
| kind         | time_range |
| data | 1961/1990 |
:::


(idx-tg90p)=
### tg90p
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Percentage of days when Tmean > 90th percentile    |
| Reference      | ECA&D           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_percentile_occurrences |
| *percentile* |                  |
| kind         | quantity |
| long name | None |
| var_name | percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | 90 %|
| *condition* |                  |
| kind         | operator |
| operator | > |
| *reference_period* |                  |
| kind         | time_range |
| data | 1961/1990 |
:::


(idx-txgt50p)=
### txgt50p
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Percentage of days when Tmax > 50th percentile    |
| Reference      | ET-SCI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_percentile_occurrences |
| *percentile* |                  |
| kind         | quantity |
| long name | None |
| var_name | percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | 50 %|
| *condition* |                  |
| kind         | operator |
| operator | > |
| *reference_period* |                  |
| kind         | time_range |
| data | 1961/1990 |
:::


(idx-txgt{PRC}p)=
### txgt{PRC}p
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Percentage of days when Tmax > {PRC}th percentile    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_percentile_occurrences |
| *percentile* |                  |
| kind         | quantity |
| long name | None |
| var_name | percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | {PRC} %|
| *condition* |                  |
| kind         | operator |
| operator | > |
| *reference_period* |                  |
| kind         | time_range |
| data | 1961/1990 |
:::


(idx-tngt{PRC}p)=
### tngt{PRC}p
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Percentage of days when Tmin > {PRC}th percentile    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_percentile_occurrences |
| *percentile* |                  |
| kind         | quantity |
| long name | None |
| var_name | percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | {PRC} %|
| *condition* |                  |
| kind         | operator |
| operator | > |
| *reference_period* |                  |
| kind         | time_range |
| data | 1961/1990 |
:::


(idx-tmgt{PRC}p)=
### tmgt{PRC}p
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Percentage of days when Tmean > {PRC}th percentile    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_percentile_occurrences |
| *percentile* |                  |
| kind         | quantity |
| long name | None |
| var_name | percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | {PRC} %|
| *condition* |                  |
| kind         | operator |
| operator | > |
| *reference_period* |                  |
| kind         | time_range |
| data | 1961/1990 |
:::


(idx-txlt{PRC}p)=
### txlt{PRC}p
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Percentage of days when Tmax < {PRC}th percentile    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_percentile_occurrences |
| *percentile* |                  |
| kind         | quantity |
| long name | None |
| var_name | percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | {PRC} %|
| *condition* |                  |
| kind         | operator |
| operator | < |
| *reference_period* |                  |
| kind         | time_range |
| data | 1961/1990 |
:::


(idx-tnlt{PRC}p)=
### tnlt{PRC}p
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Percentage of days when Tmin < {PRC}th percentile    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_percentile_occurrences |
| *percentile* |                  |
| kind         | quantity |
| long name | None |
| var_name | percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | {PRC} %|
| *condition* |                  |
| kind         | operator |
| operator | < |
| *reference_period* |                  |
| kind         | time_range |
| data | 1961/1990 |
:::


(idx-tmlt{PRC}p)=
### tmlt{PRC}p
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Percentage of days when Tmean < {PRC}th percentile    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_percentile_occurrences |
| *percentile* |                  |
| kind         | quantity |
| long name | None |
| var_name | percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | {PRC} %|
| *condition* |                  |
| kind         | operator |
| operator | < |
| *reference_period* |                  |
| kind         | time_range |
| data | 1961/1990 |
:::


(idx-dtr)=
### dtr
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Mean Diurnal Temperature Range    |
| Reference      | ETCCDI           |
| Default period | monthly      |
| **Input**      |                                      |
| low_data | tasmin |
| high_data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | diurnal_temperature_range |
| *statistic* |                  |
| kind         | reducer |
| reducer | mean |
:::


(idx-vdtr)=
### vdtr
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Mean day-to-day variation in Diurnal Temperature Range    |
| Reference      | ECA&D           |
| Default period | monthly      |
| **Input**      |                                      |
| low_data | tasmin |
| high_data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | interday_diurnal_temperature_range |
:::


(idx-etr)=
### etr
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Intra-period extreme temperature range    |
| Reference      | ECA&D           |
| Default period | monthly      |
| **Input**      |                                      |
| low_data | tasmin |
| high_data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | extreme_temperature_range |
:::


(idx-tx{PRC}pctl)=
### tx{PRC}pctl
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | {PRC}th percentile of Tmax    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | percentile |
| *percentiles* |                  |
| kind         | quantity |
| long name | None |
| var_name | percentiles |
| standard_name | None |
| proposed_standard_name | quantile |
| value | {PRC} %|
:::


(idx-tn{PRC}pctl)=
### tn{PRC}pctl
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | {PRC}th percentile of Tmin    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | percentile |
| *percentiles* |                  |
| kind         | quantity |
| long name | None |
| var_name | percentiles |
| standard_name | None |
| proposed_standard_name | quantile |
| value | {PRC} %|
:::


(idx-tm{PRC}pctl)=
### tm{PRC}pctl
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | {PRC}th percentile of Tmean    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | percentile |
| *percentiles* |                  |
| kind         | quantity |
| long name | None |
| var_name | percentiles |
| standard_name | None |
| proposed_standard_name | quantile |
| value | {PRC} %|
:::


(idx-hd17)=
### hd17
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Heating degree days (sum of 17C – Tmean, for days when Tmean < 17C)    |
| Reference      | ECA&D           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | temperature_sum |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | 17 degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | < |
:::


(idx-hddheat{TT})=
### hddheat{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Heating Degree Days (sum of {TT}C  - Tmean, for days when Tmean < {TT}C )    |
| Reference      | ET-SCI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | temperature_sum |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | < |
:::


(idx-ddgt{TT})=
### ddgt{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Degree Days above threshold {TT}C    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | temperature_sum |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | > |
:::


(idx-cddcold{TT})=
### cddcold{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Cooling Degree Days (sum of Tmean – {TT}C, for days when Tmean > {TT}C)    |
| Reference      | ET-SCI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | temperature_sum |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | > |
:::


(idx-ddlt{TT})=
### ddlt{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Degree Days below threshold {TT}C    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | temperature_sum |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | < |
:::


(idx-gddgrow{TT})=
### gddgrow{TT}
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Annual Growing Degree Days (sum of Tmean – {TT}C, for days when Tmean > {TT}C)    |
| Reference      | ET-SCI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | temperature_sum |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | {TT} degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | > |
:::


(idx-gd4)=
### gd4
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Growing degree days (sum of Tmean – 4C, for days when Tmean > 4C)    |
| Reference      | ECA&D           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | temperature_sum |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | 4 degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | > |
:::


(idx-gsl)=
### gsl
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | ETCCDI Growing Season Length (Tmean > 5C)    |
| Reference      | ETCCDI           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | season_length |
| *start_duration* |                  |
| kind         | quantity |
| long name | Spell duration for initiating the growing season |
| var_name | start_duration |
| standard_name | None |
| proposed_standard_name | None |
| value | 6 days|
| *start_threshold* |                  |
| kind         | quantity |
| long name | Temperature threshold for initiating the growing season |
| var_name | start_threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | 5 degree_Celsius|
| *start_condition* |                  |
| kind         | operator |
| operator | > |
| *start_delay* |                  |
| kind         | quantity |
| long name | None |
| var_name | start_delay |
| standard_name | None |
| proposed_standard_name | None |
| value | 0 days|
| *end_duration* |                  |
| kind         | quantity |
| long name | Spell duration for ending the growing season |
| var_name | end_duration |
| standard_name | None |
| proposed_standard_name | None |
| value | 6 days|
| *end_threshold* |                  |
| kind         | quantity |
| long name | Temperature threshold for ending the growing season |
| var_name | end_threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | 5 degree_Celsius|
| *end_condition* |                  |
| kind         | operator |
| operator | < |
| *end_delay* |                  |
| kind         | quantity |
| long name | None |
| var_name | end_delay |
| standard_name | None |
| proposed_standard_name | None |
| value | 182 days|
:::


(idx-gsstart)=
### gsstart
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Start of ETCCDI Growing Season (6 days with Tmean > 5C)    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | season_start |
| *threshold* |                  |
| kind         | quantity |
| long name | Temperature threshold for initiating the growing season |
| var_name | start_threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | 5 degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | > |
| *duration* |                  |
| kind         | quantity |
| long name | Spell duration for initiating the growing season |
| var_name | start_duration |
| standard_name | None |
| proposed_standard_name | None |
| value | 6 days|
| *delay* |                  |
| kind         | quantity |
| long name | None |
| var_name | start_delay |
| standard_name | None |
| proposed_standard_name | None |
| value | 0 days|
:::


(idx-gsend)=
### gsend
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | End of ETCCDI Growing Season (6 days with Tmean < 5C)    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | season_end |
| *start_duration* |                  |
| kind         | quantity |
| long name | Spell duration for initiating the growing season |
| var_name | start_duration |
| standard_name | None |
| proposed_standard_name | None |
| value | 6 days|
| *start_threshold* |                  |
| kind         | quantity |
| long name | Temperature threshold for initiating the growing season |
| var_name | start_threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | 5 degree_Celsius|
| *start_condition* |                  |
| kind         | operator |
| operator | > |
| *start_delay* |                  |
| kind         | quantity |
| long name | None |
| var_name | start_delay |
| standard_name | None |
| proposed_standard_name | None |
| value | 0 days|
| *end_duration* |                  |
| kind         | quantity |
| long name | Spell duration for ending the growing season |
| var_name | end_duration |
| standard_name | None |
| proposed_standard_name | None |
| value | 6 days|
| *end_threshold* |                  |
| kind         | quantity |
| long name | Temperature threshold for ending the growing season |
| var_name | end_threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | 5 degree_Celsius|
| *end_condition* |                  |
| kind         | operator |
| operator | < |
| *end_delay* |                  |
| kind         | quantity |
| long name | None |
| var_name | end_delay |
| standard_name | None |
| proposed_standard_name | None |
| value | 182 days|
:::


(idx-r10mm)=
### r10mm
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of heavy precipitation days (Precip >=10mm)    |
| Reference      | ETCCDI           |
| Default period | annual      |
| **Input**      |                                      |
| data | pr |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | lwe_precipitation_rate |
| proposed_standard_name | None |
| value | 10 mm day-1|
| *condition* |                  |
| kind         | operator |
| operator | >= |
:::


(idx-r20mm)=
### r20mm
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of very heavy precipitation days (Precip >= 20mm)    |
| Reference      | ETCCDI           |
| Default period | annual      |
| **Input**      |                                      |
| data | pr |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | lwe_precipitation_rate |
| proposed_standard_name | None |
| value | 20 mm day-1|
| *condition* |                  |
| kind         | operator |
| operator | >= |
:::


(idx-r{RT}mm)=
### r{RT}mm
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of days with daily Precip >= {RT}mm)    |
| Reference      | ETCCDI           |
| Default period | annual      |
| **Input**      |                                      |
| data | pr |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | lwe_precipitation_rate |
| proposed_standard_name | None |
| value | {RT} mm day-1|
| *condition* |                  |
| kind         | operator |
| operator | >= |
:::


(idx-wetdays)=
### wetdays
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of Wet Days (precip >= 1 mm)    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | pr |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | Wet day threshold |
| var_name | threshold |
| standard_name | lwe_precipitation_rate |
| proposed_standard_name | None |
| value | 1 mm day-1|
| *condition* |                  |
| kind         | operator |
| operator | >= |
:::


(idx-rr1)=
### rr1
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of Wet Days (precip >= 1 mm)    |
| Reference      | ECA&D           |
| Default period | annual      |
| **Input**      |                                      |
| data | pr |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | Wet day threshold |
| var_name | threshold |
| standard_name | lwe_precipitation_rate |
| proposed_standard_name | None |
| value | 1 mm day-1|
| *condition* |                  |
| kind         | operator |
| operator | >= |
:::


(idx-cdd)=
### cdd
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum consecutive dry days (Precip < 1mm)    |
| Reference      | ETCCDI           |
| Default period | annual      |
| **Input**      |                                      |
| data | pr |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | spell_length |
| *threshold* |                  |
| kind         | quantity |
| long name | Wet day threshold |
| var_name | threshold |
| standard_name | lwe_precipitation_rate |
| proposed_standard_name | None |
| value | 1 mm day-1|
| *condition* |                  |
| kind         | operator |
| operator | < |
| *statistic* |                  |
| kind         | reducer |
| reducer | max |
:::


(idx-cwd)=
### cwd
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum consecutive wet days (Precip >= 1mm)    |
| Reference      | ETCCDI           |
| Default period | annual      |
| **Input**      |                                      |
| data | pr |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | spell_length |
| *threshold* |                  |
| kind         | quantity |
| long name | Wet day threshold |
| var_name | threshold |
| standard_name | lwe_precipitation_rate |
| proposed_standard_name | None |
| value | 1 mm day-1|
| *condition* |                  |
| kind         | operator |
| operator | >= |
| *statistic* |                  |
| kind         | reducer |
| reducer | max |
:::


(idx-prcptot)=
### prcptot
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Total precipitation during Wet Days    |
| Reference      | ETCCDI           |
| Default period | annual      |
| **Input**      |                                      |
| data | pr |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | thresholded_statistics |
| *threshold* |                  |
| kind         | quantity |
| long name | Wet day threshold |
| var_name | threshold |
| standard_name | lwe_precipitation_rate |
| proposed_standard_name | None |
| value | 1 mm day-1|
| *condition* |                  |
| kind         | operator |
| operator | >= |
| *statistic* |                  |
| kind         | reducer |
| reducer | sum |
:::


(idx-sdii)=
### sdii
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Average precipitation during Wet Days (SDII)    |
| Reference      | ETCCDI           |
| Default period | annual      |
| **Input**      |                                      |
| data | pr |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | thresholded_statistics |
| *threshold* |                  |
| kind         | quantity |
| long name | Wet day threshold |
| var_name | threshold |
| standard_name | lwe_precipitation_rate |
| proposed_standard_name | None |
| value | 1 mm day-1|
| *condition* |                  |
| kind         | operator |
| operator | >= |
| *statistic* |                  |
| kind         | reducer |
| reducer | mean |
:::


(idx-r{PRC}pctl)=
### r{PRC}pctl
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | {PRC}th percentile of precipitation during wet days (Precip >= 1mm)    |
| Reference      | CLIPC           |
| Default period | annual      |
| **Input**      |                                      |
| data | pr |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | thresholded_percentile |
| *threshold* |                  |
| kind         | quantity |
| long name | Wet day threshold |
| var_name | threshold |
| standard_name | lwe_precipitation_rate |
| proposed_standard_name | None |
| value | 1 mm day-1|
| *condition* |                  |
| kind         | operator |
| operator | >= |
| *percentiles* |                  |
| kind         | quantity |
| long name | None |
| var_name | percentiles |
| standard_name | None |
| proposed_standard_name | quantile |
| value | {PRC} %|
:::


(idx-r{PRC}pSUM)=
### r{PRC}pSUM
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Total precipitation amount from days above the {PRC}th percentile    |
| Reference      | 2022 Ad hoc group           |
| Default period | annual      |
| **Input**      |                                      |
| data | pr |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_thresholded_percentile_occurrences |
| *data_threshold* |                  |
| kind         | quantity |
| long name | Wet day threshold |
| var_name | data_threshold |
| standard_name | lwe_precipitation_rate |
| proposed_standard_name | None |
| value | 1 mm day-1|
| *data_condition* |                  |
| kind         | operator |
| operator | >= |
| *percentile* |                  |
| kind         | quantity |
| long name | Percentile value |
| var_name | percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | {PRC} %|
| *percentile_condition* |                  |
| kind         | operator |
| operator | > |
| *reference_period* |                  |
| kind         | time_range |
| data | 1961/1990 |
:::


(idx-r{PRC}pPCT)=
### r{PRC}pPCT
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Percentage of total precipitation amount from days above the {PRC}th percentile    |
| Reference      | 2022 Ad hoc group           |
| Default period | annual      |
| **Input**      |                                      |
| data | pr |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_thresholded_percentile_occurrences |
| *data_threshold* |                  |
| kind         | quantity |
| long name | Wet day threshold |
| var_name | data_threshold |
| standard_name | lwe_precipitation_rate |
| proposed_standard_name | None |
| value | 1 mm day-1|
| *data_condition* |                  |
| kind         | operator |
| operator | >= |
| *percentile* |                  |
| kind         | quantity |
| long name | Percentile value |
| var_name | percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | {PRC} %|
| *percentile_condition* |                  |
| kind         | operator |
| operator | > |
| *reference_period* |                  |
| kind         | time_range |
| data | 1961/1990 |
:::


(idx-r{PRC}pDAYS)=
### r{PRC}pDAYS
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of days when precipitation is above the {PRC}th percentile    |
| Reference      | 2022 Ad hoc group           |
| Default period | annual      |
| **Input**      |                                      |
| data | pr |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_thresholded_percentile_occurrences |
| *data_threshold* |                  |
| kind         | quantity |
| long name | Wet day threshold |
| var_name | data_threshold |
| standard_name | lwe_precipitation_rate |
| proposed_standard_name | None |
| value | 1 mm day-1|
| *data_condition* |                  |
| kind         | operator |
| operator | >= |
| *percentile* |                  |
| kind         | quantity |
| long name | Percentile value |
| var_name | percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | {PRC} %|
| *percentile_condition* |                  |
| kind         | operator |
| operator | > |
| *reference_period* |                  |
| kind         | time_range |
| data | 1961/1990 |
:::


(idx-rx1day)=
### rx1day
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum 1-day precipitation    |
| Reference      | ETCCDI           |
| Default period | annual      |
| **Input**      |                                      |
| data | pr |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | thresholded_statistics |
| *threshold* |                  |
| kind         | quantity |
| long name | Wet day threshold |
| var_name | threshold |
| standard_name | lwe_precipitation_rate |
| proposed_standard_name | None |
| value | 1 mm day-1|
| *condition* |                  |
| kind         | operator |
| operator | >= |
| *statistic* |                  |
| kind         | reducer |
| reducer | max |
:::


(idx-rx5day)=
### rx5day
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum 5-day precipitation    |
| Reference      | ETCCDI           |
| Default period | annual      |
| **Input**      |                                      |
| data | pr |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | thresholded_running_statistics |
| *threshold* |                  |
| kind         | quantity |
| long name | Wet day threshold |
| var_name | threshold |
| standard_name | lwe_precipitation_rate |
| proposed_standard_name | None |
| value | 1 mm day-1|
| *condition* |                  |
| kind         | operator |
| operator | >= |
| *rolling_aggregator* |                  |
| kind         | reducer |
| reducer | sum |
| *window_size* |                  |
| kind         | quantity |
| long name | None |
| var_name | window_size |
| standard_name | None |
| proposed_standard_name | temporal_window_size |
| value | 5 day|
| *overall_statistic* |                  |
| kind         | reducer |
| reducer | max |
:::


(idx-rx{ND}day)=
### rx{ND}day
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum {ND}-day precipitation    |
| Reference      | ET-SCI           |
| Default period | annual      |
| **Input**      |                                      |
| data | pr |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | thresholded_running_statistics |
| *threshold* |                  |
| kind         | quantity |
| long name | Wet day threshold |
| var_name | threshold |
| standard_name | lwe_precipitation_rate |
| proposed_standard_name | None |
| value | 1 mm day-1|
| *condition* |                  |
| kind         | operator |
| operator | >= |
| *rolling_aggregator* |                  |
| kind         | reducer |
| reducer | sum |
| *window_size* |                  |
| kind         | quantity |
| long name | None |
| var_name | window_size |
| standard_name | None |
| proposed_standard_name | temporal_window_size |
| value | {ND} day|
| *overall_statistic* |                  |
| kind         | reducer |
| reducer | max |
:::


(idx-rh)=
### rh
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Mean of daily relative humidity    |
| Reference      | ECA&D           |
| Default period | monthly      |
| **Input**      |                                      |
| data | hurs |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | mean |
:::


(idx-rr)=
### rr
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Precipitation sum    |
| Reference      | ECA&D           |
| Default period | monthly      |
| **Input**      |                                      |
| data | pr |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | thresholded_statistics |
| *threshold* |                  |
| kind         | quantity |
| long name | Wet day threshold |
| var_name | threshold |
| standard_name | lwe_precipitation_rate |
| proposed_standard_name | None |
| value | 1 mm day-1|
| *condition* |                  |
| kind         | operator |
| operator | >= |
| *statistic* |                  |
| kind         | reducer |
| reducer | sum |
:::


(idx-pp)=
### pp
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Mean of daily sea level pressure    |
| Reference      | ECA&D           |
| Default period | monthly      |
| **Input**      |                                      |
| data | psl |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | mean |
:::


(idx-tg)=
### tg
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Mean of daily mean temperature    |
| Reference      | ECA&D           |
| Default period | monthly      |
| **Input**      |                                      |
| data | tas |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | mean |
:::


(idx-tn)=
### tn
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Mean of daily minimum temperature    |
| Reference      | ECA&D           |
| Default period | monthly      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | mean |
:::


(idx-tx)=
### tx
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Mean of daily maximum temperature    |
| Reference      | ECA&D           |
| Default period | monthly      |
| **Input**      |                                      |
| data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | mean |
:::


(idx-sd)=
### sd
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Mean of daily snow depth    |
| Reference      | ECA&D           |
| Default period | monthly      |
| **Input**      |                                      |
| data | snd |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | mean |
:::


(idx-sd1)=
### sd1
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Snow days (SD >= 1 cm)    |
| Reference      | ECA&D           |
| Default period | monthly      |
| **Input**      |                                      |
| data | snd |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | surface_snow_thickness |
| proposed_standard_name | None |
| value | 1 cm|
| *condition* |                  |
| kind         | operator |
| operator | >= |
:::


(idx-sd5cm)=
### sd5cm
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of days with snow depth >= 5 cm    |
| Reference      | ECA&D           |
| Default period | monthly      |
| **Input**      |                                      |
| data | snd |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | surface_snow_thickness |
| proposed_standard_name | None |
| value | 5 cm|
| *condition* |                  |
| kind         | operator |
| operator | >= |
:::


(idx-sd50cm)=
### sd50cm
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of days with snow depth >= 50 cm    |
| Reference      | ECA&D           |
| Default period | monthly      |
| **Input**      |                                      |
| data | snd |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | surface_snow_thickness |
| proposed_standard_name | None |
| value | 50 cm|
| *condition* |                  |
| kind         | operator |
| operator | >= |
:::


(idx-sd{D}cm)=
### sd{D}cm
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of days with snow depth >= {D} cm    |
| Reference      | ECA&D           |
| Default period | monthly      |
| **Input**      |                                      |
| data | snd |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | surface_snow_thickness |
| proposed_standard_name | None |
| value | {D} cm|
| *condition* |                  |
| kind         | operator |
| operator | >= |
:::


(idx-ss)=
### ss
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Sunshine duration, sum    |
| Reference      | ECA&D           |
| Default period | monthly      |
| **Input**      |                                      |
| data | sund |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | sum |
:::


(idx-fxx)=
### fxx
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum value of daily maximum wind gust strength    |
| Reference      | ECA&D           |
| Default period | monthly      |
| **Input**      |                                      |
| data | wsgsmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | max |
:::


(idx-fg6bft)=
### fg6bft
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Days with daily averaged wind strength >= 6 Bft (>=10.8 m/s)    |
| Reference      | ECA&D           |
| Default period | monthly      |
| **Input**      |                                      |
| data | sfcWind |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | wind_speed |
| proposed_standard_name | None |
| value | 10.8 meter second-1|
| *condition* |                  |
| kind         | operator |
| operator | >= |
:::


(idx-fgcalm)=
### fgcalm
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Calm days (daily mean wind strength <= 2 m/s)    |
| Reference      | ECA&D           |
| Default period | monthly      |
| **Input**      |                                      |
| data | sfcWind |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_occurrences |
| *threshold* |                  |
| kind         | quantity |
| long name | None |
| var_name | threshold |
| standard_name | wind_speed |
| proposed_standard_name | None |
| value | 2 meter second-1|
| *condition* |                  |
| kind         | operator |
| operator | <= |
:::


(idx-fg)=
### fg
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Mean of daily mean wind strength    |
| Reference      | ECA&D           |
| Default period | monthly      |
| **Input**      |                                      |
| data | sfcWind |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | statistics |
| *statistic* |                  |
| kind         | reducer |
| reducer | mean |
:::

<!---
(idx-CD)=
### CD
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Days with TG < 25th percentile of daily mean temperature and RR < 25th percentile of daily precipitation sum (cold/dry days)    |
| Reference      | ECA&D           |
| Default period | annual      |
| **Input**      |                                      |
| temp_data | tas |
| precip_data | pr |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_bivariate_percentile_occurrences |
| *temp_percentile* |                  |
| kind         | quantity |
| long name | Percentile value for temperature threshold |
| var_name | temp_percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | 25 %|
| *temp_percentile_condition* |                  |
| kind         | operator |
| operator | < |
| *precip_data_threshold* |                  |
| kind         | quantity |
| long name | Wet day threshold |
| var_name | precip_data_threshold |
| standard_name | lwe_precipitation_rate |
| proposed_standard_name | None |
| value | 1 mm day-1|
| *precip_data_condition* |                  |
| kind         | operator |
| operator | >= |
| *precip_percentile* |                  |
| kind         | quantity |
| long name | Percentile value for precipitation threshold |
| var_name | precip_percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | 25 %|
| *precip_percentile_condition* |                  |
| kind         | operator |
| operator | < |
| *reference_period* |                  |
| kind         | time_range |
| data | 1961/1990 |
:::


(idx-CW)=
### CW
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Days with TG < 25th percentile of daily mean temperature and RR > 75th percentile of daily precipitation sum (cold/wet days)    |
| Reference      | ECA&D           |
| Default period | annual      |
| **Input**      |                                      |
| temp_data | tas |
| precip_data | pr |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_bivariate_percentile_occurrences |
| *temp_percentile* |                  |
| kind         | quantity |
| long name | Percentile value for temperature threshold |
| var_name | temp_percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | 25 %|
| *temp_percentile_condition* |                  |
| kind         | operator |
| operator | < |
| *precip_data_threshold* |                  |
| kind         | quantity |
| long name | Wet day threshold |
| var_name | precip_data_threshold |
| standard_name | lwe_precipitation_rate |
| proposed_standard_name | None |
| value | 1 mm day-1|
| *precip_data_condition* |                  |
| kind         | operator |
| operator | >= |
| *precip_percentile* |                  |
| kind         | quantity |
| long name | Percentile value for precipitation threshold |
| var_name | precip_percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | 75 %|
| *precip_percentile_condition* |                  |
| kind         | operator |
| operator | > |
| *reference_period* |                  |
| kind         | time_range |
| data | 1961/1990 |
:::


(idx-WD)=
### WD
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Days with TG > 75th percentile of daily mean temperature and RR < 25th percentile of daily precipitation sum (warm/dry days)    |
| Reference      | ECA&D           |
| Default period | annual      |
| **Input**      |                                      |
| temp_data | tas |
| precip_data | pr |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_bivariate_percentile_occurrences |
| *temp_percentile* |                  |
| kind         | quantity |
| long name | Percentile value for temperature threshold |
| var_name | temp_percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | 75 %|
| *temp_percentile_condition* |                  |
| kind         | operator |
| operator | > |
| *precip_data_threshold* |                  |
| kind         | quantity |
| long name | Wet day threshold |
| var_name | precip_data_threshold |
| standard_name | lwe_precipitation_rate |
| proposed_standard_name | None |
| value | 1 mm day-1|
| *precip_data_condition* |                  |
| kind         | operator |
| operator | >= |
| *precip_percentile* |                  |
| kind         | quantity |
| long name | Percentile value for precipitation threshold |
| var_name | precip_percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | 25 %|
| *precip_percentile_condition* |                  |
| kind         | operator |
| operator | < |
| *reference_period* |                  |
| kind         | time_range |
| data | 1961/1990 |
:::


(idx-WW)=
### WW
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Days with TG > 75th percentile of daily mean temperature and RR > 75th percentile of daily precipitation sum (warm/wet days)    |
| Reference      | ECA&D           |
| Default period | annual      |
| **Input**      |                                      |
| temp_data | tas |
| precip_data | pr |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_bivariate_percentile_occurrences |
| *temp_percentile* |                  |
| kind         | quantity |
| long name | Percentile value for temperature threshold |
| var_name | temp_percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | 75 %|
| *temp_percentile_condition* |                  |
| kind         | operator |
| operator | > |
| *precip_data_threshold* |                  |
| kind         | quantity |
| long name | Wet day threshold |
| var_name | precip_data_threshold |
| standard_name | lwe_precipitation_rate |
| proposed_standard_name | None |
| value | 1 mm day-1|
| *precip_data_condition* |                  |
| kind         | operator |
| operator | >= |
| *precip_percentile* |                  |
| kind         | quantity |
| long name | Percentile value for precipitation threshold |
| var_name | precip_percentile |
| standard_name | None |
| proposed_standard_name | quantile |
| value | 75 %|
| *precip_percentile_condition* |                  |
| kind         | operator |
| operator | > |
| *reference_period* |                  |
| kind         | time_range |
| data | 1961/1990 |
:::
--->

(idx-nzero)=
### nzero
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Number of zero-crossing days (days when Tmin < 0 degC < Tmax)    |
| Reference      | SMHI           |
| Default period | annual      |
| **Input**      |                                      |
| low_data | tasmin |
| high_data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | count_level_crossings |
| *threshold* |                  |
| kind         | quantity |
| long name | Level crossing value for daily air temperature |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | 0 degree_Celsius|
:::


(idx-faf)=
### faf
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | First Autumn Frost (day-of-year during Jul-Dec when Tmin < 0 degC)    |
| Reference      | B4EST           |
| Default period | annual[jasond]      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | first_occurrence |
| *threshold* |                  |
| kind         | quantity |
| long name | Threshold temperature for frost |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | 0 degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | < |
:::


(idx-lsf)=
### lsf
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Last Spring Frost (day-of-year during Jan-Jun when Tmin < 0 degC)    |
| Reference      | B4EST           |
| Default period | annual[jfmamj]      |
| **Input**      |                                      |
| data | tasmin |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | last_occurrence |
| *threshold* |                  |
| kind         | quantity |
| long name | Threshold temperature for frost |
| var_name | threshold |
| standard_name | air_temperature |
| proposed_standard_name | None |
| value | 0 degree_Celsius|
| *condition* |                  |
| kind         | operator |
| operator | < |
:::


(idx-maxdtr)=
### maxdtr
| Field          | Description                          |
|----------------|--------------------------------------|
| Distribution | clix-meta-0.6.1 |
| Long name      | Maximum Diurnal Temperature Range    |
| Reference      | SMHI           |
| Default period | monthly      |
| **Input**      |                                      |
| low_data | tasmin |
| high_data | tasmax |
:::{collapse} Details
| Field              | Description                          |
|--------------------|--------------------------------------|
| **Index function** | diurnal_temperature_range |
| *statistic* |                  |
| kind         | reducer |
| reducer | max |
:::

# ASYNC-DB-SERVER

### Endpoints

- **`/asy/db/v1.0/config/init`**  - Initiatize the Database, make connections, etc; Also triggers the _**`query consumer`**_


- **`/asy/db/v1.0/resources/q_query`** Add Insert Queries to the provider Queue using _**`query provider`**_

- **`/asy/db/v1.0/resources/view_q`** Add current state of Query Queue

- **`/asy/json/v1.0/resources/dump`** Takes the View Table query and dumps the data into json file

- **`/asy/csv/v1.0/resources/dump`** Takes the View Table query and dumps the data into csv file
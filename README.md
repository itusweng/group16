# ITU BLG411E Software Engineering Course Project
# Resillient QR
This web application was designed for the ITU BLG411E Software Enginerring course project.

Main feature is the API, written in FastAPI library of Python, that allows users to register account and create/manage QR codes. There are also admin functionalities. For more detail, please refer to the documentation.

You can also find a frontend with limited features and unit/load test results in this repository.

## How To Run
* Download requirements via **requirements.txt**
* Create a PostgreSQL server and run **ddl_statements.sql** to create the tables.
* Create a file called **db_access_string.txt** and place it inside the directory. It's format should be like this:
  ```
  dbname=DATABASENAME host=HOSTNAME port=PORT user=USERNAME password=PASSWORD 
  ```
* Run the server via  `uvicorn server:app` command.
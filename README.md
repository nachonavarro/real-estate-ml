# real-estate-ml
Using geospatial data to find investment opportunities in the real estate market

## Acquiring the data

We need to add geographical columns for every property. How to run:

1. There is some setup necessary before acquiring the data:
    1. Install Python 3
    2. Create a virtual environment if you don't have one. To create one, go to the project root and run 
        ```
        python3 -m venv .env
        ```
    3. Once you have your virtual environment activate it via
        ```
        source .env/bin/activate
        ```
        *Note:* You'll need to activate your environment each time.
    
    4. Install the necessary packages via
    ```
    pip install -r requirements.txt
    ```
   
2. Acquire an API key for Foursquare and replace the `client_secret` and `client_id` with the
one Foursquare gives you and change it in `runner.py`.
3.  Finally, run 
```
python -m properties.data.runner 0 10
```
where the numbers indicate from which property to start and end. If you start running and
stop midway through for whatever reason (e.g. a crash or you've reached the daily API limit call),
call the script again but pass in the flag `--reuse` so that you don't create a new database.

## Dividing the task of finding the data

We'll divide the the properties into three so that we can call the API at the same time.

1. Nikhil: 0-2600
2. Chih: 2601-5200
3. Nacho: 5201-8039

## Once you have the data

Once you have the data you'll see a new SQLite database on the `data` folder. When we have all the properties
filled up we'll merge all of the databases back into one. At the moment we can't do this do to the API limit
restriction, and in this way we can work in parallel.

If you want to play around with the contents of the database as a pandas dataframe, do the following:

```python
from properties.data.database import DatabaseContext

db = DatabaseContext('properties0_10') # the name of the database to link up
df = db.as_df()
```

And you should be good to go!

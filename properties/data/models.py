import csv
import operator
from functools import reduce
from itertools import islice

import yaml
from peewee import *
from playhouse.migrate import migrate, SqliteMigrator
from playhouse.reflection import generate_models

db = SqliteDatabase(None)
migrator = SqliteMigrator(db)


class BaseModel(Model):
    class Meta:
        database = db


class Property(BaseModel):
    """
    A model for the properties table that is going to be stored in the SQLite.
    """

    class Meta:
        table_name = 'properties'

    fireplaces = IntegerField()
    garage_spaces = IntegerField()
    category_code = IntegerField()
    market_value = FloatField()
    bathrooms = IntegerField()
    bedrooms = IntegerField()
    stories = IntegerField()
    sale_date = DateField()
    sale_price = FloatField()
    total_area = FloatField()
    total_livable_area = FloatField()
    latitude = DecimalField()
    longitude = DecimalField()

    @classmethod
    def partial_properties(cls):
        """
        This method finds all the properties that still need to be filled with
        geographical data. In our case it means that any geographical column is null.
        We use this method to find out which rows (i.e. properties) of our properties table
        still need API calls to be filled.

        Note we need to use Python introspection to get all the dynamically added fields.
        In fact, calling Property.bedrooms works but Property.gas_station doesn't.

        :return: All the properties that have null for some geographical column.
        """
        _Property = generate_models(db)['properties']
        any_null = reduce(operator.or_, [_Property._meta.fields[cat].is_null() for cat in Category.categories()])
        return _Property.select().where(any_null)

    @classmethod
    def from_csv(cls, start, end):
        """
        Populates the database with all the properties from the properties.csv dataset
        from the OpenDataPhilly website. We have a start and end parameter to divide
        the database into subdatabases so that each member of the group can use
        the 100,000 API calls limit that Foursquare, our data provider, allows.

        As with `create_db`, this function should only
        be run once, so you should not have to call this method. The data from the csv
        is inserted into SQLite in batches for efficiency. Note that we can't insert
        all the data source at once with `insert_many` since SQLite has a limit of
        999 variables-per-query.

        :param start: The index of the first row to include
        :param end: The index of the last row to include
        """
        with open('data/south_philly_properties.csv', 'r') as f:
            dataset = csv.reader(f)
            header = next(dataset)
            data_source = [{h: r for h, r in zip(header, row)} for row in islice(dataset, start, end)]
            with db.atomic():
                for batch in chunked(data_source, 1000):
                    Property.insert_many(batch).execute()


class Category(BaseModel):
    """
    A model that represents a category of points of interest. Each category has
    a unique id in Foursquare and the category name.
    Note this is NOT the point of interest itself, it is the category of the
    point of interest.
    Examples of categories: Bar, Gas Station, Coffee Shop
    """

    class Meta:
        table_name = 'points_of_interest'

    id = CharField()
    category = CharField()

    def save(self, *args, **kwargs):
        """
        We override the default save behavior to add the category as a column in
        the properties table.
        """
        migrate(
            migrator.add_column('properties', self.category, FloatField(null=True))
        )
        return super().save(*args, **kwargs)

    @classmethod
    def categories(cls):
        return [c.category for c in Category.select()]

    @classmethod
    def update_categories(cls):
        """
        Adds all the categories that have not been added yet to SQLite, and creates a column
        in the properties table for each new category.
        Note: to add categories, simply add them to the categories.yaml file.
        """
        with open('data/categories.yaml', 'r') as f:
            categories = yaml.load(f, Loader=yaml.Loader)
            for category in categories:
                Category.get_or_create(**category)

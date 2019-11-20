import pandas as pd
from playhouse.migrate import SqliteMigrator
import properties.data.models as models


class DatabaseContext:

    def __init__(self, db_name='properties'):
        self.db = models.db
        self.db.init(f'data/{db_name}.sqlite')
        self.migrator = SqliteMigrator(self.db)

    def create_db(self):
        """
        Creates/resets the database. This operation should only be run once. Since we
        are tracking the database on git, you should not have to call this method.
        """
        with self.db:
            self.db.drop_tables([models.Property, models.Category])
            self.db.create_tables([models.Property, models.Category])

    def as_df(self):
        """
        Converts the data from sqlite to a Pandas dataframe.
        :return: A DataFrame with all the properties and their geographical features.
        """
        with self.db:
            df = pd.read_sql('SELECT * FROM properties', self.db.connection(), index_col='id')
        return df

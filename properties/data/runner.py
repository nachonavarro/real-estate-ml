import argparse

from foursquare import Foursquare, RateLimitExceeded
from properties.data.database import DatabaseContext
from properties.data.models import Property, Category


class Runner:
    """
    A class that is in charge of:
        1. Creating the properties database for a subset of properties.
        2. Running all the API calls that will populate the geo features columns.
    """
    MAX_RADIUS = 10_000

    def __init__(self):
        self.db_context = None
        self.client = Foursquare(
            client_id='UG120RKSOCA55CY5TMWF1QBLXV1W1UWDPAUJADAYCYO1TLRK',
            client_secret='3JLP5BDEL1YZH1U14JOIZMCQ4WICTG51PPN2ENP4MW1FVU34'
        )

    def run(self, start, end, create=True, verbose=True):
        """
        This function:
            1. Creates a database from `start` to `end` consisting of end - start records.
            2. Populates the database from the properties.csv
            3. Adds the category table with the categories as columns on the properties table
        Note: Each of us will run this locally, push our partial table to git,
        and in the end we will merge all the tables. For instance, one person runs
        Runner().run(0, 1000) (creating a table), another will run Runner().run(1001, 2000), etc.
        If you specify the create parameter to be False, the database context will not create a new database,
        rather it will pick up the database that matches start-end. This will come in handy if, for example,
        you create a database of 100,000 records, but the API throws a 400 error on record 60,000.
        Then you will need to run Runner.run() again, but without creating a database again!
        """
        self.db_context = DatabaseContext(db_name=f'properties{start}_{end}')
        if create:
            self.db_context.create_db()
            Property.from_csv(start, end)
        Category.update_categories()
        self.transfer_geo_data(start, verbose)

    def transfer_geo_data(self, start, verbose):
        """
        Goes through all properties that still need their geo columns filled (via partial_properties())
        calling the API on each geo column. For instance, if the geo columns are bank, park, and movie theater,
        our db has 2000 properties, and 1000 out of the 2000 properties still need to be filled, we will
        call the API 1000 properties * 3 geo columns = 30_000.
        """
        partial_properties = Property.partial_properties()
        for i, row in enumerate(partial_properties):
            if verbose:
                print(f'· Populating record...')
                print(f'· {len(partial_properties) - i} remaining...')
                print(f'· {self.client.rate_remaining} API calls left for today...')
            origin = (row.latitude, row.longitude)
            for category in Category.select():
                if getattr(row, category.category) is None:
                    try:
                        closest = self.get_closest_poi(origin, category)
                        setattr(row, category.category, closest)
                        if verbose:
                            print(f'\t{category.category} ({closest}m) ✓')
                    except RateLimitExceeded:
                        raise RateLimitExceeded(f'Stopped recording on row {start + i}.')
            row.save()
            if verbose:
                print()

    def get_closest_poi(self, origin, category):
        lat, lng = origin
        response = self.client.venues.search(params={
            'll': f'{lat},{lng}',
            'intent': 'browse',
            'radius': self.MAX_RADIUS,
            'categoryId': category.id
        })
        venues = response['venues']
        closest_venue = min(venues, key=lambda venue: venue['location']['distance'])
        return closest_venue['location']['distance']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A runner that calls Foursquare's API to find venues.")
    parser.add_argument('start', help='first index to populate data from.', type=int)
    parser.add_argument('end', help='last index to populate data from.', type=int)
    parser.add_argument('-r', '--reuse', action="store_false",
                        help='Whether to keep working from an existing database.')
    args = parser.parse_args()
    r = Runner()
    print(args.reuse)
    r.run(args.start, args.end, create=args.reuse)

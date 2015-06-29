from settings import *  # flake8: noqa

def create_db():
    from django.db import connection
    connection.creation.create_test_db(autoclobber=True)

create_db()

from tests.models import *  # flake8: noqa
from tests.factories import *  # flake8: noqa

for i in range(100): ExampleModelFactory.create()

from settings import *

def create_db():
    from django.db import connection
    connection.creation.create_test_db(autoclobber=True)

create_db()

from tests.models import *
from tests.factories import *

for i in range(100): TestModelFactory.create()

import pytest
from pathlib import Path
from dotenv import load_dotenv



@pytest.fixture()
def setup():
    assert load_dotenv(Path(__file__).parent.joinpath(".env"))
    # code to tear down test environment


@pytest.fixture()
def teardown():
    # code to tear down test environment
    pass

@pytest.mark.usefixtures("setup", "teardown")
def test_load_dbconfig():
    from mainapp.core.containers import get_container

    container = get_container()
    container

# database:
#   driver: "mysql"  # posgresql=psycopg
#   host: "${DATABASE__HOST}"
#   port: "${DATABASE__PORT}"
#   dbname: "${DATABASE__DBNAME}"
#   username: "${DATABASE__USERNAME}"
#   password: "${DATABASE__PASSWORD}"

#   # POSTGRES: See: https://www.psycopg.org/psycopg3/docs/advanced/pool.html#pool-stats
#   # pool_min:
#   # pool_max:
#   # pool_size: 5
#   # pool_available: 5
#   # requests_waiting: 0
#   # usage_ms: 100
#   # requests_num:
#   # requests_queued:
#   # requests_wait_ms:
#   # returns_bad:
#   # connections_num: 5
#   # connections_ms: 100
#   # connections_errors:
#   # connections_lost:

#   # MYSQL
#   echo: True
#   echo_pool: False
#   # case_sensitive: False
#   # encoding: utf-8
#   isolation_level: SERIALIZABLE
#   pool_reset_on_return: rollback # rollback, commit, None
#   pool_timeout: 100
#   pool_pre_ping: True
#   pool_recycle: 270
#   pool_size: 5
#   max_overflow: 10
#   implicit_returning: True
#   hide_parameters: False
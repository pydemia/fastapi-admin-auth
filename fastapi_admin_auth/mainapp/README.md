
## DB Relations

* Standalone: `Item`
* One-to-One: `Course` : `Certificate`
* One-to-Many: `Course`: `Teacher`
* One-to-Many(Optional-Foreign Key Only): `Course` : `Textbook`
* Many-to-Many: `Course` : `Student`


## DB Migrations

### alembic

```bash
$ cd fastapi_admin_auth
$ alembic init mainapp-migrations
  Creating directory '/Users/a09255/git/fastapi-admin-
  auth/fastapi_admin_auth/mainapp/migrations' ...  done
  Creating directory '<pwd>/migrations/versions' ...  done
  Generating <pwd>/migrations/script.py.mako ...  done
  Generating <pwd>/migrations/env.py ...  done
  Generating <pwd>/migrations/README ...  done
  Generating <pwd>/alembic.ini ...  done
  Please edit configuration/connection/logging settings in '<pwd>/alembic.ini' before proceeding.
```

* `env.py`:

```py
from sqlmodel import SQLModel
from mainapp.domains import (
    example,
    school,
)

db_models = [
    example.domain_models,
    school.domain_models,
]

target_metadata = SQLModel.metadata

```

* `script.py.mako`:

```diff
from alembic import op
import sqlalchemy as sa
++import sqlmodel
${imports if imports else ""}
```




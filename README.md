# fastapi-backend


## Requirements

* 분리가능한 App 구조여야 함 -> apps로 분리하고, mount하는 형태로 설계
See: https://fastapi.tiangolo.com/advanced/sub-applications/

Sub App (`subapp/main.py`):
```python
from fastapi import FastAPI
subapi = FastAPI()

@subapi.get("/sub")
def read_sub():
    return {"message": "Hello World from sub API"}
```

Main App (`main.py`):
```python
from fastapi import FastAPI
from subapp.main import subapi
app = FastAPI()

@app.get("/app")
def read_main():
    return {"message": "Hello World from main app"}

app.mount("/subapi", subapi)
```

* DB migration: `alembic`

App단위 관리: 개발주체가 외부일 경우. 관계성 단절 필요.

---

# Key Packages
* fastapi (+ starlette)
* sqlalchemy (+ postgresql)
* sqlmodel (+ pydanticV2 + dotenv)
* dependency-injector
* alembic
* autologging
* python-jose
* gunicorn (+ uvicorn)
* kubernetes
* python-multipart

## Sub Packages
* sqlalchemy-filters
* coloredlogs
* httpx
* coverage
* pytest

* ptvsd
* pydevd


# Architecture

* main.py
* core(common)
  * user/group
  * roles(rbac or abac)(casbin)
  * auth(jwt, oauth, etc.)
  * config
  * dependency injection(dependency-injector)
  * exception_handlers & routers
  * alembic(migrations)
* chat
* worker
* etc.

```bash
./create-condaenv.sh fastapi-app
```


```bash
docker network create local
```

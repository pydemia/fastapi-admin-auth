# Blender Backend 템플릿 작업 설명

이 문서는 Blender Backend 템플릿 작업에 대한 설명 문서입니다.
(작성자: 이소영)
***
## 1. 개요

### 1) 배경
'우리은행 비정형 자산화 시스템 구축' 프로젝트의 개발 기간을 감안해 Blender Backend 템플릿 작업을 선행한다.  
참고로 Blender는 아래와 같은 작업을 수행할 예정이다. (외부 모듈과의 통신은 REST API호출)

- 통합검색 App으로 부터 인입된 사용자 질의를 DPR을 통해 Embedding 
- FAISS Server를 통해 AI검색결과 조회(passage id)
- Keyword검색기를 통해 키워드 검색 결과 조회
- (AI검색결과를 통해 얻은)passage id를 이용해 지식 DB로부터 실제 Text를 조회
- Ensemble모듈을 통해 Keyword검색 결과와 AI 검색결과의 Ensemble 모델 추출

### 2) 기능
템플릿에서 제공하는 기능은 아래와 같다.
- DB연동 및 데이터 조회
- 외부 API 호출

### 3) 개발 언어 및 lib
Python (FastAPI framework)
- [aiohttp](https://pypi.org/project/aiohttp/): Async http client/server framework

- [asyncio](https://pypi.org/project/asyncio/): Async I/O 지원

- [asyncpg](https://pypi.org/project/asyncpg/): PostgreSQL과 asyncio를 위해 디자인된 database interface 제공

- [fastapi](https://pypi.org/project/fastapi/): Python3.6+의 API를 빌드하기 위한 framework

- [pydantic](https://pypi.org/project/pydantic/): data validation과 data parsing을 제공

- [python-decouple](https://pypi.org/project/python-decouple/): env 설정 파일 parsing을 제공

- [python-dotenv](https://pypi.org/project/python-dotenv/): env 파일로부터 key-value읽어서 환경 변수 설정 지원

- [pythondi](https://pypi.org/project/pythondi/): dependency injection 지원

- [sqlalchemy](https://pypi.org/project/SQLAlchemy/): 파이썬 SQL toolkit과 Object Relational Mapper를 제공

- [starlette](https://pypi.org/project/starlette/): ASGI framework (비동기 서비스 구축에 이상적인)

- [uvicorn](https://pypi.org/project/uvicorn/): Python용 ASGI web server implementation

***
## 2. Project Structure
### 1) 디렉토리 구조
패키지 구성은 확장 및 고도화, 유지보수 용이성을 고려해 도메인형 디렉토리 구조로 구성  
디렉토리는 크게 공통(common), 외부 서비스 연동(infra), 도메인(search) 부문으로 구성한다.
```bash
├── apps
│      ├── common                       # 프로젝트 전방위적으로 사용되는 객체들로 구성
│      │      ├── configs               
│      │      ├── exceptions            
│      │      ├── http            
│      │      ├── middleware            
│      │      ├── models                
│      │      ├── utilities             
│      │      └── values                
│      └── search                       # 도메인 정의
│          ├── apis                     
│          ├── models
│          ├── repository
│          ├── schemas
│          └── services
├── alembic
└── docs
```

### 2) 상세 구조
전체 프로젝트 구성은 아래와 같다.
```bash
├── apps
│      ├── common
│      │      ├── configs
│      │      │      ├── database
│      │      │      │      ├── async_database
│      │      │      │      │      ├── base.py
│      │      │      │      │      ├── connection.py
│      │      │      │      │      ├── repository.py
│      │      │      │      │      └── session.py
│      │      │      │      └── sync_database
│      │      │      ├── manager.py
│      │      │      └── settings
│      │      │          └── base.py
│      │      ├── exceptions
│      │      │      └── custom.py
│      │      ├── http
│      │      │      ├── asyncClient
│      │      │      │      └── async_base_http_client
│      │      │      └── ai_search.py
│      │      ├── middleware
│      │      │      └── exception.py
│      │      ├── models
│      │      │      └── response_model.py
│      │      ├── utilities
│      │      │      └── formatters.py
│      │      └── values
│      │          ├── constants
│      │          └── enums
│      │              └── error_codes.py
│      ├── infra
│      │      └── http
│      │          ├── ai_search.py
│      │          └── asyncClient
│      │              └── async_base_http_client.py
│      └── search
│          ├── apis
│          │      ├── route.py
│          │      └── v1
│          │          └── endpoints
│          │              ├── ai_searches.py
│          │              └── metadata.py
│          ├── models
│          │      ├── document.py
│          │      └── table.py
│          ├── repository
│          │      └── metadata.py
│          └── schemas
│                 ├── base.py
│                 ├── metadata.py
│                 └── web_search.py
├── main.py
├── .env
├── .env.development
├── .env.local
├── Dockerfile
├── README.md
├── requirements.txt
├── docs
└── alembic
```

### 3) 상세 설명

#### (1) 공통

##### a) 기본 정보 설정
공통 및 환경 변수값(.env) 읽어와 setting  
(DB연동 정보, blender Open API정보, HTTP client설정 정보 등..)
```javascript
class BackendBaseSettings(pydantic.BaseSettings):
    OPENAPI_VERSION: str = "/v1"
    OPENAPI_PREFIX: str = "/api" + OPENAPI_VERSION
    OPENAPI_SEARCH_PATH: str = OPENAPI_PREFIX + "/search"
    
    OPENAPI_METADATA_PATH: str = OPENAPI_PREFIX + "/metadata"
    OPENAPI_AI_SEARCH_PATH: str = OPENAPI_PREFIX + "/ai_search"

    METADATA_DB_TYPE: str = decouple.config("METADATA_DB_TYPE", cast=str)
    METADATA_DB_SCHEMA: str = decouple.config("METADATA_DB_SCHEMA", cast=str)
    METADATA_DB_HOST: str = decouple.config("METADATA_DB_HOST", cast=str)
    METADATA_DB_PORT: int = decouple.config("METADATA_DB_PORT", cast=int)
    METADATA_DB_NAME: str = decouple.config("METADATA_DB_NAME", cast=str)
    METADATA_DB_PASSWORD: str = decouple.config("METADATA_DB_PASSWORD",
                                                cast=str)
    METADATA_DB_USERNAME: str = decouple.config("METADATA_DB_USERNAME",
                                                cast=str)
    
    HTTP_DEFAULT_TIMEOUT: int = decouple.config("HTTP_DEFAULT_TIMEOUT",
                                                cast=int)
    HTTP_LIMIT_PER_HOST: int = decouple.config("HTTP_LIMIT_PER_HOST",
                                               cast=int)

    AI_SEARCH_URL: str = decouple.config("AI_SEARCH_URL", cast=str)
    AI_SEARCH_API_KEY: str = decouple.config("AI_SEARCH_API_KEY", cast=str)

```

##### b) DB Connection
SQLAlchemy lib를 이용해 async DB Connection을 제공. (with Connection Pooling)  
DB Access요청 시마다 매번 DB연결/닫기 반복 시 큰 비용이 발생하므로 Connection Pooling 적용.
```javascript
class AsyncDatabase:
    def __init__(self):
        self.uri: PostgresDsn = PostgresDsn(
            url=f"{settings.METADATA_DB_SCHEMA}://"
                f"{settings.METADATA_DB_USERNAME}:"
                f"{settings.METADATA_DB_PASSWORD}@"
                f"{settings.METADATA_DB_HOST}:"
                f"{settings.METADATA_DB_PORT}/"
                f"{settings.METADATA_DB_NAME}",
            scheme=settings.METADATA_DB_SCHEMA,
        )
        self.async_engine: AsyncEngine = \
            create_async_engine(url=self.set_async_db_uri,
                                echo=settings.IS_DB_ECHO_LOG,
                                pool_size=settings.DB_POOL_SIZE,
                                max_overflow=settings.DB_POOL_OVERFLOW,
                                poolclass=SQLAlchemyQueuePool
                                )
        self.async_session: AsyncSession = AsyncSession(bind=self.async_engine)
        self.pool: SQLAlchemyPool = self.async_engine.pool
```

##### c) Exception처리
+ 사용자 정의 Exception Define
```javascript
class AISearchException(CustomException):
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    error_code = ErrorCodes.AI_SEARCH_API_CALL_ERROR.code
    error_message = ErrorCodes.AI_SEARCH_API_CALL_ERROR.msg
```
+ 사용자 정의 Exception 발생
```javascript
try:
    response = await async_base_api.get(url=settings.AI_SEARCH_URL,
                                        params=dict(query=query,
                                                    page=page,
                                                    size=size))
    status_code = response.get("status_code")
    if status_code == HTTPStatus.OK:
    ...
  else:
        error_message = "status_code:" + str(status_code) + \
                        ",error:" + response.get("error")
        raise AISearchException(error_message)
except Exception as external_ex:
    raise AISearchException(error_message="error:"
                            + external_ex.__doc__)
return response
```

+ Exception처리 (Middleware)
```javascript
def exception_middleware():
    async def customize_response(request: Request, call_next):
        try:
            response = await call_next(request)
            return response

        except CustomException as custom_ex:
            error_dict = dict(code=custom_ex.error_code,
                              msg=custom_ex.error_message)
            response = JSONResponse(
                content=error_dict, status_code=custom_ex.status_code)
            return response
    return customize_response
```

#### (2) database 데이터 조회
##### a) route
```javascript
route.py
api_router.include_router(metadata.router,
                          prefix=settings.OPENAPI_METADATA_PATH,
                          tags=['Metadata'])

api_router.include_router(ai_searches.router,
                          prefix=settings.OPENAPI_AI_SEARCH_PATH,
                          tags=['AI Search'])
```

##### b) api 구현
Validation 체크, 문서화 내용 정의, service 호출
```javascript
@router.get('/list',
            name="메타데이터 리스트 조회 (with pagenation)",
            response_model=ResponseBase)
async def search_list(page: Optional[int] = Query(settings.QUERY_DEFAULT_OFFSET,
                                                  title="페이지번호",
                                                  description="페이지 번호는 0부터 시작",
                                                  ge=0),
                      size: Optional[int] = Query(settings.QUERY_DEFAULT_LIMIT,
                                                  title="사이즈",
                                                  description="size는 0보다 큰 값",
                                                  ge=1),
                      metadata_repository: MetadataSQLRepository =
                      Depends(get_repository(repo_type=MetadataSQLRepository)))\
                            -> Sequence[Metadata]:

    metadata_list = await metadata_repository.get_metadata_list(
        page=page, size=size)

    return ResponseBase(data=metadata_list)

```


##### c) Repository 구현
sqlalchemy lib를 이용해 ORM을 통한 DB데이터 조회
```javascript
    async def get_metadata_list(self, page, size) -> Sequence[Metadata]:

        stmt = sqlalchemy.select(Document) \
                                .where(Document.is_deleted == False) \
                                .order_by(Document.document_id.desc()) \
                                .offset(page).limit(size)
        query = await self.async_session.execute(statement=stmt)
        result = query.scalars().all()
        metadata_list: list = []
        
        for metadata_item in result:
            metadata = Metadata.from_orm(metadata_item)
            metadata_list.append(metadata)

        return metadata_list
```

##### d) Model 구현
```javascript
class Document(Base):
    __tablename__ = "document"

    document_id: SQLMapped[int] = sql_mapped_column(primary_key=True)

    title: SQLMapped[str] = sql_mapped_column(sqlalchemy.String(length=256),
                                              nullable=False)

    summary: SQLMapped[str] = sql_mapped_column(sqlalchemy.String(length=512),
                                                nullable=True)

    domain_id: SQLMapped[int] = sql_mapped_column(sqlalchemy.Integer,
                                                  nullable=False)

    ...
```

##### d) Schema 구현
+ BaseSchemaModel schema관련 config 정의
```javascript
class MetadataBase(BaseSchemaModel):
    document_id: int = Field(title="문서 아이디",
                             description="문서 ID는 도메인 별로 채번된 값이다.")

    title: str = Field(...,
                       title="문서 제목",
                       max_length=256,
                       description="문서 제목")

    summary: str = Field(...,
                         title="문서 요약내용",
                         max_length=512,
                         description="문서 요약내용")

    domain_id: int = Field(...,
                           title="도메인 아이디",
                           description="문서가 속한 도메인 아이디")

    document_format: str = Field(...,
                                 title="문서 파일 포맷",
                                 max_length=50,
                                 description="문서 파일 포맷")

    authority: int = Field(...,
                           title="문서 접근 권한",
                           description="문서 접근 권한")

    document_owner_id: int = Field(...,
                                   title="문서 소유자 ID",
                                   description="문서 소유자 ID")

    created_by_user_id: int = Field(...,
                                    title="메타데이터 생성자 ID",
                                    description="메타데이터 생성자 ID")

    modified_by_user_id: int = Field(...,
                                     title="메타데이터 수정자 ID",
                                     description="메타데이터 수정자 ID")


class Metadata(MetadataBase):
    pass
```

#### (3) 외부 REST API호출
+ aiohttp를 이용해 async http통신 기본 기능 구현  
(httpx lib는 동기/비동기 http통신을 제공하나 aiohttp가 성능(속도)면에서 우세하여 aiohttp를 선택함.  
참고로 동기 http통신도 httpx lib보다는 requests lib가 성능면에서 우세하다고 함.)
```javascript
@dataclass
class AsyncBaseHttpClient:
    headers: dict = field(default_factory=dict)
    aiohttp_client: Optional[ClientSession] = field(default=None)

    def __post_init__(self):
        if isinstance(self.headers, dict):
            self.headers = {**self._get_default_headers(), **self.headers}
        else:
            self.headers = self._get_default_headers()

    def _get_default_headers(self) -> Dict[str, any]:
        return {"Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "fastapi-aiohttp-simple-example"}
        
    @classmethod
    def get_aiohttp_client(cls) -> ClientSession:
        if cls.aiohttp_client is None:
            timeout = ClientTimeout(total=30)
            connector = TCPConnector(family=AF_INET, limit_per_host=10)
            cls.aiohttp_client = ClientSession(timeout=timeout,
                                               connector=connector)
        return cls.aiohttp_client

```

+ Daum 웹문서 검색. API호출
AsyncBaseHttpClient를 이용해 Daum Open API호출
```javascript
async_base_api = AsyncBaseHttpClient(headers=None, aiohttp_client=None)

class AISearchHttpClient:
    async def get_web_search(self, query, page, size):
        try:
            async_base_api.add_custom_header(key="Authorization",
                                             value=settings.AI_SEARCH_API_KEY)
            response = await async_base_api.get(url=settings.AI_SEARCH_URL,
                                                params=dict(query=query,
                                                            page=page,
                                                            size=size))
            status_code = response.get("status_code")
            if status_code == HTTPStatus.OK:
                web_document_list: list = list()
                response_body = json.loads(response.get("body"))          
                ....
                return WebSearchResult(meta=response_body["meta"],
                                       documents=web_document_list)

            else:
                error_message = "status_code:" + str(status_code) + \
                                ",error:" + response.get("error")
                raise AISearchException(error_message)
        except Exception as external_ex:
            raise AISearchException(error_message="error:"
                                    + external_ex.__doc__)

        return response
```

***
## 3. Open API Documentation
[doc] http://3.34.154.82:8000/docs/api/v1#/  
[redoc] http://3.34.154.82:8000/redoc/api/v1
![metadata리스트 조회](https://gitlab.com/skdt/aistudio/aibrilta/aibril-ta-solution/base-backend-fastapi/-/raw/development/docs/%5BRedoc%5D%20metadata%20%EB%A6%AC%EC%8A%A4%ED%8A%B8%20%EC%A1%B0%ED%9A%8C.png "metadata리스트 조회")
![metadata단건 조회]( https://gitlab.com/skdt/aistudio/aibrilta/aibril-ta-solution/base-backend-fastapi/-/raw/development/docs/%5BRedoc%5D%20metadata%20%EB%8B%A8%EA%B1%B4%20%EC%A1%B0%ED%9A%8C.png "metadata단건 조회")
![Daum 웹 문서 조회 (외부 API호출)]( https://gitlab.com/skdt/aistudio/aibrilta/aibril-ta-solution/base-backend-fastapi/-/raw/development/docs/%5BRedoc%5D%20Daum%20%EC%9B%B9%20%EB%AC%B8%EC%84%9C%20%EC%A1%B0%ED%9A%8C%20(%EC%99%B8%EB%B6%80%20API%ED%98%B8%EC%B6%9C).png "Daum 웹 문서 조회 (외부 API호출)")
***
## 4. 테스트
![metadata리스트 조회](https://gitlab.com/skdt/aistudio/aibrilta/aibril-ta-solution/base-backend-fastapi/-/raw/development/docs/%5BPostman%5Dmetadata%20%EB%A6%AC%EC%8A%A4%ED%8A%B8%20%EC%A1%B0%ED%9A%8C.png "metadata리스트 조회 (http://3.34.154.82:8000/api/v1/metadata/11)")
![metadata단건 조회](https://gitlab.com/skdt/aistudio/aibrilta/aibril-ta-solution/base-backend-fastapi/-/raw/development/docs/%5BPostman%5Dmetadata%20%EB%8B%A8%EA%B1%B4%20%EC%A1%B0%ED%9A%8C.png "metadata단건 조회 (http://3.34.154.82:8000/api/v1/metadata/list?page=0&size=5)")
![Daum 웹 문서 조회 (외부 API호출)](https://gitlab.com/skdt/aistudio/aibrilta/aibril-ta-solution/base-backend-fastapi/-/raw/development/docs/%5BPostman%5D%20Daum%20%EC%9B%B9%EB%AC%B8%EC%84%9C%20%EC%A1%B0%ED%9A%8C%20(%EC%99%B8%EB%B6%80%20api%ED%98%B8%EC%B6%9C).png "Daum 웹 문서 조회 (외부 API호출) (http://3.34.154.82:8000/api/v1/ai_search?query=samsung&page=3&size=2)")

***
## 5. 배포
EC2 인스턴스명: woori_bank  
key pair: wooribank-key.pem  
![EC2인스턴스 정보](https://gitlab.com/skdt/aistudio/aibrilta/aibril-ta-solution/base-backend-fastapi/-/raw/development/docs/%5B%EB%B0%B0%ED%8F%AC%5D%20AWS%20EC2%EC%9D%B8%EC%8A%A4%ED%84%B4%EC%8A%A4%20%EC%A0%95%EB%B3%B4.png "EC2인스턴스 정보")

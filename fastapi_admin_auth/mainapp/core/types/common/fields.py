# from pydantic.v1 import (
#     Field,
# )
# from pydantic.v1 import Field
from pydantic import Field
import sqlalchemy as sa
import datetime as dt


__all__ = [
    "DESCField",
    "MEMField",
    "CPUField",
    "GPUField",
    "K8SNAMEField",
    "REPLICAField",
    "CONCURRENCYField",
    "NODENAMEField",
    "NODESELECTORField",
    "CANARYWEIGHTField",
    "BATCHSIZEField",
    "trim_error_msg",
    "TimestampTZField",
]


MEMField = Field(
    2,
    title="Memory 크기",
    ge=0.1,
    le=128,
    multiple_of=0.1,
)
CPUField = Field(
    1,
    title="CPU 크기",
    ge=0.1,
    le=64,
    multiple_of=0.1,
)
GPUField = Field(
    0,
    title="GPU 개수",
    ge=0,
    le=8,
    multiple_of=1,
)

REPLICAField = Field(
    1,
    title="replica 값",
    ge=0,
    le=10_000,
    multiple_of=1,
)

CONCURRENCYField = Field(
    100,
    title="concurrency 값",
    ge=1,
    le=10_000,
    multiple_of=1,
)

K8SNAMEField = Field(
    "",
    title="k8s namespace",
    max_length=200,
)

DESCField = Field(
    "",
    title="description text",
    max_length=2_000,
)

NODENAMEField = Field(
    None,
    title="node name",
    max_length=200,
)

NODESELECTORField = Field(
    None,
    title="nodeSelector 값",
    max_length=200,
)

CANARYWEIGHTField = Field(
    10,
    title="concurrency 값",
    ge=0,
    le=100,
    multiple_of=10,
)

BATCHSIZEField = Field(
    10,
    title="batch size",
    ge=1,
    le=100,
)


def trim_error_msg(s: str):
    return s[:10_000]

TimestampTZField = Field(
    sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    default_factory=dt.datetime.now(dt.timezone.utc),
    title="Timestamp with Timezone",
)
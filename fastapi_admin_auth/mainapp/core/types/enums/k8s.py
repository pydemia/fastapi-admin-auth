from .base import BaseEnum
from typing import Iterator, Optional, Union, List, Tuple, Dict
import pandas as pd

__all__ = [
    "ActionStatus",
    "JobResult",
    "ServiceStatus",
    "ServiceType",
    "TektonReason",
    "TektonStatus",
    # "RuntimeSummaryCategory",
    # "summarize_status",
]


class ActionStatus(BaseEnum):
    ADDED = "ADDED"
    MODIFIED = "MODIFIED"
    DELETED = "DELETED"
    ERROR = "ERROR"


class JobResult(BaseEnum):
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"

class ServiceType(BaseEnum):
    LoadBalancer = "LoadBalancer"
    NodePort = "NodePort"
    ClusterIP = "ClusterIP"

class ServiceStatus(BaseEnum):
    """THIS ORDER IS REFERENCED. DO NOT CHANGE IT.
    """
    WAITING = "WAITING"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    COMPLETED = "COMPLETED"
    DELETED = "DELETED"
    UNKNOWN = "UNKNOWN"
    ERROR = "ERROR"

class TektonReason(BaseEnum):
    """THIS ORDER IS REFERENCED. DO NOT CHANGE IT.
    """
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    RUNNING = "Running"

class TektonStatus(BaseEnum):
    TRUE = "True"
    FALSE = "False"
    UNKNOWN = "Unknown"

# class RuntimeSummaryCategory(BaseEnum):
#     ALL = "ALL"                 # All models registered (not versions): Theoretical maximum number of Endpoints
#     AVAILABLE = "AVAILABLE"     # All models deployable
#     RUNNING = "RUNNING"         # All models served
#     HEALTHY = "HEALTHY"         # All models served and working
#     WARNING = "WARNING"         # All models served and working, having minor problems (in present or future)
#     ERROR = "ERROR"             # All models serving but not working

#     def to_status(self) -> Tuple[Optional[List[ServiceStatus]], Optional[List[TektonReason]]]:
#         status: Optional[List[ServiceStatus]] = None
#         image_status: Optional[Tuple[TektonReason]] = None

#         if self == RuntimeSummaryCategory.ALL:
#             image_status = tuple(TektonReason)
#         elif self == RuntimeSummaryCategory.AVAILABLE:
#             image_status = (TektonReason.SUCCEEDED,)
#         elif self == RuntimeSummaryCategory.RUNNING:
#             status = (
#                 ServiceStatus.RUNNING,
#                 ServiceStatus.WAITING,
#                 ServiceStatus.UNKNOWN,
#                 ServiceStatus.STOPPED,
#                 ServiceStatus.COMPLETED,
#                 ServiceStatus.ERROR,
#             )
#         elif self == RuntimeSummaryCategory.HEALTHY:
#             status = (ServiceStatus.RUNNING,)
#         elif self == RuntimeSummaryCategory.WARNING:
#             status = (
#                 ServiceStatus.STOPPED,
#                 ServiceStatus.WAITING,
#                 ServiceStatus.UNKNOWN,
#             )
#         elif self == RuntimeSummaryCategory.ERROR:
#             status = (
#                 ServiceStatus.COMPLETED,
#                 ServiceStatus.ERROR,
#             )
#         return status, image_status




#     @classmethod
#     def from_status(cls,
#         model_status_agged: Iterator[Tuple[str, TektonReason, int]],
#         service_status_agged: List[Tuple[ServiceStatus, int]]
#         ) -> Dict[str, int]:

#         if not model_status_agged:
#             return {
#                 RuntimeSummaryCategory.ALL.type: 0,
#                 RuntimeSummaryCategory.AVAILABLE.type: 0,
#                 RuntimeSummaryCategory.RUNNING.type: 0,
#                 RuntimeSummaryCategory.HEALTHY.type: 0,
#                 RuntimeSummaryCategory.WARNING.type: 0,
#                 RuntimeSummaryCategory.ERROR.type: 0,
#             }

#         else:
#             model_status_agged = pd.DataFrame.from_records(
#                 model_status_agged, columns=["model_id", "image_status", "count"],
#             )
#             dtype = pd.CategoricalDtype([i.type for i in list(TektonReason)], ordered=True)
#             model_status_agged["image_status"] = model_status_agged["image_status"].astype(str).astype(dtype)
#             mdl_summary_reagged = (
#                 model_status_agged
#                 .groupby("model_id")
#                 .apply(lambda grp: grp.sort_values(by="image_status", ascending=True).head(1))
#                 .groupby("image_status")[["model_id"]]
#                 .count()
#                 .reset_index()
#                 .values.tolist()
#             )

#             mdl_summary = {k: v for k, v in mdl_summary_reagged}
#             edp_summary = {k: v for k, v in service_status_agged}

#             res = {
#                 RuntimeSummaryCategory.ALL.type: max(sum(mdl_summary.values()), 0),
#                 RuntimeSummaryCategory.AVAILABLE.type: mdl_summary.get(TektonReason.SUCCEEDED.type, 0),
#                 RuntimeSummaryCategory.RUNNING.type: max(
#                     sum(
#                         v for k, v in edp_summary.items()
#                         if k in {
#                             ServiceStatus.RUNNING,
#                             ServiceStatus.WAITING,
#                             ServiceStatus.UNKNOWN,
#                             ServiceStatus.STOPPED,
#                             ServiceStatus.COMPLETED,
#                             ServiceStatus.ERROR,
#                         }
#                     ),
#                     0),
#                 RuntimeSummaryCategory.HEALTHY.type: edp_summary.get(ServiceStatus.RUNNING, 0),
#                 RuntimeSummaryCategory.WARNING.type: max(
#                     sum(
#                         v for k, v in edp_summary.items()
#                         if k in {
#                             ServiceStatus.STOPPED,
#                             ServiceStatus.WAITING,
#                             ServiceStatus.UNKNOWN,
#                         }
#                     ),
#                     0
#                 ),
#                 RuntimeSummaryCategory.ERROR.type: max(
#                     sum(
#                         v for k, v in edp_summary.items()
#                         if k in {
#                             ServiceStatus.COMPLETED,
#                             ServiceStatus.ERROR,
#                         }
#                     ),
#                     0
#                 ),
#             }

#             return res


# def summarize_status(
#         model_status_agged: List[Tuple[TektonReason, int]],
#         service_status_agged: List[Tuple[ServiceStatus, int]]
#         ):

#     mdl_summary = {k: v for k, v in model_status_agged}
#     edp_summary = {k: v for k, v in service_status_agged}

#     return {
#         RuntimeSummaryCategory.ALL.type: max(sum(mdl_summary.values()), 0),
#         RuntimeSummaryCategory.AVAILABLE.type: mdl_summary.get(TektonReason.SUCCEEDED, 0),
#         RuntimeSummaryCategory.RUNNING.type: max(sum(edp_summary.values()), 0),
#         RuntimeSummaryCategory.HEALTHY.type: edp_summary.get(ServiceStatus.RUNNING, 0),
#         RuntimeSummaryCategory.WARNING.type: max(
#             sum(
#                 v for k, v in mdl_summary
#                 if k in {
#                     ServiceStatus.WAITING,
#                     ServiceStatus.UNKNOWN,
#                 }
#             ),
#             0
#         ),
#         RuntimeSummaryCategory.ERROR.type: max(
#             sum(
#                 v for k, v in mdl_summary
#                 if k in {
#                     ServiceStatus.STOPPED,
#                     ServiceStatus.DELETED,
#                     ServiceStatus.COMPLETED,
#                     ServiceStatus.ERROR,
#                 }
#             ),
#             0
#         ),
#     }

# _*_ coding: utf-8 _*_
from typing import Union

from enum import Enum
from .base import BaseEnum

__all__ = [
    "AirflowStatusType",
    "AirflowStatusFlag",
    "AirflowStatus",
]


class AirflowStatusType(BaseEnum):
    NONE = None
    SCHEDULED = "scheduled"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    SHUTDOWN = "shutdown"
    RESTARTING = "restarting"
    FAILED = "failed"
    SKIPPED = "skipped"
    UPSTREAM_FAILED = "upstream_failed"
    UP_FOR_RETRY = "up_for_retry"
    UP_FOR_RESCHEDULE = "up_for_reschedule"
    SENSING = "sensing"
    DEFERRED = "deferred"
    REMOVED = "removed"

    # not airflow state. only for null handling in `AirflowTaskInstance`
    DEACTIVATED = "deactivated"
    # To-do: automl case?
    AUTOML_INITIALIZED = "automl_initialized"


class AirflowStatusFlag(Enum):
    """
                      ERROR, COMPLETE, PROCESSING, INITIALIZED, PREPARED)
    DEACTIVATED = 0: (False, False,    False,      False,       False)
    QUEUED      = 1: (False, False,    False,      True,        True)
    RUNNING     = 2: (False, False,    True,       True,        True)
    SUCCESS     = 3: (False, True,     False,      True,        True)
    FAILED      = 4: (True,  False,    False,      True,        True)
    STOPPED     = 5: (False, False,    False,      True,        True)

                                                ERROR, COMPLETE, PROCESSING, INITIALIZED, PREPARED)
    AirflowStatusType.SCHEDULED.value:         (False, False,    False,      True,        True),  -> 1
    AirflowStatusType.QUEUED.value:            (False, False,    False,      True,        True),  -> 1
    AirflowStatusType.RUNNING.value:           (False, False,    True,       True,        True),  -> 2
    AirflowStatusType.UP_FOR_RETRY.value:      (False, False,    True,       True,        True),  -> 2
    AirflowStatusType.UP_FOR_RESCHEDULE.value: (False, False,    True,       True,        True),  -> 2
    AirflowStatusType.RESTARTING.value:        (False, False,    True,       True,        True),  -> 2
    AirflowStatusType.SENSING.value:           (False, False,    True,       True,        True),  -> 2
    AirflowStatusType.DEFERRED.value:          (False, False,    True,       True,        True),  -> 2
    AirflowStatusType.SUCCESS.value:           (False, True,     False,      True,        True),  -> 3
    AirflowStatusType.SHUTDOWN.value:          (False, True,     False,      True,        True),  -> 3
    AirflowStatusType.SKIPPED.value:           (False, True,     False,      True,        True),  -> 3
    AirflowStatusType.REMOVED.value:           (False, True,     False,      True,        True)   -> 3
    AirflowStatusType.SHUTDOWN.value:          (False, True,     False,      True,        True),  -> 3
    AirflowStatusType.FAILED.value:            (True,  False,    False,      True,        True),  -> 4
    AirflowStatusType.UPSTREAM_FAILED.value:   (True,  False,    False,      True,        True),  -> 4
    """
    deactivated =        0, { "error": False, "complete": False, "processing": False, "initialized": True,  "prepared": False }
    queued =             1, { "error": False, "complete": False, "processing": False, "initialized": True,  "prepared": True  }
    scheduled =          1, { "error": False, "complete": False, "processing": False, "initialized": True,  "prepared": True  }
    running =            2, { "error": False, "complete": False, "processing": True,  "initialized": True,  "prepared": True  }
    restarting =         2, { "error": False, "complete": False, "processing": True,  "initialized": True,  "prepared": True  }
    up_for_retry =       2, { "error": False, "complete": False, "processing": True,  "initialized": True,  "prepared": True  }
    up_for_reschedule =  2, { "error": False, "complete": False, "processing": True,  "initialized": True,  "prepared": True  }
    sensing =            2, { "error": False, "complete": False, "processing": True,  "initialized": True,  "prepared": True  }
    deferred =           2, { "error": False, "complete": False, "processing": True,  "initialized": True,  "prepared": True  }
    success =            3, { "error": False, "complete": True,  "processing": False, "initialized": True,  "prepared": True  }
    shutdown =           3, { "error": False, "complete": True,  "processing": False, "initialized": True,  "prepared": True  }
    skipped =            3, { "error": False, "complete": True,  "processing": False, "initialized": True,  "prepared": True  }
    removed =            3, { "error": False, "complete": True,  "processing": False, "initialized": True,  "prepared": True  }
    failed =             4, { "error": True,  "complete": False, "processing": False, "initialized": True,  "prepared": True  }
    upstream_failed =    4, { "error": True,  "complete": False, "processing": False, "initialized": True,  "prepared": True  }
    stopped =            5, { "error": False, "complete": False, "processing": False, "initialized": True,  "prepared": True  }
    # To-do: automl case?
    automl_initialized = 6, { "error": False, "complete": False, "processing": False, "initialized": True,  "prepared": False }

    def __init__(self, status_int, status_dict):
        self.status_int = status_int
        self.status_dict = status_dict

    @classmethod
    def of(cls, status_flag: Union[int, str, AirflowStatusType, "AirflowStatusFlag"]):
        if isinstance(status_flag, int):
            try:
                return [i for i in cls if i.status_int == status_flag][0]
            except IndexError:
                raise ValueError(f"'{status_flag}' is not in {cls.__name__}")    
        elif isinstance(status_flag, AirflowStatusType):
            return cls[status_flag.value]
        elif isinstance(status_flag, str):
            return cls[status_flag]
        elif isinstance(status_flag, cls):
            return status_flag
        else:
            raise ValueError(f"'{status_flag}' is not in {cls.__name__}")


class AirflowStatus(Enum):
    #              ERROR, COMPLETE, PROCESSING, INITIALIZED, PREPARED
    DEACTIVATED = (False, False,    False,      False,       False)
    QUEUED      = (False, False,    False,      True,        True)
    RUNNING     = (False, False,    True,       True,        True)
    SUCCESS     = (False, True,     False,      True,        True)
    FAILED      = (True,  False,    False,      True,        True)
    # STOPPED     = (False, False,    False,      False,       False)

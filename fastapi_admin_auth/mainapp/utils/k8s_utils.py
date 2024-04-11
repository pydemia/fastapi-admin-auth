# _*_ coding: utf-8 _*_
from autologging import logged
from kubernetes_client import KubernetesManager
from kubernetes.client.exceptions import ApiException
from kubernetes.client.models import (
    V1PersistentVolumeClaim,
    V1PersistentVolumeClaimSpec,
    V1PersistentVolume,
    V1PersistentVolumeSpec,
    V1ObjectMeta,
    V1ObjectReference,
    V1CSIPersistentVolumeSource,
    V1ResourceRequirements
)

__all__ = [
    "prepare_pv",
    "prepare_pvc"
]


@logged
def prepare_pv(
        client: KubernetesManager,
        pv_name: str,
        origin_pv_name: str,
        capacity: int = 10
) -> None:
    """PV 조회 없으면 PV 생성.
    Args:
        client:
        pv_name: pv 명
        org_pv_name: python workflow pv 명
        namespace: 네임스페이스
        capacity: 용량(Gi)
    """
    k_client = client.client
    # PV 없을 경우, PV 생성
    try:
        k_client.read_persistent_volume(name=pv_name)
    except ApiException as e:
        if e.status != 404:
            raise e
        pv: V1PersistentVolume = k_client.read_persistent_volume(name=origin_pv_name)
        new_spec: V1PersistentVolumeSpec = pv.spec
        new_spec.claim_ref = None
        new_spec.capacity = {'storage': f'{capacity}Gi'}

        k_client.create_persistent_volume(body=V1PersistentVolume(
            api_version=pv.api_version,
            kind=pv.kind,
            metadata=V1ObjectMeta(name=pv_name),
            spec=new_spec
        ))


@logged
def prepare_pvc(
        client: KubernetesManager,
        pv_name: str,
        pvc_name: str,
        namespace: str,
        origin_namespace: str = 'aiip-workflow',
        capacity: int = 10
) -> None:
    """namespace 내 PVC 조회 없으면 PVC 생성.
    Args:
        client:
        pv_name: pv 명
        pvc_name: pvc 명
        namespace: 네임스페이스
        org_namespace: python workflow 네임스페이스
        capacity: 용량(Gi)
    """
    k_client = client.client
    # namespace 내 PV 없을 경우, PV 생성
    try:
        k_client.read_namespaced_persistent_volume_claim(name=pvc_name, namespace=namespace)
    except ApiException as e:
        if e.status != 404:
            raise e
        pvc: V1PersistentVolumeClaim = k_client.read_namespaced_persistent_volume_claim(
            name=pvc_name,
            namespace=origin_namespace
        )
        new_spec: V1PersistentVolumeClaimSpec = pvc.spec
        new_spec.volume_name = pv_name
        r: V1ResourceRequirements = new_spec.resources
        r.requests = {'storage': f'{capacity}Gi'}

        k_client.create_namespaced_persistent_volume_claim(
            namespace=namespace,
            body=V1PersistentVolumeClaim(
                api_version=pvc.api_version,
                kind=pvc.kind,
                metadata=V1ObjectMeta(
                    # name=pvc_name,
                    name=pvc.metadata.name,
                    namespace=namespace
                ),
                spec=new_spec
            )
        )

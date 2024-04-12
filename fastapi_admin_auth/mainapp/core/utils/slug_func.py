from corusadmin.orchestration.models import ApiSpec


def get_info_by_slug(slug: str, **kwargs) -> str:
    api_spec = ApiSpec.objects.get(slug=slug, active=True)
    return api_spec.func_execute(**kwargs)

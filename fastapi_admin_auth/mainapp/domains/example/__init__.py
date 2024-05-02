from mainapp.core.domains import import_domain_components

(
    domain_router,
    domain_adminviews,
    domain_models,
    domain_seeds,
) = import_domain_components(__name__)

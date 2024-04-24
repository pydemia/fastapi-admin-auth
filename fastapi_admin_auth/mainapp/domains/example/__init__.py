from mainapp.core.domains import import_domain_components

domain_router, domain_adminviews, domain_models = import_domain_components(__name__)

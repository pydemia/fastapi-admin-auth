from mainapp.core.domains import import_domain_components

router, admin_views, models = import_domain_components(__name__)

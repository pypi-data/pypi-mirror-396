# flake8: noqa

if __import__("typing").TYPE_CHECKING:
    # import apis into api package
    from circle.web3.smart_contract_platform.api.deploy_import_api import DeployImportApi
    from circle.web3.smart_contract_platform.api.event_monitors_api import EventMonitorsApi
    from circle.web3.smart_contract_platform.api.interact_api import InteractApi
    from circle.web3.smart_contract_platform.api.templates_api import TemplatesApi
    from circle.web3.smart_contract_platform.api.view_update_api import ViewUpdateApi
    
else:
    from lazy_imports import LazyModule, as_package, load

    load(
        LazyModule(
            *as_package(__file__),
            """# import apis into api package
from circle.web3.smart_contract_platform.api.deploy_import_api import DeployImportApi
from circle.web3.smart_contract_platform.api.event_monitors_api import EventMonitorsApi
from circle.web3.smart_contract_platform.api.interact_api import InteractApi
from circle.web3.smart_contract_platform.api.templates_api import TemplatesApi
from circle.web3.smart_contract_platform.api.view_update_api import ViewUpdateApi

""",
            name=__name__,
            doc=__doc__,
        )
    )

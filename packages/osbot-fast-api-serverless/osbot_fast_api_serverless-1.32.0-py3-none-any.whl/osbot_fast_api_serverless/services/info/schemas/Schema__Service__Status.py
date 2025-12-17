from osbot_fast_api_serverless                                                   import package_name
from osbot_fast_api_serverless.services.info.schemas.Enum__Service_Environment   import Enum__Service_Environment
from osbot_fast_api_serverless.services.info.schemas.Enum__Service_Status        import Enum__Service_Status
from osbot_fast_api_serverless.utils.Version                                     import version__osbot_fast_api_serverless
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Version  import Safe_Str__Version
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id                import Safe_Id

class Schema__Service__Status(Type_Safe):
    name        : Safe_Id                   = Safe_Id(package_name)
    version     : Safe_Str__Version         = version__osbot_fast_api_serverless
    status      : Enum__Service_Status      = Enum__Service_Status.operational
    environment : Enum__Service_Environment = Enum__Service_Environment.local
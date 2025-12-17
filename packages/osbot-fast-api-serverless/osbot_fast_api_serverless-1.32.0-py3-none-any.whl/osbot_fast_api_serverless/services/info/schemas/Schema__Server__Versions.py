from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Version import Safe_Str__Version
from osbot_utils.utils.Version                                                  import Version as Version__OSBot_Utils
from osbot_fast_api.utils.Version                                               import version__osbot_fast_api
from osbot_fast_api_serverless.utils.Version                                    import version__osbot_fast_api_serverless


class Schema__Server__Versions(Type_Safe):
    osbot_utils                 : Safe_Str__Version       = Safe_Str__Version(Version__OSBot_Utils().value()    )
    osbot_fast_api              : Safe_Str__Version       = Safe_Str__Version(version__osbot_fast_api           )
    osbot_fast_api_serverless   : Safe_Str__Version       = Safe_Str__Version(version__osbot_fast_api_serverless)

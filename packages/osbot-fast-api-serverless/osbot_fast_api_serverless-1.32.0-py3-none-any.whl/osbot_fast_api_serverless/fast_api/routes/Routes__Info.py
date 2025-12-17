from osbot_fast_api.api.routes.Fast_API__Routes           import Fast_API__Routes
from osbot_fast_api_serverless.services.info.Service_Info import Service_Info
from osbot_fast_api_serverless.utils.Version              import version__osbot_fast_api_serverless

TAG__ROUTES_INFO                  = 'info'
ROUTES_PATHS__INFO                = [ f'/{TAG__ROUTES_INFO}/health'  ,
                                      f'/{TAG__ROUTES_INFO}/server'  ,
                                      f'/{TAG__ROUTES_INFO}/status'  ,
                                      f'/{TAG__ROUTES_INFO}/version' ,
                                      f'/{TAG__ROUTES_INFO}/versions']
ROUTES_INFO__HEALTH__RETURN_VALUE = {'status': 'ok'}

class Routes__Info(Fast_API__Routes):
    tag         : str          = 'info'
    service_info: Service_Info

    def health(self):
        return ROUTES_INFO__HEALTH__RETURN_VALUE

    def server(self):                                             # Get service versions
        return self.service_info.server_info()

    def status(self):                                               # Get service status information
        return self.service_info.service_info()

    def versions(self):                                             # Get service versions
        return self.service_info.versions()                         # todo: this should also include the version from Fast_API
                                                                    #       and see if this should not be inside the /server endpoint

    def version(self):
        return dict(version=version__osbot_fast_api_serverless )    # todo: fix this to get this value from FastAPI app object

    def setup_routes(self):
        self.add_route_get(self.health  )
        self.add_route_get(self.server  )
        self.add_route_get(self.status  )
        self.add_route_get(self.version )
        self.add_route_get(self.versions)
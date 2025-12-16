from avrs.requests.rest_request import AvrsRestApiRequest


class AvrsGetWebVizMetaRequest(AvrsRestApiRequest):
    def __init__(self, parser, cfg):
        AvrsRestApiRequest.__init__(self, parser, cfg, '/api/v1.0/get-web-viz-meta', 'GET')
        psr = parser.add_parser('get-web-viz-meta', help='get metadata from the simulator needed by the web frontend')
        psr.set_defaults(func=self.send_request)

    def get_request_params(self, args):
        return {}
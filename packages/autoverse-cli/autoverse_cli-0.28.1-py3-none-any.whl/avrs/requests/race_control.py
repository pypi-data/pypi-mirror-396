from avrs.requests.request import AvrsApiRequest
class AvrsRaceControlRequest(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'RaceControl', 'Ego')
        psr = parser.add_parser('race-control', help='send different flags to the race control')
        self.sector_number = 3  # Assuming there are 3 sectors; adjust as necessary, constant for now

        psr.add_argument(
            '--session-type', 
            type=int, 
            default=-1,
            help='the id of the session type to set')

        psr.add_argument(
            '--track-flag', 
            type=int, 
            default=-1,
            help='the id of the track flag to set')

        psr.add_argument(
            '--car-flag', 
            type=int, 
            default=-1,
            help='the id of the car flag to set')
        
        psr.add_argument(
            '--sector-flag',
            nargs=self.sector_number, 
            type=int,
            default=[-1, -1, -1],
            help='the ids of the sector flags to set, provide 3 values for sector 1, sector 2 and sector 3 in that order')

        psr.add_argument(
            '--object-name', 
            default='Ego', 
            help='the name of the car to set flags on')


        psr.set_defaults(func=self.send_request)

    def get_request_body(self, args):
        self.target_object_id = args.object_name
        return {
            'sessionType': args.session_type,
            'trackFlag': args.track_flag,
            'carFlag': args.car_flag,
            'sectorFlag': args.sector_flag
        }
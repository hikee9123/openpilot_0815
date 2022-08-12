from common.params import Params

# Map query config



QUERY_RADIUS = int( Params().get("OpkrOSM_QUERY_RADIUS", encoding="utf8") )   # def: 3000  # mts. Radius to use on OSM data queries.
MIN_DISTANCE_FOR_NEW_QUERY = int( Params().get("OpkrOSM_MIN_DISTANCE_FOR_NEW_QUERY", encoding="utf8") ) # 1000  # mts. Minimum distance to query area edge before issuing a new query.
FULL_STOP_MAX_SPEED = float( Params().get("OpkrOSM_FULL_STOP_MAX_SPEED", encoding="utf8") ) # 1.39  # m/s Max speed for considering car is stopped.
LOOK_AHEAD_HORIZON_TIME =  float( Params().get("OpkrOSM_LOOK_AHEAD_HORIZON_TIME", encoding="utf8") )  #15.  # s. Time horizon for look ahead of turn speed sections to provide on liveMapData msg.
LANE_WIDTH = float( Params().get("OpkrOSM_LANE_WIDTH", encoding="utf8") )   #3.7  # Lane width estimate. Used for detecting departures from way.
PRE_LANE_DISTANCE = float( Params().get("OpkrOSM_PRE_LANE_DISTANCE", encoding="utf8") ) # 100.  #  1 about 1M distance
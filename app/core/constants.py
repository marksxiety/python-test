"""Geospatial constants shared by request validation and distance queries."""

# Mean radius of the Earth in kilometres, used by the haversine formula.
EARTH_RADIUS_KM = 6371.0088

# Approximate length of one degree of latitude in kilometres.
KM_PER_DEGREE_LATITUDE = 111.32

# Half of the Earth's circumference: no point can be farther away than this.
MAX_SEARCH_DISTANCE_KM = 20015.0

from .models import Airport, Runway
from .core.airports import get as get_airport, get_by_iata, get_by_icao, search_by_name as search_airports_by_name
from .core.distance import distance, distance_km, distance_mi, distance_nmi
from .core.geodesy import initial_bearing, midpoint, great_circle_path
from .core.search import nearest_airport, nearest_airports, airports_within_radius
from .core.routing import estimate_flight_time_hours as estimate_flight_time, route_distance
from .core.emissions import estimate_co2_kg_by_codes as estimate_co2_kg_for_segment
from .core.weather import get_metar, get_taf
from .core.runways import (
    get_runways_by_airport,
    get_longest_runway,
    get_paved_runways,
)
from .core.statistics import (
    get_country_stats,
    get_continent_stats,
    get_global_stats,
    get_top_countries_by_airports,
    get_top_countries_by_large_airports,
)
from .exceptions import (
    AeroNavXError,
    AirportNotFoundError,
    InvalidAirportCodeError,
    DataLoadError,
    RoutingError,
    WeatherDataError,
)


__version__ = "0.3.1"

__all__ = [
    "Airport",
    "Runway",
    "get_airport",
    "get_by_iata",
    "get_by_icao",
    "distance",
    "distance_km",
    "distance_mi",
    "distance_nmi",
    "initial_bearing",
    "midpoint",
    "great_circle_path",
    "nearest_airport",
    "nearest_airports",
    "airports_within_radius",
    "estimate_flight_time",
    "route_distance",
    "estimate_co2_kg_for_segment",
    "search_airports_by_name",
    "get_metar",
    "get_taf",
    "get_runways_by_airport",
    "get_longest_runway",
    "get_paved_runways",
    "get_country_stats",
    "get_continent_stats",
    "get_global_stats",
    "get_top_countries_by_airports",
    "get_top_countries_by_large_airports",
    "AeroNavXError",
    "AirportNotFoundError",
    "InvalidAirportCodeError",
    "DataLoadError",
    "RoutingError",
    "WeatherDataError",
]

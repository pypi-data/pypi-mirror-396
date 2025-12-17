# AeroNavX

A production-grade Python library for airport data and flight geometry calculations.

**🆕 v0.2.0:** Now with **84,000+ airports** from [OurAirports](https://ourairports.com) (MIT License)

## Features

- 🛫 **Airport Database**: 84,000+ global airports with efficient IATA/ICAO indexing
- 📏 **Distance Calculations**: Haversine, Vincenty, and Spherical Law of Cosines
- 🌍 **Geodesy**: Bearings, midpoints, great circle paths
- 🔍 **Search**: Fuzzy name search, nearest neighbor queries, radius search
- 🛤️ **Routing**: Multi-segment routes, flight time estimation, shortest paths
- 📊 **Analytics**: Statistics by country, continent, type, and elevation
- ⏰ **Timezone Support**: Automatic timezone detection and local time
- 🌱 **Emissions**: CO2 emissions estimation per passenger
- 🌤️ **Weather**: METAR and TAF data fetching
- 💻 **CLI**: Command-line interface for quick queries
- 🌐 **REST API**: FastAPI-based web service

## Installation

```bash
pip install aeronavx
```

**Or from source:**
```bash
git clone https://github.com/teyfikoz/AeroNavX.git
cd AeroNavX
pip install -e .
```

## Quick Start

```python
import aeronavx

# Get airports
ist = aeronavx.get_airport("IST")
jfk = aeronavx.get_airport("JFK")

# Calculate distance
dist_km = ist.distance_to(jfk)
print(f"Distance: {dist_km:.2f} km")

# Find nearest airports
nearest = aeronavx.nearest_airport(41.0, 29.0, n=5)

# Estimate emissions
co2 = aeronavx.estimate_co2_kg_for_segment("IST", "JFK")
print(f"CO2: {co2:.2f} kg per passenger")
```

### Advanced: Filtering Airports

```python
from aeronavx.core import loader

# Load only major airports (large + medium with scheduled service)
major_airports = loader.load_airports(
    include_types=['large_airport', 'medium_airport'],
    scheduled_service_only=True
)
print(f"Major airports: {len(major_airports):,}")  # ~3,200

# Load specific countries
us_airports = loader.load_airports(countries=['US'])
print(f"US airports: {len(us_airports):,}")  # ~20,000

# Load airports with IATA codes only
iata_airports = loader.load_airports(has_iata_only=True)
print(f"IATA airports: {len(iata_airports):,}")  # ~9,000
```

## CLI Usage

```bash
# Calculate distance
aeronavx distance --from IST --to JFK --unit nmi

# Find nearest airports
aeronavx nearest --lat 41.0 --lon 29.0 --n 5

# Search by name
aeronavx search --name "Heathrow"

# Estimate emissions
aeronavx emissions --from IST --to LHR

# Flight time
aeronavx flight-time --from IST --to JFK
```

## API Server

```bash
python -m aeronavx.api.server
```

Then access:
- http://localhost:8000/health
- http://localhost:8000/airport/IST
- http://localhost:8000/distance?from=IST&to=JFK
- http://localhost:8000/nearest?lat=41.0&lon=29.0&n=5

## Data

AeroNavX includes **84,000+ airports** from [OurAirports](https://ourairports.com/data/), which provides:
- ✅ **Global Coverage**: Airports, heliports, seaplane bases, and more
- ✅ **MIT License**: Free to use commercially
- ✅ **Regular Updates**: Community-maintained and updated
- ✅ **Comprehensive Data**: IATA/ICAO codes, coordinates, types, and more

**Data Attribution:**
Airport data from [OurAirports](https://ourairports.com) (David Megginson et al.) - Licensed under [MIT License](https://github.com/davidmegginson/ourairports-data)

## Examples

See `examples/` directory for:
- `basic_distance.py`: Distance calculations
- `nearest_airports.py`: Finding nearby airports
- `routing_example.py`: Multi-segment routes
- `emissions_example.py`: CO2 estimation

## Testing

```bash
pytest
```

## Dependencies

**Required**: Python >= 3.10

**Optional**:
- `pandas`: DataFrame support
- `scipy`: Faster spatial indexing
- `rapidfuzz`: Better fuzzy search
- `timezonefinder`: Timezone support
- `fastapi`, `uvicorn`: API server
- `requests`: Weather data

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or pull request.

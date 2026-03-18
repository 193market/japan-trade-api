# Japan Trade Data API

Japan international trade data including exports, imports, trade balance, merchandise trade, FDI inflows/outflows, and trade openness. Powered by World Bank Open Data.

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | API info and available endpoints |
| `GET /summary` | All trade indicators snapshot |
| `GET /exports` | Exports of goods & services (USD) |
| `GET /imports` | Imports of goods & services (USD) |
| `GET /trade-balance` | Current account balance |
| `GET /trade-openness` | Trade as % of GDP |
| `GET /merchandise` | Merchandise exports & imports |
| `GET /fdi` | FDI inflows and outflows |
| `GET /current-account` | Current account balance (BoP) |

## Data Source

World Bank Open Data
https://data.worldbank.org/country/JP

## Authentication

Requires `X-RapidAPI-Key` header via RapidAPI.

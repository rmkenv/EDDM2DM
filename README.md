# High-Income Address Finder

This tool helps you identify residential and commercial addresses in high-income areas based on demographic data. It analyzes carrier route income data and cross-references it with property address databases to create targeted address lists.

## Configuration

The tool uses two configuration files:

1. `zip_codes_config.json` - Specifies which ZIP codes to analyze
2. `gis_services_config.json` - Configures GIS service endpoints for address and demographic data

### ZIP Codes Configuration

Edit `zip_codes_config.json` to specify which ZIP codes you want to analyze:

```json
{
  "zip_codes": ["21227", "21228", "21229"],
  "description": "ZIP codes to analyze for high-income areas",
  "last_updated": "2023-05-03"
}
```

### GIS Services Configuration

Edit `gis_services_config.json` to configure your GIS service endpoints:

```json
{
  "address_services": [
    {
      "name": "Your Address Service",
      "url": "https://your-gis-server.com/arcgis/rest/services/Addresses/MapServer/0/query",
      "query_params": {
        "where": "ZIP_CODE in ({zip_codes})",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "json",
        "resultRecordCount": 3000
      },
      "field_mappings": {
        "address": "FULL_ADDRESS",
        "street_number": "HOUSE_NUMBER",
        "street_name": "STREET_NAME",
        "street_type": "STREET_TYPE",
        "city": "CITY_NAME",
        "zip": "ZIP_CODE",
        "use": "PROPERTY_USE",
        "latitude": "LATITUDE",
        "longitude": "LONGITUDE"
      }
    }
  ],
  "eddm_services": [
    {
      "name": "EDDM Carrier Routes",
      "url": "https://emapdata.adc4gis.com/routes",
      "query_params": {
        "zips": "{zip_codes}"
      },
      "field_mappings": {
        "zip": "zip",
        "route_id": "zipcrid",
        "income_avg": "inc_avg",
        "pct_inc_gte_100k": "inc_gte_100k"
      }
    }
  ]
}
```

## Usage

Run the `high_income_address_finder()` function to analyze the configured ZIP codes and generate a list of addresses in high-income areas.

```python
from high_income_finder import high_income_address_finder

# Run with default configuration files
addresses = high_income_address_finder()

# Or specify custom configuration files
addresses = high_income_address_finder(
    zip_codes_file='my_zip_codes.json',
    gis_services_file='my_gis_services.json'
)
```

## Output Files

The tool generates several output files:

- `high_income_addresses_final.csv/.xlsx` - Complete table of addresses in high-income areas
- `high_income_streets_summary.csv/.xlsx` - Summary of streets in high-income areas
- `income_distribution_routes.png` - Histogram of income distribution
- `address_income_distribution.png` - Distribution of addresses by income
- `property_use_distribution.png` - Breakdown of property types

## Requirements

- Python 3.6+
- pandas
- numpy
- matplotlib
- requests
- openpyxl (for Excel output)

## Customization

You can customize the tool by:

1. Adding your own ZIP codes to analyze
2. Configuring your own GIS services for address data
3. Adjusting the income threshold for "high-income" classification
4. Modifying the field mappings to match your data sources

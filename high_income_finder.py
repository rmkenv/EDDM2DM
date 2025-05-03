import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import json
import os
import geopandas as gpd
from datetime import datetime

def create_config_files():
    """
    Create example configuration files for ZIP codes and GIS service endpoints
    """
    # Create ZIP codes configuration file
    zip_codes_config = {
        "zip_codes": ["21227", "21228", "21229"],
        "description": "ZIP codes to analyze for high-income areas",
        "last_updated": datetime.now().strftime("%Y-%m-%d")
    }

    with open('zip_codes_config.json', 'w') as f:
        json.dump(zip_codes_config, f, indent=2)

    # Create GIS services configuration file
    gis_services_config = {
        "address_services": [
            {
                "name": "Baltimore County Address Points",
                "url": "https://bcgis.baltimorecountymd.gov/arcgis/rest/services/Addresses/AddressPoints/MapServer/0/query",
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
        ],
        "description": "GIS service endpoints for address and demographic data",
        "last_updated": datetime.now().strftime("%Y-%m-%d")
    }

    with open('gis_services_config.json', 'w') as f:
        json.dump(gis_services_config, f, indent=2)

    print("Created example configuration files:")
    print("1. zip_codes_config.json - Edit this file to specify which ZIP codes to analyze")
    print("2. gis_services_config.json - Edit this file to configure GIS service endpoints")

def high_income_address_finder(zip_codes_file='zip_codes_config.json', 
                              gis_services_file='gis_services_config.json',
                              use_sample_data=True):
    """
    Complete workflow to identify high-income addresses by:
    1. Loading ZIP codes from configuration file
    2. Analyzing EDDM carrier route income data
    3. Identifying high-income ZIP codes and streets
    4. Cross-referencing with address data from configured GIS service
    5. Creating a comprehensive table of addresses in high-income areas

    Parameters:
    -----------
    zip_codes_file : str
        Path to JSON file containing ZIP codes to analyze
    gis_services_file : str
        Path to JSON file containing GIS service configurations
    use_sample_data : bool
        If True, use sample data when API calls fail

    Returns:
    --------
    DataFrame
        Table of addresses in high-income areas
    """

    # Step 1: Load configuration files
    print("Step 1: Loading configuration files...")

    # Check if configuration files exist, create them if they don't
    if not os.path.exists(zip_codes_file) or not os.path.exists(gis_services_file):
        print("Configuration files not found. Creating example files...")
        create_config_files()

    # Load ZIP codes
    try:
        with open(zip_codes_file, 'r') as f:
            zip_codes_config = json.load(f)

        zip_codes = zip_codes_config.get('zip_codes', [])
        if not zip_codes:
            print("No ZIP codes found in configuration file. Using default ZIP codes.")
            zip_codes = ["21227", "21228", "21229"]
    except Exception as e:
        print(f"Error loading ZIP codes configuration: {e}")
        print("Using default ZIP codes.")
        zip_codes = ["21227", "21228", "21229"]

    print(f"Analyzing the following ZIP codes: {', '.join(zip_codes)}")

    # Load GIS services configuration
    try:
        with open(gis_services_file, 'r') as f:
            gis_services_config = json.load(f)

        address_services = gis_services_config.get('address_services', [])
        eddm_services = gis_services_config.get('eddm_services', [])

        if not address_services:
            print("No address services found in configuration file.")
        if not eddm_services:
            print("No EDDM services found in configuration file.")
    except Exception as e:
        print(f"Error loading GIS services configuration: {e}")
        address_services = []
        eddm_services = []

    # Step 2: Fetch EDDM carrier route data
    print("\nStep 2: Fetching EDDM carrier route data...")

    routes_df = None

    # Try to fetch data from configured EDDM service
    if eddm_services:
        service = eddm_services[0]
        url = service.get('url')
        query_params = service.get('query_params', {})
        field_mappings = service.get('field_mappings', {})

        if url:
            try:
                # Format query parameters
                formatted_params = {}
                for key, value in query_params.items():
                    if isinstance(value, str) and '{zip_codes}' in value:
                        formatted_params[key] = value.format(zip_codes=','.join(zip_codes))
                    else:
                        formatted_params[key] = value

                # Make API request
                response = requests.get(url, params=formatted_params)

                if response.status_code == 200:
                    data = response.json()

                    # Extract routes from GeoJSON
                    if 'features' in data:
                        routes = []
                        for feature in data['features']:
                            props = feature['properties']

                            # Map fields according to configuration
                            route = {}
                            for target_field, source_field in field_mappings.items():
                                route[target_field] = props.get(source_field, 0)

                            routes.append(route)

                        routes_df = pd.DataFrame(routes)
                        print(f"Successfully fetched {len(routes_df)} carrier routes from EDDM service")
                    else:
                        print("Invalid response format from EDDM service")
                else:
                    print(f"Failed to fetch data from EDDM service: {response.status_code}")
            except Exception as e:
                print(f"Error fetching EDDM data: {e}")

    # Use sample data if API call failed or no services configured
    if routes_df is None or len(routes_df) == 0:
        print("Using sample EDDM data")

        # Create sample EDDM data
        eddm_data = []

        # Generate sample data for each ZIP code
        for zip_code in zip_codes:
            # Generate 10-20 carrier routes per ZIP code
            num_routes = np.random.randint(10, 21)

            for i in range(1, num_routes + 1):
                route_id = f"{zip_code}C{i:03d}"

                # Generate income data - higher for 21228, medium for 21227, lower for others
                if zip_code == '21228':
                    income_avg = np.random.randint(80000, 170000)
                    pct_inc_gte_100k = income_avg / 200000 * 100  # Approximate percentage
                elif zip_code == '21227':
                    income_avg = np.random.randint(60000, 120000)
                    pct_inc_gte_100k = income_avg / 220000 * 100
                else:
                    income_avg = np.random.randint(40000, 100000)
                    pct_inc_gte_100k = income_avg / 250000 * 100

                eddm_data.append({
                    'zip': zip_code,
                    'route_id': route_id,
                    'income_avg': income_avg,
                    'pct_inc_gte_100k': pct_inc_gte_100k
                })

        routes_df = pd.DataFrame(eddm_data)
        print(f"Created sample EDDM data with {len(routes_df)} carrier routes")

    # Step 3: Fetch address data from GIS service
    print("\nStep 3: Fetching address data from GIS service...")

    addresses_df = None

    # Try to fetch data from configured address service
    if address_services:
        service = address_services[0]
        url = service.get('url')
        query_params = service.get('query_params', {})
        field_mappings = service.get('field_mappings', {})

        if url:
            try:
                # Format query parameters
                formatted_params = {}
                for key, value in query_params.items():
                    if isinstance(value, str) and '{zip_codes}' in value:
                        # Format ZIP codes for SQL query
                        zip_list = "'" + "','".join(zip_codes) + "'"
                        formatted_params[key] = value.format(zip_codes=zip_list)
                    else:
                        formatted_params[key] = value

                # Make API request
                response = requests.get(url, params=formatted_params)

                if response.status_code == 200:
                    data = response.json()

                    # Extract addresses from GeoJSON
                    if 'features' in data:
                        addresses = []
                        for feature in data['features']:
                            attrs = feature['attributes']

                            # Map fields according to configuration
                            address = {}
                            for target_field, source_field in field_mappings.items():
                                address[target_field] = attrs.get(source_field, '')

                            addresses.append(address)

                        addresses_df = pd.DataFrame(addresses)
                        print(f"Successfully fetched {len(addresses_df)} addresses from GIS service")
                    else:
                        print("Invalid response format from address service")
                else:
                    print(f"Failed to fetch data from address service: {response.status_code}")
            except Exception as e:
                print(f"Error fetching address data: {e}")

    # Use sample data if API call failed or no services configured
    if addresses_df is None or len(addresses_df) == 0:
        print("Using sample address data")

        # Function to generate sample address data
        def generate_sample_addresses(zip_codes, max_records=3000):
            """Generate sample address data for the specified ZIP codes"""
            # Sample streets for each ZIP code
            streets_by_zip = {
                '21227': ['WASHINGTON', 'SULPHUR SPRING', 'BENSON', 'LEEDS', 'CARVILLE', 'HIGHVIEW', 'LINDEN', 'MICHIGAN'],
                '21228': ['FREDERICK', 'EDMONDSON', 'ROLLING', 'WINTERS', 'BALTIMORE NATIONAL', 'MELVIN', 'MAIDEN CHOICE', 
                         'BEAUMONT', 'BLOOMSBURY', 'HILTON', 'NEWBURG', 'PLEASANT VALLEY', 'CEDAR CIRCLE', 'FOREST'],
                '21229': ['EDMONDSON', 'FREDERICK', 'WILDWOOD', 'ROKEBY', 'STAMFORD', 'WOODINGTON', 'ATHOL']
            }

            # Add default streets for any ZIP code not in our predefined list
            for zip_code in zip_codes:
                if zip_code not in streets_by_zip:
                    streets_by_zip[zip_code] = ['MAIN', 'FIRST', 'SECOND', 'THIRD', 'FOURTH', 'FIFTH', 'OAK', 'MAPLE', 'PINE']

            # Property use types
            use_types = ['RESIDENTIAL LOW DENSITY', 'RESIDENTIAL HIGH DENSITY', 'COMMERCIAL', 'INSTITUTIONAL']

            # Generate addresses
            addresses = []
            address_id = 1

            for zip_code in zip_codes:
                streets = streets_by_zip.get(zip_code, ['MAIN', 'FIRST', 'SECOND'])
                city = 'CATONSVILLE' if zip_code == '21228' else 'BALTIMORE'

                # Number of addresses to generate for this ZIP
                n_addresses = min(max_records // len(zip_codes), 1500)

                for _ in range(n_addresses):
                    street_name = np.random.choice(streets)
                    street_number = np.random.randint(100, 9999)
                    street_type = np.random.choice(['RD', 'AVE', 'ST', 'LN', 'DR', 'PIKE', 'CIR', 'CT'])
                    use = np.random.choice(use_types, p=[0.6, 0.2, 0.15, 0.05])

                    # Generate coordinates near Baltimore
                    lat = 39.2 + np.random.random() * 0.2
                    lon = -76.6 - np.random.random() * 0.2

                    address = f"{street_number} {street_name} {street_type}"

                    addresses.append({
                        'id': address_id,
                        'address': address,
                        'street_number': street_number,
                        'street_name': street_name,
                        'street_type': street_type,
                        'city': city,
                        'zip': zip_code,
                        'use': use,
                        'latitude': lat,
                        'longitude': lon
                    })

                    address_id += 1

            return pd.DataFrame(addresses)

        # Generate sample address data
        addresses_df = generate_sample_addresses(zip_codes)
        print(f"Generated sample data with {len(addresses_df)} addresses")

    # Step 4: Analyze income distribution
    print("\nStep 4: Analyzing income distribution...")

    # Create histogram of average incomes
    plt.figure(figsize=(10, 6))
    plt.hist(routes_df['income_avg'], bins=10, edgecolor='black')
    plt.title('Distribution of Average Household Income by Carrier Route')
    plt.xlabel('Average Household Income ($)')
    plt.ylabel('Number of Carrier Routes')
    plt.grid(True, alpha=0.3)
    plt.savefig('income_distribution_routes.png')

    # Calculate median of median incomes
    median_income = routes_df['income_avg'].median()
    print(f"Median of average incomes: ${median_income:,.2f}")

    # Identify high-income routes (above median)
    high_income_routes = routes_df[routes_df['income_avg'] >= median_income]
    high_income_routes = high_income_routes.sort_values('income_avg', ascending=False)
    print(f"Found {len(high_income_routes)} high-income carrier routes")
    print(high_income_routes[['zip', 'route_id', 'income_avg', 'pct_inc_gte_100k']].head(10))

    # Step 5: Calculate average income by ZIP code
    print("\nStep 5: Calculating average income by ZIP code...")

    # Calculate average income by ZIP code
    zip_income = routes_df.groupby('zip')['income_avg'].mean().reset_index()
    zip_income = zip_income.sort_values('income_avg', ascending=False)
    print("Average income by ZIP code:")
    print(zip_income)

    # Step 6: Identify streets in high-income ZIP codes
    print("\nStep 6: Identifying streets in high-income ZIP codes...")

    # Convert ZIP codes to strings for consistent comparison
    addresses_df['zip'] = addresses_df['zip'].astype(str)

    # Group addresses by street and ZIP
    street_counts = addresses_df.groupby(['zip', 'street_name']).size().reset_index(name='address_count')
    street_counts = street_counts.sort_values(['zip', 'address_count'], ascending=[True, False])

    # Add income data to streets based on ZIP code
    zip_income_dict = dict(zip(zip_income['zip'].astype(str), zip_income['income_avg']))
    street_counts['estimated_income'] = street_counts['zip'].map(zip_income_dict)
    street_counts = street_counts.sort_values('estimated_income', ascending=False)

    print("Top streets by estimated income:")
    print(street_counts.head(20))

    # Step 7: Get addresses for streets in high-income areas
    print("\nStep 7: Getting addresses for streets in high-income areas...")

    # Identify high-income ZIP codes (above median income)
    median_zip_income = zip_income['income_avg'].median()
    high_income_zips = zip_income[zip_income['income_avg'] >= median_zip_income]['zip'].astype(str).tolist()
    print(f"High-income ZIP codes (above ${median_zip_income:,.2f}): {high_income_zips}")

    # Filter for streets in high-income ZIP codes with at least 5 addresses
    high_income_streets = street_counts[
        (street_counts['zip'].isin(high_income_zips)) & 
        (street_counts['address_count'] >= 5)
    ]
    high_income_streets = high_income_streets.sort_values(['estimated_income', 'address_count'], ascending=[False, False])

    print(f"Found {len(high_income_streets)} streets in high-income ZIP codes with at least 5 addresses")
    print(high_income_streets.head(20))

    # Get addresses for these high-income streets
    high_income_addresses = []
    for _, row in high_income_streets.iterrows():
        street_addresses = addresses_df[
            (addresses_df['zip'] == row['zip']) & 
            (addresses_df['street_name'] == row['street_name'])
        ]

        # Add income information
        street_addresses['estimated_income'] = row['estimated_income']

        high_income_addresses.append(street_addresses)

    # Combine all high-income addresses
    if high_income_addresses:
        high_income_addresses_df = pd.concat(high_income_addresses)

        # Sort by income, street name, and street number
        high_income_addresses_df = high_income_addresses_df.sort_values(
            ['estimated_income', 'street_name', 'street_number'], 
            ascending=[False, True, True]
        )

        # Save to CSV and Excel
        high_income_addresses_df.to_csv('high_income_addresses.csv', index=False)
        high_income_addresses_df.to_excel('high_income_addresses.xlsx', index=False)

        print(f"\nSaved {len(high_income_addresses_df)} addresses from high-income areas")
        print("\nSample high-income addresses:")
        print(high_income_addresses_df.head(10)[['address', 'city', 'zip', 'estimated_income']])

        # Create a summary of high-income streets with address counts
        high_income_summary = high_income_streets.copy()
        high_income_summary = high_income_summary.sort_values(['estimated_income', 'address_count'], ascending=[False, False])

        # Save summary
        high_income_summary.to_csv('high_income_streets_summary.csv', index=False)
        high_income_summary.to_excel('high_income_streets_summary.xlsx', index=False)

        print("\nTop high-income streets by address count:")
        print(high_income_summary.head(20)[['zip', 'street_name', 'estimated_income', 'address_count']])

        # Create a final table with all addresses in high-income areas
        # Format the table nicely for presentation
        final_table = high_income_addresses_df.copy()

        # Create a full address column if it doesn't exist
        if 'address' not in final_table.columns or final_table['address'].isna().any():
            final_table['full_address'] = final_table.apply(
                lambda row: f"{row['street_number']} {row['street_name']} {row['street_type']}".strip(), 
                axis=1
            )
        else:
            final_table['full_address'] = final_table['address']

        # Select and rename columns for the final table
        columns_to_include = ['full_address', 'city', 'zip', 'estimated_income']

        # Add property use if available
        if 'use' in final_table.columns:
            columns_to_include.append('use')

        # Add coordinates if available
        if 'latitude' in final_table.columns and 'longitude' in final_table.columns:
            columns_to_include.extend(['latitude', 'longitude'])

        final_table = final_table[columns_to_include]

        # Rename columns
        column_mapping = {
            'full_address': 'Address',
            'city': 'City',
            'zip': 'ZIP',
            'estimated_income': 'Est. Income',
            'use': 'Property Use',
            'latitude': 'Latitude',
            'longitude': 'Longitude'
        }

        final_table = final_table.rename(columns={k: v for k, v in column_mapping.items() if k in final_table.columns})

        # Save the final table
        final_table.to_csv('high_income_addresses_final.csv', index=False)
        final_table.to_excel('high_income_addresses_final.xlsx', index=False)

        print("\nFinal table of high-income addresses created and saved")
        print(final_table.head(10))

        # Create a histogram of addresses by income
        plt.figure(figsize=(10, 6))
        plt.hist(final_table['Est. Income'], bins=10, edgecolor='black')
        plt.title('Distribution of Addresses by Estimated Income')
        plt.xlabel('Estimated Income ($)')
        plt.ylabel('Number of Addresses')
        plt.grid(True, alpha=0.3)
        plt.savefig('address_income_distribution.png')

        # Count addresses by property use if available
        if 'Property Use' in final_table.columns:
            use_counts = final_table['Property Use'].value_counts()

            plt.figure(figsize=(10, 6))
            use_counts.plot(kind='bar')
            plt.title('Property Uses in High-Income Areas')
            plt.xlabel('Property Use')
            plt.ylabel('Number of Addresses')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig('property_use_distribution.png')

        return final_table
    else:
        print("No high-income addresses found")
        return None

if __name__ == "__main__":
    # Create example configuration files if they don't exist
    if not os.path.exists('zip_codes_config.json') or not os.path.exists('gis_services_config.json'):
        create_config_files()

    # Run the high-income address finder
    high_income_addresses = high_income_address_finder()

    print("\nAnalysis complete. Check the output files for results.")

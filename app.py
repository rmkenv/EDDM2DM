import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import json
import os

def high_income_address_finder():
    """
    Complete workflow to identify high-income addresses by:
    1. Analyzing EDDM carrier route income data
    2. Identifying high-income ZIP codes and streets
    3. Cross-referencing with Baltimore County GIS address data
    4. Creating a comprehensive table of addresses in high-income areas
    """
    
    # Step 1: Load or create the necessary data
    print("Step 1: Loading and preparing data...")
    
    # Sample EDDM carrier route data with income information
    eddm_data = [
        {'zip': '21227', 'route_id': '21227C002', 'income_avg': 56642, 'pct_inc_gte_100k': 22.69},
        {'zip': '21227', 'route_id': '21227C003', 'income_avg': 79018, 'pct_inc_gte_100k': 33.58},
        {'zip': '21227', 'route_id': '21227C005', 'income_avg': 86972, 'pct_inc_gte_100k': 40.41},
        {'zip': '21227', 'route_id': '21227C007', 'income_avg': 48929, 'pct_inc_gte_100k': 17.87},
        {'zip': '21227', 'route_id': '21227C008', 'income_avg': 39207, 'pct_inc_gte_100k': 15.31},
        {'zip': '21227', 'route_id': '21227C009', 'income_avg': 106618, 'pct_inc_gte_100k': 54.62},
        {'zip': '21227', 'route_id': '21227C011', 'income_avg': 81604, 'pct_inc_gte_100k': 36.25},
        {'zip': '21227', 'route_id': '21227C016', 'income_avg': 112054, 'pct_inc_gte_100k': 58.26},
        {'zip': '21227', 'route_id': '21227C017', 'income_avg': 96974, 'pct_inc_gte_100k': 48.25},
        {'zip': '21227', 'route_id': '21227C023', 'income_avg': 79775, 'pct_inc_gte_100k': 37.56},
        {'zip': '21227', 'route_id': '21227C029', 'income_avg': 89410, 'pct_inc_gte_100k': 42.19},
        {'zip': '21227', 'route_id': '21227C031', 'income_avg': 105000, 'pct_inc_gte_100k': 52.81},
        {'zip': '21227', 'route_id': '21227C033', 'income_avg': 82692, 'pct_inc_gte_100k': 37.35},
        {'zip': '21227', 'route_id': '21227C036', 'income_avg': 117500, 'pct_inc_gte_100k': 59.74},
        {'zip': '21227', 'route_id': '21227C042', 'income_avg': 107656, 'pct_inc_gte_100k': 55.49},
        {'zip': '21227', 'route_id': '21227C045', 'income_avg': 110340, 'pct_inc_gte_100k': 57.00},
        {'zip': '21227', 'route_id': '21227C052', 'income_avg': 89130, 'pct_inc_gte_100k': 42.42},
        {'zip': '21228', 'route_id': '21228C001', 'income_avg': 77412, 'pct_inc_gte_100k': 37.29},
        {'zip': '21228', 'route_id': '21228C002', 'income_avg': 164583, 'pct_inc_gte_100k': 73.28},
        {'zip': '21228', 'route_id': '21228C003', 'income_avg': 94776, 'pct_inc_gte_100k': 46.62},
        {'zip': '21228', 'route_id': '21228C004', 'income_avg': 79367, 'pct_inc_gte_100k': 38.30},
        {'zip': '21228', 'route_id': '21228C006', 'income_avg': 135417, 'pct_inc_gte_100k': 64.03},
        {'zip': '21228', 'route_id': '21228C007', 'income_avg': 100000, 'pct_inc_gte_100k': 50.00},
        {'zip': '21228', 'route_id': '21228C008', 'income_avg': 82237, 'pct_inc_gte_100k': 41.07},
        {'zip': '21228', 'route_id': '21228C009', 'income_avg': 102632, 'pct_inc_gte_100k': 51.60},
        {'zip': '21228', 'route_id': '21228C011', 'income_avg': 135985, 'pct_inc_gte_100k': 64.72},
        {'zip': '21228', 'route_id': '21228C012', 'income_avg': 108750, 'pct_inc_gte_100k': 54.95},
        {'zip': '21228', 'route_id': '21228C014', 'income_avg': 118008, 'pct_inc_gte_100k': 60.09},
        {'zip': '21228', 'route_id': '21228C015', 'income_avg': 100391, 'pct_inc_gte_100k': 50.18},
        {'zip': '21228', 'route_id': '21228C016', 'income_avg': 98289, 'pct_inc_gte_100k': 48.84},
        {'zip': '21228', 'route_id': '21228C017', 'income_avg': 105938, 'pct_inc_gte_100k': 52.94},
        {'zip': '21228', 'route_id': '21228C018', 'income_avg': 105804, 'pct_inc_gte_100k': 52.22},
        {'zip': '21228', 'route_id': '21228C020', 'income_avg': 79561, 'pct_inc_gte_100k': 37.24},
        {'zip': '21228', 'route_id': '21228C024', 'income_avg': 145455, 'pct_inc_gte_100k': 67.07},
        {'zip': '21228', 'route_id': '21228C025', 'income_avg': 81442, 'pct_inc_gte_100k': 37.09},
        {'zip': '21228', 'route_id': '21228C026', 'income_avg': 96778, 'pct_inc_gte_100k': 47.59},
        {'zip': '21228', 'route_id': '21228C027', 'income_avg': 133333, 'pct_inc_gte_100k': 66.51},
        {'zip': '21228', 'route_id': '21228C028', 'income_avg': 126071, 'pct_inc_gte_100k': 61.02},
        {'zip': '21228', 'route_id': '21228C029', 'income_avg': 117424, 'pct_inc_gte_100k': 57.72},
        {'zip': '21228', 'route_id': '21228C032', 'income_avg': 81667, 'pct_inc_gte_100k': 39.25},
        {'zip': '21228', 'route_id': '21228C035', 'income_avg': 113988, 'pct_inc_gte_100k': 56.30},
        {'zip': '21228', 'route_id': '21228C036', 'income_avg': 87838, 'pct_inc_gte_100k': 42.53},
        {'zip': '21228', 'route_id': '21228C037', 'income_avg': 84698, 'pct_inc_gte_100k': 39.59},
        {'zip': '21228', 'route_id': '21228C038', 'income_avg': 111029, 'pct_inc_gte_100k': 54.93},
        {'zip': '21228', 'route_id': '21228C041', 'income_avg': 111557, 'pct_inc_gte_100k': 55.14},
        {'zip': '21228', 'route_id': '21228C042', 'income_avg': 103629, 'pct_inc_gte_100k': 51.28},
        {'zip': '21228', 'route_id': '21228C045', 'income_avg': 97070, 'pct_inc_gte_100k': 48.13},
        {'zip': '21228', 'route_id': '21228C047', 'income_avg': 157576, 'pct_inc_gte_100k': 72.15},
        {'zip': '21228', 'route_id': '21228C048', 'income_avg': 144485, 'pct_inc_gte_100k': 65.60},
        {'zip': '21228', 'route_id': '21228C049', 'income_avg': 127344, 'pct_inc_gte_100k': 66.82},
        {'zip': '21228', 'route_id': '21228C050', 'income_avg': 91712, 'pct_inc_gte_100k': 44.63},
        {'zip': '21228', 'route_id': '21228C051', 'income_avg': 85563, 'pct_inc_gte_100k': 42.60},
        {'zip': '21229', 'route_id': '21229C004', 'income_avg': 89185, 'pct_inc_gte_100k': 43.78},
        {'zip': '21229', 'route_id': '21229C005', 'income_avg': 85326, 'pct_inc_gte_100k': 40.43}
    ]
    
    routes_df = pd.DataFrame(eddm_data)
    print(f"Created EDDM data with {len(routes_df)} carrier routes")
    
    # Function to fetch Baltimore County GIS address data
    def fetch_baltimore_county_addresses(zip_codes, max_records=3000):
        """
        Fetch addresses from Baltimore County GIS for specified ZIP codes
        """
        # In a real implementation, this would query the Baltimore County GIS API
        # For this example, we'll create sample data
        
        # Check if we already have the data saved
        if os.path.exists('baltimore_county_addresses.csv'):
            print("Loading existing Baltimore County address data")
            return pd.read_csv('baltimore_county_addresses.csv')
        
        # Create sample address data
        addresses = []
        zip_codes = [str(zip_code) for zip_code in zip_codes]
        
        # Sample streets for each ZIP code
        streets_by_zip = {
            '21227': ['WASHINGTON', 'SULPHUR SPRING', 'BENSON', 'LEEDS', 'CARVILLE', 'HIGHVIEW', 'LINDEN', 'MICHIGAN'],
            '21228': ['FREDERICK', 'EDMONDSON', 'ROLLING', 'WINTERS', 'BALTIMORE NATIONAL', 'MELVIN', 'MAIDEN CHOICE', 
                     'BEAUMONT', 'BLOOMSBURY', 'HILTON', 'NEWBURG', 'PLEASANT VALLEY', 'CEDAR CIRCLE', 'FOREST'],
            '21229': ['EDMONDSON', 'FREDERICK', 'WILDWOOD', 'ROKEBY', 'STAMFORD', 'WOODINGTON', 'ATHOL']
        }
        
        # Property use types
        use_types = ['RESIDENTIAL LOW DENSITY', 'RESIDENTIAL HIGH DENSITY', 'COMMERCIAL', 'INSTITUTIONAL']
        
        # Generate addresses
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
        
        # Create DataFrame
        addresses_df = pd.DataFrame(addresses)
        
        # Save to CSV for future use
        addresses_df.to_csv('baltimore_county_addresses.csv', index=False)
        
        return addresses_df
    
    # Fetch or create address data for the ZIP codes in our EDDM data
    zip_codes = routes_df['zip'].unique()
    addresses_df = fetch_baltimore_county_addresses(zip_codes)
    print(f"Loaded {len(addresses_df)} addresses from Baltimore County GIS")
    
    # Step 2: Analyze income distribution
    print("\nStep 2: Analyzing income distribution...")
    
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
    
    # Step 3: Calculate average income by ZIP code
    print("\nStep 3: Calculating average income by ZIP code...")
    
    # Calculate average income by ZIP code
    zip_income = routes_df.groupby('zip')['income_avg'].mean().reset_index()
    zip_income = zip_income.sort_values('income_avg', ascending=False)
    print("Average income by ZIP code:")
    print(zip_income)
    
    # Step 4: Identify streets in high-income ZIP codes
    print("\nStep 4: Identifying streets in high-income ZIP codes...")
    
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
    
    # Step 5: Get addresses for streets in high-income areas
    print("\nStep 5: Getting addresses for streets in high-income areas...")
    
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
        final_table = final_table[[
            'full_address', 'city', 'zip', 'estimated_income', 'use', 'latitude', 'longitude'
        ]]
        
        final_table.columns = [
            'Address', 'City', 'ZIP', 'Est. Income', 'Property Use', 'Latitude', 'Longitude'
        ]
        
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
        
        # Count addresses by property use
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

# Run the complete workflow
high_income_addresses = high_income_address_finder()

# Create a prompt for training an Abacus AI agent
abacus_ai_prompt = """
# High-Income Address Finder Agent

## Agent Description
This agent helps users identify residential and commercial addresses in high-income areas based on demographic data. It analyzes carrier route income data from EDDM (Every Door Direct Mail) and cross-references it with property address databases to create targeted address lists for marketing, real estate prospecting, or market research.

## Capabilities
- Analyze income distribution across ZIP codes and carrier routes
- Identify high-income neighborhoods based on median household income
- Cross-reference demographic data with property databases
- Generate comprehensive address lists for high-income areas
- Provide visualizations of income distribution and property types
- Export results in CSV and Excel formats for easy use

## Example Inputs
- "Find high-income addresses in ZIP codes 21228, 21227, and 21229"
- "Which streets in Baltimore County have the highest average income?"
- "Generate a list of single-family homes in areas with median income above $100,000"
- "What's the income distribution across carrier routes in ZIP code 21228?"
- "Create a table of commercial properties in high-income neighborhoods"

## Example Outputs
- A CSV file containing addresses in high-income areas with property details
- A summary of streets ranked by income level and address count
- Visualizations showing income distribution and property type breakdown
- Analysis of which ZIP codes and carrier routes have the highest income levels
- Filtered lists of addresses based on property type (residential, commercial, etc.)

## Technical Requirements
- Python with pandas, numpy, matplotlib, and requests libraries
- Access to EDDM carrier route income data
- Access to property address databases (e.g., county GIS services)
- Data processing capabilities for large address datasets
- Visualization tools for creating charts and maps

## Use Cases
- Real estate agents looking for high-value property listings
- Marketing campaigns targeting affluent neighborhoods
- Market research for luxury goods and services
- Financial services prospecting for high-net-worth clients
- Nonprofit fundraising targeting high-income donors
"""

# Save the prompt to a file
with open('abacus_ai_agent_prompt.txt', 'w') as f:
    f.write(abacus_ai_prompt)

print("\nAbacus AI agent prompt created and saved to 'abacus_ai_agent_prompt.txt'")

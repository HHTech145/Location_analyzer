from bs4 import BeautifulSoup
import pandas as pd 
html = """
<div class=" cl_b eq_c"><div class="cl_a">A few important facts</div><div class="cl_e"><div class="cw_a"><span class="hw_a cw_b"><nav class="h4_a c6_a"><ol><li><a href="/report/country/uk/transport">UK</a></li><li><span role="link" tabindex="0">England</span></li><li><span role="link" tabindex="0">London</span></li><li><span role="link" tabindex="0">Tower Hamlets</span></li><li><span role="link" tabindex="0">Lansbury</span></li><li><span>E14 0ND</span></li></ol></nav></span><h1 class="hx_a">Transport Links near <span class="d1_a">New Village Avenue, London, E14 0ND</span></h1></div></div><div class="cl_e"><div class="es_a"><div class="ig_a dz_a dz_d es_b"><p class="hu_a dz_e">Connectivity to public transport</p><div class="hs_a es_c"><strong>Average</strong> 5/9</div></div><div class="ig_a dz_a  es_g"><p class="hu_a dz_e">Travel zone</p><div class="hs_a">3</div></div></div></div><div class="cl_e"><p class="hv_a">Connectivity to the public transport is 5 out of 9 in <strong>New Village Avenue, London, E14 0ND</strong></p><button type="button" class=" i4_a  i4_d i4_p  i4_m eq_q">What does it mean?</button></div><div class="cl_c"><h2 class="eq_a">Transport stations <span class="eq_b">10+</span></h2><div><div class="er_a"><ul class="er_b"><li class="er_c"><div class="er_d"><p class="er_e">East India<span class="er_f"> 0.3 miles </span></p></div><div class="er_h"><span class="er_i"><svg width="20" height="20" viewBox="0 0 32 24"><path d="M16 0A12 12 0 004.68 8h4.4a8 8 0 0113.8 0h4.4A12 12 0 0016 0zM27.8 10h-4.08a7.86 7.86 0 01.26 2 8.23 8.23 0 01-.25 2h4.08a11.9 11.9 0 000-4zM16 19.98a8 8 0 01-6.91-4h-4.4a12 12 0 0022.62 0h-4.4a8 8 0 01-6.9 4zm-8-8a7.86 7.86 0 01.26-2H4.17a11.9 11.9 0 000 4h4.08a8.23 8.23 0 01-.25-2z" fill="#00A4A7"></path><path d="M29.98 10H2a2 2 0 00-2 2 2 2 0 002 2h27.98a2 2 0 002-2 2 2 0 00-2-2z" fill="#213e90"></path></svg></span><span class="er_j" style="background: rgb(0, 153, 153); color: white;">dlr</span></div></li><li class="er_c"><div class="er_d"><p class="er_e">Canning Town<span class="er_f"> 0.4 miles </span></p></div><div class="er_h"><span class="er_i"><svg width="20" height="20" viewBox="0 0 32 24"><path d="M16 0A12 12 0 004.68 8h4.4a8 8 0 0113.8 0h4.4A12 12 0 0016 0zM27.8 10h-4.08a7.86 7.86 0 01.26 2 8.23 8.23 0 01-.25 2h4.08a11.9 11.9 0 000-4zM16 19.98a8 8 0 01-6.91-4h-4.4a12 12 0 0022.62 0h-4.4a8 8 0 01-6.9 4zm-8-8a7.86 7.86 0 01.26-2H4.17a11.9 11.9 0 000 4h4.08a8.23 8.23 0 01-.25-2z" fill="#00A4A7"></path><path d="M29.98 10H2a2 2 0 00-2 2 2 2 0 002 2h27.98a2 2 0 002-2 2 2 0 00-2-2z" fill="#213e90"></path></svg></span><span class="er_j" style="background: rgb(0, 153, 153); color: white;">dlr</span></div><div class="er_h"><span class="er_i"><svg width="20" height="20" viewBox="0 0 32 24"><path d="M16 0A12 12 0 004.68 8h4.4a8 8 0 0113.8 0h4.4A12 12 0 0016 0zM27.8 10h-4.08a7.86 7.86 0 01.26 2 8.23 8.23 0 01-.25 2h4.08a11.9 11.9 0 000-4zM16 19.98a8 8 0 01-6.91-4h-4.4a12 12 0 0022.62 0h-4.4a8 8 0 01-6.9 4zm-8-8a7.86 7.86 0 01.26-2H4.17a11.9 11.9 0 000 4h4.08a8.23 8.23 0 01-.25-2z" fill="#dc241f"></path><path d="M29.98 10H2a2 2 0 00-2 2 2 2 0 002 2h27.98a2 2 0 002-2 2 2 0 00-2-2z" fill="#213e90"></path></svg></span><span class="er_j" style="background: rgb(134, 143, 152); color: white;">jubilee</span></div></li><li class="er_c"><div class="er_d"><p class="er_e">Blackwall<span class="er_f"> 0.5 miles </span></p></div><div class="er_h"><span class="er_i"><svg width="20" height="20" viewBox="0 0 32 24"><path d="M16 0A12 12 0 004.68 8h4.4a8 8 0 0113.8 0h4.4A12 12 0 0016 0zM27.8 10h-4.08a7.86 7.86 0 01.26 2 8.23 8.23 0 01-.25 2h4.08a11.9 11.9 0 000-4zM16 19.98a8 8 0 01-6.91-4h-4.4a12 12 0 0022.62 0h-4.4a8 8 0 01-6.9 4zm-8-8a7.86 7.86 0 01.26-2H4.17a11.9 11.9 0 000 4h4.08a8.23 8.23 0 01-.25-2z" fill="#00A4A7"></path><path d="M29.98 10H2a2 2 0 00-2 2 2 2 0 002 2h27.98a2 2 0 002-2 2 2 0 00-2-2z" fill="#213e90"></path></svg></span><span class="er_j" style="background: rgb(0, 153, 153); color: white;">dlr</span></div></li><li class="er_c"><div class="er_d"><p class="er_e">Star Lane<span class="er_f"> 0.6 miles </span></p></div><div class="er_h"><span class="er_i"><svg width="20" height="20" viewBox="0 0 32 24"><path d="M16 0A12 12 0 004.68 8h4.4a8 8 0 0113.8 0h4.4A12 12 0 0016 0zM27.8 10h-4.08a7.86 7.86 0 01.26 2 8.23 8.23 0 01-.25 2h4.08a11.9 11.9 0 000-4zM16 19.98a8 8 0 01-6.91-4h-4.4a12 12 0 0022.62 0h-4.4a8 8 0 01-6.9 4zm-8-8a7.86 7.86 0 01.26-2H4.17a11.9 11.9 0 000 4h4.08a8.23 8.23 0 01-.25-2z" fill="#00A4A7"></path><path d="M29.98 10H2a2 2 0 00-2 2 2 2 0 002 2h27.98a2 2 0 002-2 2 2 0 00-2-2z" fill="#213e90"></path></svg></span><span class="er_j" style="background: rgb(0, 153, 153); color: white;">dlr</span></div></li><li class="er_c"><div class="er_d"><p class="er_e">All Saints<span class="er_f"> 0.6 miles </span></p></div><div class="er_h"><span class="er_i"><svg width="20" height="20" viewBox="0 0 32 24"><path d="M16 0A12 12 0 004.68 8h4.4a8 8 0 0113.8 0h4.4A12 12 0 0016 0zM27.8 10h-4.08a7.86 7.86 0 01.26 2 8.23 8.23 0 01-.25 2h4.08a11.9 11.9 0 000-4zM16 19.98a8 8 0 01-6.91-4h-4.4a12 12 0 0022.62 0h-4.4a8 8 0 01-6.9 4zm-8-8a7.86 7.86 0 01.26-2H4.17a11.9 11.9 0 000 4h4.08a8.23 8.23 0 01-.25-2z" fill="#00A4A7"></path><path d="M29.98 10H2a2 2 0 00-2 2 2 2 0 002 2h27.98a2 2 0 002-2 2 2 0 00-2-2z" fill="#213e90"></path></svg></span><span class="er_j" style="background: rgb(0, 153, 153); color: white;">dlr</span></div></li><li class="er_c"><div class="er_d"><p class="er_e">Langdon Park<span class="er_f"> 0.6 miles </span></p></div><div class="er_h"><span class="er_i"><svg width="20" height="20" viewBox="0 0 32 24"><path d="M16 0A12 12 0 004.68 8h4.4a8 8 0 0113.8 0h4.4A12 12 0 0016 0zM27.8 10h-4.08a7.86 7.86 0 01.26 2 8.23 8.23 0 01-.25 2h4.08a11.9 11.9 0 000-4zM16 19.98a8 8 0 01-6.91-4h-4.4a12 12 0 0022.62 0h-4.4a8 8 0 01-6.9 4zm-8-8a7.86 7.86 0 01.26-2H4.17a11.9 11.9 0 000 4h4.08a8.23 8.23 0 01-.25-2z" fill="#00A4A7"></path><path d="M29.98 10H2a2 2 0 00-2 2 2 2 0 002 2h27.98a2 2 0 002-2 2 2 0 00-2-2z" fill="#213e90"></path></svg></span><span class="er_j" style="background: rgb(0, 153, 153); color: white;">dlr</span></div></li><li class="er_c"><div class="er_d"><p class="er_e">Poplar<span class="er_f"> 0.8 miles </span></p></div><div class="er_h"><span class="er_i"><svg width="20" height="20" viewBox="0 0 32 24"><path d="M16 0A12 12 0 004.68 8h4.4a8 8 0 0113.8 0h4.4A12 12 0 0016 0zM27.8 10h-4.08a7.86 7.86 0 01.26 2 8.23 8.23 0 01-.25 2h4.08a11.9 11.9 0 000-4zM16 19.98a8 8 0 01-6.91-4h-4.4a12 12 0 0022.62 0h-4.4a8 8 0 01-6.9 4zm-8-8a7.86 7.86 0 01.26-2H4.17a11.9 11.9 0 000 4h4.08a8.23 8.23 0 01-.25-2z" fill="#00A4A7"></path><path d="M29.98 10H2a2 2 0 00-2 2 2 2 0 002 2h27.98a2 2 0 002-2 2 2 0 00-2-2z" fill="#213e90"></path></svg></span><span class="er_j" style="background: rgb(0, 153, 153); color: white;">dlr</span></div></li><li class="er_c"><div class="er_d"><p class="er_e">Royal Victoria<span class="er_f"> 0.8 miles </span></p></div><div class="er_h"><span class="er_i"><svg width="20" height="20" viewBox="0 0 32 24"><path d="M16 0A12 12 0 004.68 8h4.4a8 8 0 0113.8 0h4.4A12 12 0 0016 0zM27.8 10h-4.08a7.86 7.86 0 01.26 2 8.23 8.23 0 01-.25 2h4.08a11.9 11.9 0 000-4zM16 19.98a8 8 0 01-6.91-4h-4.4a12 12 0 0022.62 0h-4.4a8 8 0 01-6.9 4zm-8-8a7.86 7.86 0 01.26-2H4.17a11.9 11.9 0 000 4h4.08a8.23 8.23 0 01-.25-2z" fill="#00A4A7"></path><path d="M29.98 10H2a2 2 0 00-2 2 2 2 0 002 2h27.98a2 2 0 002-2 2 2 0 00-2-2z" fill="#213e90"></path></svg></span><span class="er_j" style="background: rgb(0, 153, 153); color: white;">dlr</span></div></li><li class="er_c"><div class="er_d"><p class="er_e">North Greenwich<span class="er_f"> 0.9 miles </span></p></div><div class="er_h"><span class="er_i"><svg width="20" height="20" viewBox="0 0 32 24"><path d="M16 0A12 12 0 004.68 8h4.4a8 8 0 0113.8 0h4.4A12 12 0 0016 0zM27.8 10h-4.08a7.86 7.86 0 01.26 2 8.23 8.23 0 01-.25 2h4.08a11.9 11.9 0 000-4zM16 19.98a8 8 0 01-6.91-4h-4.4a12 12 0 0022.62 0h-4.4a8 8 0 01-6.9 4zm-8-8a7.86 7.86 0 01.26-2H4.17a11.9 11.9 0 000 4h4.08a8.23 8.23 0 01-.25-2z" fill="#dc241f"></path><path d="M29.98 10H2a2 2 0 00-2 2 2 2 0 002 2h27.98a2 2 0 002-2 2 2 0 00-2-2z" fill="#213e90"></path></svg></span><span class="er_j" style="background: rgb(134, 143, 152); color: white;">jubilee</span></div></li><li class="er_c"><div class="er_d"><p class="er_e">Bromley-by-Bow<span class="er_f"> 0.9 miles </span></p></div><div class="er_h"><span class="er_i"><svg width="20" height="20" viewBox="0 0 32 24"><path d="M16 0A12 12 0 004.68 8h4.4a8 8 0 0113.8 0h4.4A12 12 0 0016 0zM27.8 10h-4.08a7.86 7.86 0 01.26 2 8.23 8.23 0 01-.25 2h4.08a11.9 11.9 0 000-4zM16 19.98a8 8 0 01-6.91-4h-4.4a12 12 0 0022.62 0h-4.4a8 8 0 01-6.9 4zm-8-8a7.86 7.86 0 01.26-2H4.17a11.9 11.9 0 000 4h4.08a8.23 8.23 0 01-.25-2z" fill="#dc241f"></path><path d="M29.98 10H2a2 2 0 00-2 2 2 2 0 002 2h27.98a2 2 0 002-2 2 2 0 00-2-2z" fill="#213e90"></path></svg></span><span class="er_j" style="background: rgb(0, 114, 41); color: white;">district</span><span class="er_j" style="background: rgb(215, 153, 175); color: black;">hammersmith-city</span></div></li></ul></div></div></div><div class="cl_e"><h2 class="da_a">Explore transport links in nearby locations</h2><ul class="da_b"><li class="da_c"><span role="link" tabindex="0">Transport links near Blair Street, London, E14 0GE</span></li><li class="da_c"><span role="link" tabindex="0">Transport links near Deauville Close, London, E14 0GG</span></li><li class="da_c"><span role="link" tabindex="0">Transport links near Fortrose Close, London, E14 0GS</span></li><li class="da_c"><span role="link" tabindex="0">Transport links near Portree Street, London, E14 0HU</span></li><li class="da_c"><span role="link" tabindex="0">Transport links near Oban Street, London, E14 0HZ</span></li><li class="da_c"><span role="link" tabindex="0">
Transport links near Abbott Road, London, E14 0LR</span></li>
<li class="da_c"><span role="link" tabindex="0">Transport links near New Village Avenue, London, E14 0NH</span></li></ul>
</div><div class="cl_h cl_i"><div class="el_a"><p class="el_b">Data source:  
<a href="https://api-portal.tfl.gov.uk/" rel="noreferrer" target="_blank">Transport for London</a></p> <p class="el_c"></p></div></div><div class="df_a cl_j"><h2 class="hs_a df_d">Explore more</h2><ul class="df_b"><li><a href="/report/postcode/E140ND/overview" class=" i4_a  i4_d i4_j i4_v df_c">Overview</a></li><li><span role="link" tabindex="0" class=" i4_a  i4_d i4_j i4_v df_c">Affluence</span></li><li><a href="/report/postcode/E140ND/crime" class=" i4_a  i4_d i4_j i4_v df_c">Crime</a></li><li><span role="link" tabindex="0" class=" i4_a  i4_d i4_j i4_v df_c">Demographics</span></li><li><span role="link" tabindex="0" class=" i4_a  i4_d i4_j i4_v df_c">Noise</span></li><li><span role="link" tabindex="0" class=" i4_a  i4_d i4_j i4_v df_c">Amenities</span></li><li><span role="link" tabindex="0" class=" i4_a  i4_d i4_j i4_v df_c">Schools</span></li><li><span role="link" tabindex="0" class=" i4_a  i4_d i4_j i4_v df_c">Environment</span></li><li><span role="link" tabindex="0" class=" i4_a  i4_d i4_j i4_v df_c">Reviews</span></li></ul></div></div>
"""

# Initialize BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# # Initialize dictionary to hold the extracted information
# connectivity_data = {}
# stations_data = []
# # Check if the 'Connectivity to public transport' section exists
# connectivity_div = soup.find('div', class_='es_a')

# if connectivity_div:
#     # Extracting connectivity rating
#     connectivity_info = connectivity_div.find('div', class_='ig_a dz_a dz_d es_b')
#     if connectivity_info:
#         transport_text = connectivity_info.find('p', class_='hu_a dz_e').text.strip()
#         transport_score = connectivity_info.find('div', class_='hs_a es_c').text.strip()
#         print(f"{transport_text}: {transport_score}")
    
#     # Extracting travel zone
#     travel_zone_info = connectivity_div.find('div', class_='ig_a dz_a es_g')
#     if travel_zone_info:
#         travel_text = travel_zone_info.find('p', class_='hu_a dz_e').text.strip()
#         travel_zone = travel_zone_info.find('div', class_='hs_a').text.strip()
#         print(f"{travel_text}: {travel_zone}")
    
#         # Adding connectivity information to dictionary
#     connectivity_data = {
#         "connectivity to public transport": transport_score,
#         "travel zone": travel_zone
#     }
# else:
#     print("Connectivity to public transport information is not available.")

# # Find all the station details
# stations = []
# # Find all the station details and group them by station name
# for station in soup.find_all('li', class_='er_c'):
#     station_name = station.find('p', class_='er_e').text.strip()
#     distance = station.find('span', class_='er_f').text.strip()
#     lines = [line.text.strip() for line in station.find_all('span', class_='line_class')]  # Adjust class as necessary

#     # Add to the stations_data dictionary
#     stations_data[station_name] = {"distance": distance, "lines": lines}

# # Create DataFrame for connectivity
# connectivity_df = pd.DataFrame([connectivity_data])

# # Create DataFrame for stations
# stations_df = pd.DataFrame.from_dict(stations_data, orient='index')

# # Display the DataFrames
# print("Connectivity DataFrame:")
# print(connectivity_df)
# print("\nStations DataFrame:")
# print(stations_df)

import re 
# Initialize dictionary to hold the extracted information
connectivity_data = {}
stations_data = []

# Check if the 'Connectivity to public transport' section exists
connectivity_div = soup.find('div', class_='es_a')

if connectivity_div:
    # Extracting connectivity rating
    connectivity_info = connectivity_div.find('div', class_='ig_a dz_a dz_d es_b')
    if connectivity_info:
        transport_text = connectivity_info.find('p', class_='hu_a dz_e').text.strip()
        transport_score = connectivity_info.find('div', class_='hs_a es_c').text.strip()
        print(f"{transport_text}: {transport_score}")
    
    # Extracting travel zone
    travel_zone_info = connectivity_div.find('div', class_='ig_a dz_a es_g')
    if travel_zone_info:
        travel_text = travel_zone_info.find('p', class_='hu_a dz_e').text.strip()
        travel_zone = travel_zone_info.find('div', class_='hs_a').text.strip()
        print(f"{travel_text}: {travel_zone}")

        # Adding connectivity information to dictionary
        connectivity_data = {
            "connectivity to public transport": transport_score,
            "travel zone": travel_zone
        }
else:
    print("Connectivity to public transport information is not available.")

# Find all the station details and group them by station name
for station in soup.find_all('li', class_='er_c'):
    station_name = station.find('p', class_='er_e').text.strip()
    # Use regex to capture everything before the numeric value
    match = re.match(r'^(.*?)(?=\s*\d+(\.\d+)?\s*miles?)', station_name)

    # Get the matched group if it exists
    station_name = match.group(1).strip() if match else ""
    distance = station.find('span', class_='er_f').text.strip()
    # lines = [line.text.strip() for line in station.find_all('span', class_='line_class')]  # Adjust class as necessary
    # Extract lines
    lines = [span.text.strip() for span in station.find_all('span', class_='er_j')]
    s = ""
    if len(lines) > 1:
        for i, line in enumerate(lines):
            s += line
            if i < len(lines) - 1:
                s += ","
    else:
        s = lines[0]
    print(s)
    # Add to the stations_data dictionary
    # Append each station's data to the list as a dictionary
    stations_data.append({
        "station_name": station_name,
        "distance": distance,
        "lines": s
    })

# Create DataFrame for connectivity
connectivity_df = pd.DataFrame([connectivity_data])

# Create DataFrame for stations
stations_df = pd.DataFrame(stations_data, columns=['station_name', 'distance', 'lines'])

print()

# Display the DataFrames
print("Connectivity DataFrame:")
print(connectivity_df)
print("\nStations DataFrame:")
print(stations_df)

print("____________________________________________")
import re

text = "East India 3 miles"

# Use regex to capture everything before the numeric value
match = re.match(r'^(.*?)(?=\s*\d+(\.\d+)?\s*miles?)', text)

# Get the matched group if it exists
cleaned_text = match.group(1).strip() if match else ""

print(cleaned_text)
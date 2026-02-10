import geopandas as gpd
import pandas as pd
import shapely
import numpy as np
import contextlib
import glob
import os
import apsimxpy
from apsimxpy.field.soil.ssurgo import sdapoly, sdaprop
from apsimxpy.field.soil.ssurgo import soil_extraction as se
from apsimxpy.field.soil.ssurgo import saxton as sax
from apsimxpy.field.soil.ssurgo import soil_apsim as sa

# Importing fields and getting atitude and longitude 
folder = "/workspace/workflow/_3AgroDataExtraction"
geojson_file = glob.glob(os.path.join(folder, "*.geojson"))
fields=gpd.read_file(geojson_file[0])

fields = fields.to_crs(epsg=32616)

accurate_centroids = fields.centroid
centroids_geographic = accurate_centroids.to_crs(epsg=4326)

fields['long'] = round(centroids_geographic.x, 7)
fields['lat'] = round(centroids_geographic.y, 7)

# The apsimxpy module allows you to extract weather and soil properties
init_obg=apsimxpy.Initialize(apsim_folder_input='/workflow',apsim_file_input='CornSoybean_C')

# Set dates to extract weather variables
clock1=apsimxpy.Clock(init_obj=init_obg)
clock1.set_StartDate((1,1,1980)) 
clock1.set_EndDate((31,12,2024))

met=apsimxpy.Weather(init_obg)
soils=pd.DataFrame()
for idx, row in fields.iterrows():
    # Extraction of soil variables
    ssurgo_soil=se.get_poly_soil(row,plot=True)
    main_soil=se.get_main_soil(ssurgo_soil,plot=True)
    
    row_soil = ssurgo_soil[ssurgo_soil['mukey'] == main_soil]
    muname = row_soil['muname'].iloc[0].lower()
    
    if muname.startswith(("borrow", "urban", "water")):
        print("⚠ No valid Area:", row_soil['muname'])
        continue

    props=se.get_soil_props(ssurgo_soil,main_soil)
    s_apsim=sa.soil_apsim(props)
    s_apsim['id_cell']=row['id_cell']
    s_apsim['id_within_cell']=row['id_within_cell']
    print(s_apsim)
    soils = pd.concat([soils, s_apsim], ignore_index=True)
    # Extraction of weather variables
    lat = row['lat']
    long = row['long']
    filename = f"w_id_{row['id_cell']}_{row['id_within_cell']}"
    met.get_weather((round(long,7), round(lat,7)), clock1, filename)
    print(f'Weather and Soil Variables extracted for field {row['id_cell']}-{row['id_within_cell']}')

# Custom soil profiles
new_layers = [
    (0,50),(50,100),
    (100,150),(150,200),(200,400),
    (400,600),(600,800),(800,1000),
    (1000,1500),(1500,2000)
]

weighted_vars = [
    'SAND','CLAY','SILT','BD','KSAT','SAT','DUL','LL','AirDry',
    'PO','SWCON','CONA','DiffusConst','XF_maize','KL_maize',
    'e','PH','CO','CEC','SW'
]

copy_vars = ['RootCN','RootWt','id_cell','id_within_cell']

def weighted_layer(df, ztop, zbot):
    out = {}
    for var in weighted_vars:
        num, den = 0.0, 0.0
        for _, r in df.iterrows():
            overlap = max(0, min(zbot, r.BOT_LAYER) - max(ztop, r.TOP_LAYER))
            if overlap > 0:
                num += overlap * r[var]
                den += overlap
        out[var] = num / den if den > 0 else None
    return out

rows = []

for id_cell, df_cell in soils.groupby('id_cell'):

    df_cell = df_cell.sort_values('TOP_LAYER')

    for ztop, zbot in new_layers:
        row = weighted_layer(df_cell, ztop, zbot)

        row['TOP_LAYER'] = ztop
        row['BOT_LAYER'] = zbot
        row['THICK'] = zbot - ztop

        for v in copy_vars:
            row[v] = df_cell[v].iloc[0]

        rows.append(row)

new_profile = pd.DataFrame(rows)

new_profile.to_csv("/workspace/soil/soils.csv",index=False)

print('Variables extracted successful!!! step 3/4')

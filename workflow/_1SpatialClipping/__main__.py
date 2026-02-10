import geopandas as gpd

# gdb with allf the fields in the US
gdb_path="/workspace/workflow/_1SpatialClipping/FIELDS1724.gdb"
cols = ['geometry','CDL2017','CDL2018','CDL2019','CDL2020','CDL2021','CDL2022','CDL2023','CDL2024']  
# Selection of our area of interest (aoi) (Indiana State)
usa = gpd.read_file("/workspace/workflow/_1SpatialClipping/US_States/US_States.shp")
aoi=usa[usa['NAME']=='Indiana']
aoi_fields = gpd.read_file(gdb_path, layer='national1724', columns=cols,mask=aoi)
# Exporting fields within the aoi
aoi_fields.to_file("/workspace/workflow/_2GridSampling/aoi_fields.geojson",driver="GeoJSON")
print("Spatial clipping completed! step 1/4")
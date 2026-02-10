import geopandas as gpd
import apsimxpy
import numpy as np
import shutil
import pandas as pd
import glob
import os

folder = "/workspace/workflow/_3AgroDataExtraction"
geojson_file = glob.glob(os.path.join(folder, "*.geojson"))
fields=gpd.read_file(geojson_file[0])

nitrogen=[0,50,100,150,200,250,300]


# for id,row in fields[fields['id_cell']>=989].iterrows():
for id,row in fields.iterrows():
    if row['region']=='C':
        apsim_file='CornSoybean_C'
    elif row['region']=='NC':
        apsim_file='CornSoybean_NC'
    elif row['region']=='NE':
        apsim_file='CornSoybean_NE'
    
    src_folder = f"/workspace/workflow/_5RunSimulations/field_{row['id_cell']}_{row['id_within_cell']}"
    src_file = os.path.join(src_folder, f"{apsim_file}_{row['id_cell']}_{row['id_within_cell']}.apsimx")

    # Check if folder exists
    if os.path.exists(src_file):
        shutil.copy(src_file, f"/workspace/{apsim_file}.apsimx")
    else:
        print(f"No file (Urban Soil): {src_file}. Next...")
        continue
    
    init_obg=apsimxpy.Initialize(apsim_folder_input='/Users/jorgeandresjolahernandez/Desktop/ApsimxpyModule',apsim_file_input=apsim_file)
    
    fert=apsimxpy.field.management.Fertilize(init_obg)
    sim1=apsimxpy.simulator(init_obj=init_obg)
    
    for n_rate in nitrogen:
        fert.set_fert_sowing(n_rate)
        sim1.run()
        results=pd.read_csv(f'/workspace/{init_obg.apsim_file_input}.Report.csv')
        results['Nitrogen']=n_rate
        results['county']=row['countyname']
        results['id_cell']=row['id_cell']
        results['id_within_cell']=row['id_within_cell']
        results.to_csv(f'/workspace/{init_obg.apsim_file_input}.Report.csv')
        shutil.copy(f"/workspace/{apsim_file}.Report.csv",f"/workspace/workflow/_5RunSimulations/field_{row['id_cell']}_{row['id_within_cell']}/report_{row['id_cell']}_{row['id_within_cell']}_N{n_rate}.csv")
    print("Simulations Finished for :",row['id_cell'],row['id_within_cell'])

print("Simulations Finished , merging results... ")



lis_results=[]

for id,row in fields.iterrows():
    for n_rate in nitrogen:
        
        res_file=f"/workspace/workflow/_5RunSimulations/field_{row['id_cell']}_{row['id_within_cell']}/report_{row['id_cell']}_{row['id_within_cell']}_N{n_rate}.csv"
        
        if os.path.exists(res_file):
            results=pd.read_csv(res_file)
        else:
            print(f"No results for : {row['id_cell']}")
            continue
        
        results['Yield'] = (results['MaizeYield']+results['SoyBeanYield'])/1000
        results = results[results["Yield"] != 0]
        results = results[['Clock.Today','Yield','Nitrogen','id_cell','id_within_cell','MaizeYield','SoyBeanYield','ISoilWater.LeachNO3']]
        lis_results.append(results)
all_results = pd.concat(lis_results, ignore_index=True)
all_results.to_parquet("/workspace/workflow/_6EvaluationNotebooks/results.parquet", index=False)   

print("Results merged in a parquet!")
            
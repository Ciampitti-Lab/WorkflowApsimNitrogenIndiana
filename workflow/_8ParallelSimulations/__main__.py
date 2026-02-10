import geopandas as gpd
import apsimxpy
import numpy as np
import shutil
import pandas as pd
import glob
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

folder = "/workspace/workflow/_3AgroDataExtraction"
geojson_file = glob.glob(os.path.join(folder, "*.geojson"))
fields=gpd.read_file(geojson_file[0])


nitrogen = np.random.uniform(0, 267.66, size=6)/ 0.892

# Preproccesing
soils=pd.read_csv("/workspace/soil/soils.csv")
cols = ['SAND', 'CLAY', 'SILT', 'BD']
soils = soils[~(soils[cols].fillna(0) == 0).all(axis=1)]

lis_df=[]
count=0

# os.makedirs(f"/workspace/workflow/_8ParallelSimulations/apsim_files")

region=input('Select specific region (ee: "all" , "NC", "C", "NE")')

if region=="all":
    sample_fields=fields
elif region=='NC':
    sample_fields=fields[fields['region']=='NC']
elif region=='C':
    sample_fields=fields[fields['region']=='C']
elif region=='NE':
    sample_fields=fields[fields['region']=='NE']
    
# for id,row in sample_fields[sample_fields['id_cell']>=230].iterrows():
for id,row in sample_fields.iterrows():
    print(row['id_cell'])
    if row['region']=='C':
        apsim_file='CornSoybean_C'
    elif row['region']=='NC':
        apsim_file='CornSoybean_NC'
    elif row['region']=='NE':
        apsim_file='CornSoybean_NE'
    
    if row['id_within_cell']%2==0:
        for year in list(range(2006,2023,2)):
            
            init_obg=apsimxpy.Initialize(apsim_folder_input='/Users/jorgeandresjolahernandez/Desktop/ApsimxpyModule',apsim_file_input= apsim_file)

            clock1=apsimxpy.Clock(init_obj=init_obg)

            clock1.set_StartDate((1,1,year)) 
            clock1.set_EndDate((31,12,year))
            
            met=apsimxpy.Weather(init_obg)
            soil1=apsimxpy.field.Soil(init_obg)
            fert=apsimxpy.field.management.Fertilize(init_obg)
            
            # Setting the weather
            weather_name=f"w_id_{row['id_cell']}_{row['id_within_cell']}"
            met.set_weather(weather_name)
            
            # Setting soil
            soil=soils[(soils['id_cell']==row['id_cell']) & (soils['id_within_cell']==row['id_within_cell'])]
            if soil.empty:
                print(soil)
                continue
            soil1.set_soil_saxton(soil,r=row['region'])
            
            for n_rate in nitrogen:
                fert.set_fert_sowing(n_rate)
                # Creating a file for each field
                shutil.copy(f"/workspace/{apsim_file}.apsimx",f"/workspace/workflow/_8ParallelSimulations/apsim_files/{apsim_file}_{row['id_cell']}_{row['id_within_cell']}_N{n_rate}_Y{year}.apsimx")
                # Counting simulations
                count+=1
    else:
        for year in list(range(2006,2023,2)):
            init_obg=apsimxpy.Initialize(apsim_folder_input='/Users/jorgeandresjolahernandez/Desktop/ApsimxpyModule',apsim_file_input= apsim_file)

            clock1=apsimxpy.Clock(init_obj=init_obg)

            clock1.set_StartDate((1,1,year)) 
            clock1.set_EndDate((31,12,year))
            
            met=apsimxpy.Weather(init_obg)
            soil1=apsimxpy.field.Soil(init_obg)
            fert=apsimxpy.field.management.Fertilize(init_obg)
            
            # Setting the weather
            weather_name=f"w_id_{row['id_cell']}_{row['id_within_cell']}"
            met.set_weather(weather_name)
            
            # Setting soil
            soil=soils[(soils['id_cell']==row['id_cell']) & (soils['id_within_cell']==row['id_within_cell'])]
            if soil.empty:
                continue
            soil1.set_soil_saxton(soil,r=row['region'])
            
            for n_rate in nitrogen:
                fert.set_fert_sowing(n_rate)
                # Creating a file for each field
                shutil.copy(f"/workspace/{apsim_file}.apsimx",f"/workspace/workflow/_8ParallelSimulations/apsim_files/{apsim_file}_{row['id_cell']}_{row['id_within_cell']}_N{n_rate}_Y{year}.apsimx")
                # Counting simulations
                count+=1


# Running Parallel Simulations
def single_simulation(row):  
    if row['id_within_cell']%2==0:
        for year in list(range(2006,2010,2)):  
            for n_rate in nitrogen:
                if row['region']=='C':
                    apsim_file=f'CornSoybean_C_{row['id_cell']}_{row['id_within_cell']}_N{n_rate}_Y{year}'
                elif row['region']=='NC':
                    apsim_file=f'CornSoybean_NC_{row['id_cell']}_{row['id_within_cell']}_N{n_rate}_Y{year}'
                elif row['region']=='NE':
                    apsim_file=f'CornSoybean_NE_{row['id_cell']}_{row['id_within_cell']}_N{n_rate}_Y{year}'
                    
                src_file = os.path.join('/workspace/workflow/_8ParallelSimulations/apsim_files', f"{apsim_file}.apsimx")
                # Check if folder exists
                if os.path.exists(src_file):
                    init_obg=apsimxpy.Initialize(apsim_folder_input='/Users/jorgeandresjolahernandez/Desktop/ApsimxpyModule/workflow/_8ParallelSimulations/apsim_files',apsim_file_input=apsim_file)
                else:
                    print(f"No file (Urban Soil): {src_file}. Next...")
                    continue
                    
                sim1=apsimxpy.simulator(init_obj=init_obg)
                sim1.run()
                    
                results=pd.read_csv(f'/workspace/workflow/_8ParallelSimulations/apsim_files/{init_obg.apsim_file_input}.Report.csv')
                results['nitro_kg_ha']=n_rate
                results['county']=row['countyname']
                results['id_cell']=row['id_cell']
                results['id_within_cell']=row['id_within_cell']
                results.to_csv(f'/workspace/workflow/_8ParallelSimulations/apsim_files/report_{row['id_cell']}_{row['id_within_cell']}_N{n_rate}_Y{year}.csv')
                print("Simulations Finished for task :",row['id_cell'],row['id_within_cell'],'N:', n_rate,'Year',year)
    else:
        for year in list(range(2007,2010,2)):  
            for n_rate in nitrogen:
                if row['region']=='C':
                    apsim_file=f'CornSoybean_C_{row['id_cell']}_{row['id_within_cell']}_N{n_rate}_Y{year}'
                elif row['region']=='NC':
                    apsim_file=f'CornSoybean_NC_{row['id_cell']}_{row['id_within_cell']}_N{n_rate}_Y{year}'
                elif row['region']=='NE':
                    apsim_file=f'CornSoybean_NE_{row['id_cell']}_{row['id_within_cell']}_N{n_rate}_Y{year}'
                    
                src_file = os.path.join('/workspace/workflow/_8ParallelSimulations/apsim_files', f"{apsim_file}.apsimx")
                # Check if folder exists
                if os.path.exists(src_file):
                    init_obg=apsimxpy.Initialize(apsim_folder_input='/Users/jorgeandresjolahernandez/Desktop/ApsimxpyModule/workflow/_8ParallelSimulations/apsim_files',apsim_file_input=apsim_file)
                else:
                    print(f"No file (Urban Soil): {src_file}. Next...")
                    continue
                    
                sim1=apsimxpy.simulator(init_obj=init_obg)
                sim1.run()
                    
                results=pd.read_csv(f'/workspace/workflow/_8ParallelSimulations/apsim_files/{init_obg.apsim_file_input}.Report.csv')
                results['nitro_kg_ha']=n_rate
                results['county']=row['countyname']
                results['id_cell']=row['id_cell']
                results['id_within_cell']=row['id_within_cell']
                results.to_csv(f'/workspace/workflow/_8ParallelSimulations/apsim_files/report_{row['id_cell']}_{row['id_within_cell']}_N{n_rate}_Y{year}.csv')
                print("Simulations Finished for task :",row['id_cell'],row['id_within_cell'],'N:', n_rate,'Year',year)



# tasks = [row.to_dict() for _, row in sample_fields[sample_fields['id_cell']>=230].iterrows()] 

tasks = [row.to_dict() for _, row in sample_fields.iterrows()] 

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(single_simulation, task) for task in tasks]
    for f in as_completed(futures):
        f.result()

lis_results=[]

for id,row in sample_fields.iterrows():
    if row['id_within_cell']%2==0:
        for year in list(range(2006,2010,2)):  
            for n_rate in nitrogen:
                res_file=f"/workspace/workflow/_8ParallelSimulations/apsim_files/report_{row['id_cell']}_{row['id_within_cell']}_N{n_rate}_Y{year}.csv"
                
                if os.path.exists(res_file):
                    results=pd.read_csv(res_file)
                else:
                    print(f"No results for : {row['id_cell']}")
                    continue
                
                results['yield_ton_ha'] = (results['maize_yield_kg_ha']+results['soybean_yield_kg_ha'])/1000
                results = results[results["yield_ton_ha"] != 0]
                results = results[['date','yield_ton_ha','nitro_kg_ha','id_cell','id_within_cell','maize_yield_kg_ha','soybean_yield_kg_ha','leachno3']]
                lis_results.append(results)
    else:
        for year in list(range(2007,2010,2)):  
            for n_rate in nitrogen:
                res_file=f"/workspace/workflow/_8ParallelSimulations/apsim_files/report_{row['id_cell']}_{row['id_within_cell']}_N{n_rate}_Y{year}.csv"
                
                if os.path.exists(res_file):
                    results=pd.read_csv(res_file)
                else:
                    print(f"No results for : {row['id_cell']}")
                    continue
                
                results['yield_ton_ha'] = (results['maize_yield_kg_ha']+results['soybean_yield_kg_ha'])/1000
                results = results[results["yield_ton_ha"] != 0]
                results = results[['date','yield_ton_ha','nitro_kg_ha','id_cell','id_within_cell','maize_yield_kg_ha','soybean_yield_kg_ha','leachno3']]
                lis_results.append(results)
                
all_results = pd.concat(lis_results, ignore_index=True)
all_results.to_parquet("/workspace/workflow/_6EvaluationNotebooks/results.parquet", index=False)   

print("Results merged in a parquet!")
            

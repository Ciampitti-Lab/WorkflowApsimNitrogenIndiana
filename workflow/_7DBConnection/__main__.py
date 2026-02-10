import geopandas as gpd
import pandas as pd
import psycopg2

# Reading the results file after running simulations
results = pd.read_parquet("/workspace/workflow/_6EvaluationNotebooks/results.parquet", engine="fastparquet")

# Extracting the year
results["Clock.Today"] = pd.to_datetime(results["Clock.Today"])
results['Year'] = results['Clock.Today'].dt.year

# yield from kg to tons
idx = results.groupby(['id_cell', 'Nitrogen'])['Yield'].idxmax()
results = results.loc[idx].reset_index(drop=True)
results['Yield'] = (results['MaizeYield']+results['SoyBeanYield'])/1000

# Create ID 
id_list=list() 
for idx,row in results.iterrows():
    id_list.append(str(row['id_cell'])+'_'+str(row['Nitrogen']))
    
results['id']=id_list

# Select important variables
results = results[['id','id_cell','Nitrogen','Yield']]
results = results.rename(columns={
    'id': 'id_sim',
    'Nitrogen': 'nitrogen',
    'Yield': 'yield'
})

DB_CONFIG={
    'host':'dpg-d4pf6np5pdvs73asbc60-a.oregon-postgres.render.com',
    'dbname':'apsimxpydb',
    'user':'jorgejola',
    'password':'Hb39h7DitoXgITE0ztX6srEiQPQsdo9Q',
    'port': 5432 
}

# Generate the connection to the PostgreSQL database
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

conn = None 

try:
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM simulations;")
    conn.commit()
    
    insert_query = """
    INSERT INTO simulations (id_sim , id_cell, nitrogen, yield)
    VALUES (%s, %s, %s, %s);
    """
    
    data = list(results.itertuples(index=False, name=None))
    cur.executemany(insert_query, data)
    
    conn.commit()
    print(f"Successfully inserted {cur.rowcount} rows into simulations.")

except (Exception, psycopg2.Error) as error:
    print(f"Error while connecting to PostgreSQL or inserting data: {error}")

finally:
    if conn:
        cur.close()
        conn.close()
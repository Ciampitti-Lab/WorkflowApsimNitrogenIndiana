import analysis
from analysis import results_config
import matplotlib.pyplot as plt
from ipywidgets import interact
import matplotlib.dates as mdates
import pandas as pd
from plotnine import *

res=results_config("/workspace/workflow/_6EvaluationNotebooks/results.parquet")

res.read_results()

res.create_folders()
##############################
# Simulations Visualizations #
##############################

### Visualization Creation

#### Maize Yield Production
pivot_df_maize=res.maize_yield_prod()

plt.figure(figsize=(12, 6))
for col in pivot_df_maize.columns:
    plt.plot(pivot_df_maize.index, pivot_df_maize[col], label=f"Nitrogen {col}")

years = pd.DatetimeIndex(pivot_df_maize.index).year.unique()
plt.xticks(pd.to_datetime([f'{year}-01-01' for year in years]), years, rotation=45)

plt.xlabel("year")
plt.ylabel('maize_yield_kg_ha')
plt.title("Maize yield over time")
plt.legend(title="Simulation", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig("/workspace/workflow/_6EvaluationNotebooks/SimViz/MaizeYield.jpeg")

#### SoyBean Production
pivot_df_soybean = res.soybean_yield_prod()

plt.figure(figsize=(12, 6))
for col in pivot_df_soybean.columns:
    plt.plot(pivot_df_soybean.index, pivot_df_soybean[col], label=f"Nitrogen {col}")

years = pd.DatetimeIndex(pivot_df_soybean.index).year.unique()
plt.xticks(pd.to_datetime([f'{year}-01-01' for year in years]), years, rotation=45)

plt.xlabel("year")
plt.ylabel('soybean_yield_kg_ha')
plt.title("Soy Bean yield over time")
plt.legend(title="Simulation", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig("/workspace/workflow/_6EvaluationNotebooks/SimViz/SoyBeanYield.jpeg")

#### All Production

pivot_df_yield=res.all_yield_prod()

plt.figure(figsize=(12, 6))
for col in pivot_df_yield.columns:
    plt.plot(pivot_df_yield.index, pivot_df_yield[col], label=f"Nitrogen {col}")

years = pd.DatetimeIndex(pivot_df_yield.index).year.unique()
plt.xticks(pd.to_datetime([f'{year}-01-01' for year in years]), years, rotation=45)

plt.xlabel("year")
plt.ylabel('yield_ton_ha')
plt.title("Yield over time")
plt.legend(title="Simulation", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig("/workspace/workflow/_6EvaluationNotebooks/SimViz/Yield.jpeg")

############################
# Ground Truth Data Folder #
############################

gtd=res.read_gtd()

#### Yield per region
YieldperRegion=(
    ggplot(gtd, aes(x='nitro_kg_ha', y='yield_ton_ha', color='region')) +
    geom_point(size=1) +
    geom_smooth(method='lm',se=False) +
    theme_bw() +
    labs(
        x='Total Nitrogen (kg/ha)',
        y='Yield (t/ha)',
        color='County'
    )
)
YieldperRegion.save("/workspace/workflow/_6EvaluationNotebooks/GTViz/YieldperRegion.jpeg")

#### Boxplot Yield per region
YieldBoxRegion = (
    ggplot(gtd, aes(x='region', y='yield_ton_ha', fill="region")) +
    geom_violin(alpha=0.6) +
    geom_boxplot(width=0.35) +
    theme_bw() +
    labs(
        x='Region',
        y='Yield (t/ha)',
        fill='Source'
    )+
    theme(
        axis_text_x=element_text(size=8, angle=45, hjust=1),  
        figure_size=(12, 6)  
    )
)
YieldBoxRegion.save("/workspace/workflow/_6EvaluationNotebooks/GTViz/YieldBoxRegion")

#############################
# GTD vs SIM visualizations #
#############################

res.results_prepare()

boxplot_data=res.boxplot_nrate_config()

boxplotComparation = (
    ggplot(boxplot_data, aes(x='region', y='yield_ton_ha', fill='source')) +
    geom_boxplot(position=position_dodge(width=0.8), width=0.3, alpha=0.6) +
    facet_wrap('~rate', ncol=2, scales='free_y') +
    theme_bw() +
    labs(
        title='Ground Truth vs Simulated Yield',
        x='Region',
        y='Yield (t/ha)',
        fill='Data'
    ) +
    theme(
        axis_text_x=element_text(size=8, angle=45, hjust=1),
        figure_size=(12, 7)
    )
)

boxplotComparation.save("/workspace/workflow/_6EvaluationNotebooks/SimGTViz/boxplotComparation.jpeg")

##########################
## Paper visualizations ##
##########################
regionColors = {
    'NC': '#2ca02c',
    'NE': '#ff7f0e',
    'C':  '#1f77b4'
}
### Boxplot

boxplot_data.reset_index(drop=True,inplace=True)
boxplot_paper=(ggplot(boxplot_data ,aes(y='yield_ton_ha',x='region',fill='region'))+
      geom_boxplot()+
      facet_wrap('~source')+
      theme_bw()+
      xlab('Region')+
      ylab('Yield (Ton/Ha)')+
      theme(legend_position='none')+
      scale_fill_manual(values=regionColors)
      )

boxplot_paper.save("/workspace/workflow/_6EvaluationNotebooks/PaperViz/boxplotPaper.jpeg")

### Curves 

curves_df=res.average_aonr(fit=False)

curvesPaper = (
    ggplot()
    + geom_line(curves_df, aes("nitro_kg_ha", "yield_por", color="region"), size=3)
    + theme_bw()
    + labs(
        x="N rate (Kg/Ha)",
        y="Percent of maximum yield",
        color="Region"
    )
    + scale_color_manual(values=regionColors)
    + facet_wrap("source")
    
)
curvesPaper.save("/workspace/workflow/_6EvaluationNotebooks/PaperViz/curvesPaper.jpeg")

### bars
total_counts=res.aonr_calculate()

bars_plot = (
    ggplot(total_counts, aes(x='nitro_kg_ha',y='percentaje',fill='region'))
    #+ geom_col(position='dodge', width=50,color='black')
    + geom_col(position='dodge', width=25,color='black')
    + theme_bw()
    + facet_grid('source~region')
    + labs(x='Agronomical Optimum N Rate (Kg/ha)',y="% of sites",fill='Region')
    + scale_fill_manual(values=regionColors)
)

bars_plot.save("/workspace/workflow/_6EvaluationNotebooks/PaperViz/barsPaper.jpeg")

### Nitrogen Leaching

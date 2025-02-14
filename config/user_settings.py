#!/usr/bin/env python3

'''
|===============================================================|
| File: user_settings.py                                        |
| Project: WasteAndMaterialFootprint-MacroStudy                 |
| Repository: www.github.com/Stew-McD/WasteAndMaterialFootprint-MacroStudy|
| Description: <<description>>                                  |
|---------------------------------------------------------------|
| File Created: Thursday, 28th September 2023 1:27:06 pm        |
| Author: Stewart Charles McDowall                              |
| Email: s.c.mcdowall@cml.leidenuniv.nl                         |
| Github: Stew-McD                                              |
| Company: CML, Leiden University                               |
|---------------------------------------------------------------|
| Last Modified: Friday, 29th September 2023 8:27:09 pm         |
| Modified By: Stewart Charles McDowall                         |
| Email: s.c.mcdowall@cml.leidenuniv.nl                         |
|---------------------------------------------------------------|
|License: The Unlicense                                         |
|===============================================================|
'''
#%%
import os
import numpy as np
from pathlib import Path
from multiprocessing import cpu_count

custom_bw2_dir = os.path.expanduser("~") + '/brightway2data'
if custom_bw2_dir:
    os.environ["BRIGHTWAY2_DIR"] = custom_bw2_dir

import bw2data as bd


title = 'markets'
project_name = "WMFootprint-SSP2LT-cutoff"
limit = None # limit the number of activities to be processed (for testing)
verbose = True
use_multiprocessing = False

num_cpus = int(os.environ.get('SLURM_CPUS_PER_TASK', os.environ.get('SLURM_JOB_CPUS_PER_NODE', cpu_count())))

if project_name not in bd.projects:
    print(f'{"*"*80}\n')
    print(f'Project {project_name} not found, exiting...')
    print(f'{"*"*80}\n')
    exit(0)

else:
    print(f'\n\n{"="*100}\n')
    print(f'\t\t *** Processing activity set "{title}" in project {project_name} *** ')
    print(f'\n{"="*100}\n')
    bd.projects.set_current(project_name)


database_names = None # you could also specify a list of databases here

# extract all databases in the project except those in the exclude list (ie. the biosphere and the WasteAndMaterialFootprint database)
if not database_names:
    exclude = ["biosphere", 'WasteAndMaterialFootprint'] # add to here if you want
    database_names = sorted([x for x in bd.databases if not any(e in x for e in exclude)])


# Define filters for activities of interest
# Can leave as an empty list or include specific names to filter.
# Uncommenting a name (e.g. 'battery production') will include it in the filter.
names_filter = [
    'market for',
    # 'battery production',
]

# Specify CPC (Central Product Classification) numbers to include. (integers)
cpc_num_filter = [
    # 46420, 
    # 46410, 
    # -1 # if there is no CPC number
]

# Specify keywords to exclude from the activities.
exclude_filter = [
    'recovery',
    'treatment', 
    'disposal', 
    'waste', 
    'services', 
    'waste', 
    'scrap'
    'site preparation', 
    'construction',
    'maintainence',
]

locations_filter = [
    'GLO', 
    'RoW', 
    'World',
]

units_filter = [
    'kilogram', 
    'cubic meter',
    'unit',
]

activitytype_filter = [
    'market activity',
]

filters = {
    "names": names_filter,
    "CPC_num": cpc_num_filter,
    "exclude": exclude_filter,
    "locations": locations_filter,
    "units": units_filter,
    "activity type": activitytype_filter,
}


# choose methods

# Filter methods to select those of interest
methods_all =  np.unique([x[0] for x in bd.methods.list])
# methods_waste = [x for x in bd.methods.list if "Waste Footprint" in x[0]]
# methods_material = [x for x in bd.methods.list if "Demand:" in x[1]]

KEYWORDS_METHODS = [
    "ReCiPe 2016 v1.03, midpoint (I)",
    "EF v3.1 EN15804",
    "EDIP 2003 no LT",
    "Crustal Scarcity Indicator 2020",
    "WasteAndMaterialFootprint",
]

methods_other = [x for x in bd.methods.list if any(e in x[0] for e in KEYWORDS_METHODS)]

methods = methods_other # methods_waste + methods_material + 
#methods = methods_other


# %% DIRECTORY PATHS
# Set the paths (to the data, logs, and the results

# Get the directory of the main script
cwd = Path.cwd()
# Get the path one level up
dir_root = cwd.parents[0]

    # Set up the data directories
dir_data = dir_root / 'data' / title
dir_tmp = dir_data / 'tmp' / project_name
dir_logs = dir_data / 'logs' / project_name
dir_results = dir_data / 'results' / project_name
dir_figures = dir_results / 'figures' 
dirs = [dir_data, dir_tmp, dir_logs, dir_results]

for DIR in dirs:
    if not os.path.isdir(DIR): 
        os.makedirs(DIR)
        
activities_list = dir_data / f"activities_list_merged_{project_name}_{title}.csv"

combined_raw_csv, combined_raw_pickle = (dir_tmp / f"{title}_combined_rawresults_df.{x}" for x in ['csv', 'pickle'])

combined_cooked_csv, combined_cooked_pickle = (dir_results / f"{title}_combined_cookedresults_df.{x}" for x in ['csv', 'pickle'])

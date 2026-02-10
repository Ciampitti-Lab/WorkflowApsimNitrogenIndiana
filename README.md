## ⚙️ Workflow

### 🧩 Structure
```text
workflow/
├── _1SpatialClipping
├── _2GridSampling
├── _3AgroDataExtraction
├── _4preproccesig
├── _5RunSimulations
├── _6EvaluationNotebooks
├── _7DBConnection
├── _8ParallelSimulations
├── _9GTDpreparation
└── manager.ipynb

<----- Additional Files/Folders ----->

├── weather/
├── soil/
├── CornSoybean_C.apsimx
├── CornSoybean_NC.apsimx
└── CornSoybean_NE.apsimx
```
### 📘 Directory Descriptions

| Type   | Name | Description |
|-------|------|-------------|
| Folder | `_1SpatialClipping` | Cuts and selects fields within the area of interest (Indiana State). |
| Folder | `_2GridSampling` | Generates sampling grid and select 4 random corn fields within each cell. |
| Folder | `_4preproccesig` | Cleans, formats, and prepares inputs for APSIM simulations. |
| Folder | `_5RunSimulations` | Executes APSIM NG simulations using prepared inputs. |
| Folder | `_6EvaluationNotebooks` | Evaluates simulation outputs comparing with ground truth data and performs exploratory analysis. |
| Folder | `_7DBConnection` | Handles database connections for storing and retrieving results.|
| Folder | `_8ParallelSimulations` | Runs APSIM simulations in parallel. |
| Folder | `_9GTDpreparation` | Prepares ground truth data. |
| File | `manager.ipynb` | Central notebook orchestrating and monitoring the full workflow. |
| Folder | `weather` | Saves .met files. |
| Folder | `soil` | Saves soil information extracted from ssurgo. |
| File | `CornSoybean_C.apsimx` | Input file to run simulations in the center region of Indiana. |
| File | `CornSoybean_NC.apsimx` | Input file to run simulations in the north center region of Indiana. |
| File | `CornSoybean_NE.apsimx` | Input file to run simulations in the north east region of Indiana. |

## 📦 Installation

### Prerequisites
- docker
- apsiminitiative/apsimng (docker image)

### Steps

- Import apsimxpy 
- Clone Repository in the same folder than the apsimxpy module

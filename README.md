# RB-SynSubDB - Rat Brain Subregional Proteomics Database

## Introduction
RB-SynSubDB is a specialized database focusing on the proteomics of synaptosomes in rat brain subregions. This database provides protein expression data for six major brain regions (prefrontal cortex, posterior cortex, hippocampus, striatum, olfactory bulb, and cerebellum), offering an important reference for neuroscience research.

## Features
- Provides visualization of protein expression data for six major brain regions
- Supports interactive querying of protein expression data
- Uses KNN algorithm to handle missing data
- Offers visualization of brain region distribution and expression levels

## Installation Instructions
### System Requirements
- Python 3.8+
- pip package manager
### Installation Steps
1. Clone the repository
```bash
git clone https://github.com/yourusername/RB-SynSubDB.git
cd RB-SynSubDB
```
2. Install dependencies
```bash
pip install -r requirements.txt
```

## Usage
1. Start the application
```bash
python app.py
```

2. Open the browser and access the application
- Open the browser
- Access http://localhost:8050

## Project Structure
- `app.py`: Main application
- `brain_map.py`: Brain region visualization module
- `data.txt`: Raw data file
- `dataKNN.csv`: KNN processed data file
- `assets/`: Static resources folder
  - `brain_regions.svg`: Brain region SVG file
  - `neuron_network_bg.svg`: Neuron network background image
  - `style.css`: Style sheet file
- `requirements.txt`: Dependency package list

## Data Processing
- Use KNN algorithm to handle missing data
- Support data import and export
- Provide data visualization and statistical analysis

## Contribution Guidelines
We welcome all forms of contributions, including but not limited to:
- Report issues
- Submit improvement suggestions
- Submit code modifications

## License
This project is licensed under the MIT License - see [LICENSE](LICENSE) file

## Contact
If you have any questions or suggestions, please contact us through the following methods:
- Submit Issue
- Send Pull Request

## Acknowledge
Thank you to all the researchers and developers who have contributed to this project.
# MI: Motor Imagery Brain–Computer Interface

This repository reorganizes the original MI project, providing a cleaner code structure and a README that links all key resources, making it a good starting point for understanding the Cerebruh_BCI project.  

The original project repo:   
[https://github.com/MBSI-Inc/Cerebruh_BCI/tree/main/Experiments/MI_2](https://github.com/MBSI-Inc/Cerebruh_BCI/tree/main/Experiments/MI_2)   

## Quick links
- **Onboarding Doc (Include workshop 1-3 for newbees)**:   
https://mbsi-org-au.atlassian.net/wiki/spaces/BCI/pages/174948360/Onboarding+Brain+Brain

- **Code for integration (Connect MI outputs to the wheelchair controller)**:   
https://github.com/MBSI-Inc/CereCe_Integration/blob/NewGaze/a.py

- **3D unity simulator(Gaze Based)**:   
https://github.com/MBSI-Inc/Gazebaes_Wheelchair_Simulator



## Pipeline 

### Requirements
- Explore EEG device
- Python 3.9
- See requirements.txt for Python dependencies

You can install enviroment by using following commands:

```bash
# Create a conda environment
conda create -n bci python=3.9

# Activate the environment
conda activate bci

# Install dependencies
python -m pip install -r requirements.txt
```

### 0) EEG Device Setup
Follow the guide below to set up the ExG amplifier:

[EEG Setup Cheat Sheet](https://mbsi-org-au.atlassian.net/wiki/spaces/BCI/pages/3768321/EEG+Set-Up+Cheat+Sheet+filenaming+conventions)

### 1) Record EEG Data
Records EEG data during motor imagery (MI) experiments for training. Connects to the EEG device, launches the pygame experiment, and saves the data to the specified output file.  

**Usage**  

```bash
python launch_record_experiment.py -n "Explore_Device_Name" -f "output_filename"
```   

*Note*: If explore device name and output file names are not provided, the defaults in constants.py will be used.

### 2) Train the Classifier
Trains an LDA classifier on recorded EEG data and saves the model. Expects the same file name as provided in the recording step. Will save the trained model using the same name.  

**Usage**  

```bash
python launch_train_and_save_model.py -f "recorded_data_filename"
```  

*Note*: If file name is not provided, the defaults in constants.py will be used.


### 3) Real-Time MI Inference
Runs real-time MI classification using the trained model and live EEG input. You can run it in **CLI mode** for command-line interaction or in **diagnostic mode** with visual UI feedback. Both modes expect the same device/model filename used in previous steps and run asynchronously until terminated.


**Usage**  

```bash
# CLI mode
python launch_async_mi_core.py -n "Explore_Device_Name" -m "model_filename" -t "KeyPress"

# Diagnostic mode
python launch_async_mi_diagnostic.py -n "Explore_Device_Name" -m "model_filename"
```



## Core components (inside `src/`)

- `analysisMI_classes.py` — data analysis & training
- `async_mi_core.py` — realtime MI classification engine
- `async_mi_diagnostic_class.py` — diagnostic UI wrapper
- `record_MI_class.py` — experiment recording interface
- `helper_functions.py` — signal processing helpers
- `constants.py` — defaults and configuration
- `self_threaded_process_interface.py` — async/threading utilities

Usage summary
- Record with `launch_record_experiment.py` → Train with `launch_train_and_save_model.py` → Run with `launch_async_mi_core.py` or `launch_async_mi_diagnostic.py`.

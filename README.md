# MI: Motor Imagery Brain-Computer Interface

A Python implementation of a motor imagery (MI) brain-computer interface system using EEG signals from Explore devices.

## Overview

This system provides a complete pipeline for motor imagery classification:
1. **Record** EEG data during MI experiments
2. **Train** machine learning models on recorded data  
3. **Run** real-time MI classification with live feedback

## Launch Scripts

### `launch_record_experiment.py`
Records EEG data during motor imagery experiments for model training. Connects to an EEG and starts the pygame that controls the data collection experiment. Will save the data files using the provided output file name.

**Usage:**

If explore device name and output file names are not provided, the defaults in `constants.py` will be used.
```bash
python launch_record_experiment.py -n "Explore_Device_Name" -f "output_filename"
```

### `launch_train_and_save_model.py` 
Trains an LDA classifier on recorded EEG data and saves the model. Expects the same file name as provided in the recording step. Will save the trained model using the same name.

**Usage:**

If file name is not provided, the defaults in `constants.py` will be used.
```bash
python launch_train_and_save_model.py -f "recorded_data_filename"
```

### `launch_async_mi_core.py`
Runs real-time MI classification with command-line interaction. Expects the file name as used in previous steps. Will load the trained model, connect to the EEG, and run async MI until termination.

**Usage:**
```bash
python launch_async_mi_core.py -n "Explore_Device_Name" -m "model_filename" -t "KeyPress"
```

### `launch_async_mi_diagnostic.py`
Runs real-time MI classification with visual UI feedback.

**Usage:**
```bash
python launch_async_mi_diagnostic.py -n "Explore_Device_Name" -m "model_filename"
```

## Core Components (src/)

- **`analysisMI_classes.py`** - Data analysis and model training classes
- **`async_mi_core.py`** - Real-time MI classification engine
- **`async_mi_diagnostic_class.py`** - Wrapper around mi_core that provides visual feedback
- **`record_MI_class.py`** - Experiment recording interface
- **`helper_functions.py`** - Signal processing utilities
- **`constants.py`** - System-wide parameters and settings
- **`self_threaded_process_interface.py`** - Threading interface for async operations

## Workflow

1. **Record data:** Use `launch_record_experiment.py` to collect training data
2. **Train model:** Use `launch_train_and_save_model.py` to create classifier
3. **Run BCI:** Use `launch_async_mi_core.py` or `launch_async_mi_diagnostic.py` for real-time control

## Requirements

- Python 3.9
- Explore EEG device (unless using mock files)
- See `requirements.txt` for Python dependencies

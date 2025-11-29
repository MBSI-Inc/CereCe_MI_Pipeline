# MI_2 Package Installation Guide

## Overview

The MI_2 package has been set up as a proper Python package that can be installed and used across your system. Here are several ways to use it:

### Install Conda
 - Install from [Conda](https://docs.conda.io/projects/conda/en/latest/index.html) website. You can use the Miniconda variant.

### Option 1: Install with Requirements File (Recommended)

```bash
conda create -n bci python=3.11.9
conda activate bci

# Navigate to the MI_2 directory
cd "<path to the MI_2 directory>"

# Install dependencies first
pip install -r requirements.txt

# Then install the package in development mode
pip install -e .
```

If your terminal isn't able to find conda, see [this overflow post](https://stackoverflow.com/questions/28612500/why-anaconda-does-not-recognize-conda-command)

## Usage After Installation

Once installed, you can import the package from anywhere in your Python environment:

```python
# Import specific functions
from mi2_bci import (
    custom_filter,
    filter_epoch,
    PSD_epoch,
    SAMPLING_FREQ,
    LOW_FREQ,
    HIGH_FREQ
)

# Import classes
from mi2_bci import MI_analyse, MI_classifier, AsyncMICore

# Import everything
from mi2_bci import *
```

## Uninstalling

To uninstall the package:

```bash
pip uninstall mi2-bci
```
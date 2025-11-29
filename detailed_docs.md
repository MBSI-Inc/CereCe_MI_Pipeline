# Detailed Docs

This document is to provide more detail on the implementation of MI 2.

## Entrypoints
Entry points are as specified in the README. They run from the command line. 

There are four main entry points:
 - launch async mi core
 - launch async mi diagnostic
 - launch record experiment
 - launch train and save model

All entry points start by processing relevant command line arguments and apply valid default values.

## Workflow
1. Launch record experiment
    - Connects to EEG worn by experimentee and begins recording data (todo: move this to the Record class)
    - Begins recording experiment as implemented in the Record class (record_MI_class)
        - The record class displays a UI which prompts the experimentee to attempt MI or rest. It does this in a set amount of 'blocks'. The timestamps of these prompts are sent to Explore, which saves them in a CSV alongside the EEG recordings
    - The end result are csvs containing the recorded EEG signals and the timestamps of the rest/MI prompts. IE, the features and labels for ML to learn from. Explore refers to these as 'codes'.
2. Launch train and save model
    - First uses MI_analyse from analysisMI_classes.
        - This loads up the raw data generated from step 1 and pre-processes them into a form more readily used for ML
        - MI_analyse pre-processes by:
            - Taking the raw EEG signals and seperating them based on the timestamps/codes (MI or Rest labels).
            - Applying Cz re-referencing which is a tested and established method of pre-processing that aims to remove noise artefacts shared across electrodes and minimise removing the MI information.
            - Further decomposing the signals by chopping them into chunks called 'epochs'. 
            - These epochs undergo signal filtering to isolate the signals of interest (Beta waves).
            - 'Bad' epochs are rejected. These are epochs with anomalous peak to peak amplitudes.
            - These epochs then get converted to PSDs. 
            - The two types of epochs (MI and Rest) and combined by type into datasets.
            - The results are two sets of PSDs, one corresponding to periods of MI, the other corresponding to periods of Rest.
            - Note that many of the functions used here are stored in the shared helper functions. These functions are re-used during classification (step 3) to ensure the same kind of data processing is used across both the contexts of training and model usage.
    - Secondly, uses MI_classifier to train a model using the training data genererated earlier.
        - Loads up the datasets generated from MI_analyse. 
        - Uses an LDA and trains on the datasets given. 
        - Pickles this model for later use.
    - The end result is an LDA model trained on the data recorded from launch record experiment.
3. Launch async MI (core or diagnostic). Diagnostic is just a wrapper around core. Launch async MI Core does the following:
    - Connect to an EEG worn by a user (NOT experimentee)
        - This time is under the context of wheelchair usage.
    - Starts an instance of AsyncMICore (or Diagnostic)
        - This starts a thread which asynchronously provides MI/Rest classifications using the model trained by Launch train and save model.
        - It first unpickles the model that has been pre-trained in step 2. 
        - It subscribes to the connected Explore.
            - MI Core has a data buffer. Subscribing to Explore means that every time a new EEG signal sample is collected by the EEG, it is pushed to the data buffer.
    - Starts the async thread from AsyncMICore
        - This thread repeatedly does the following:
            - Checks if there is sufficient data in the data buffer.
            - If true, take an epoch from the data buffer
                - Process the data buffer using the same methods used in step 2 (training). This is facilitated through the use of the shared helper functions.
                - Feed the resulting PSD into the trained model and record the output classification.
                - Apply an exponential filter to this model output.
                - Store both the raw classification prediction AND the filtered prediction.
            - (TODO: rename to smoothing) The result is that the AsyncMICore class stores both the current exponentially filtered MI/Rest prediction and the most recent prediction.
            - These prediction can, at any time, be pulled from an outer thread by the calling of the pull_predictions class.
    - Launch async MI core can then, at any time, display the current prediction state of the AsyncMICore thread through keyboard commands.
    - The difference between MICore and MIDiagnostic is that Diagnostic repeatedly takes the output from Core and displays that output using a UI, instead of using keyboard commands to display the output on the console.
4. Integration:
    - AsyncMICore is the intended class for integration outside of the BCI subsystem. 
        - An external ingestor of MICore should mimick the structure of launch async mi core IE:
            - Connect to EEG using Explore.
            - Start an instance of AsyncMICore.
            - (TODO: consider starting this thread as part of AsyncMICore's init)Start the internal thread of AsyncMICore.
            - Call AsyncMICore.getData() to retrieve the latest MI/Rest prediction and the smoothed prediction.
## Key Concepts
- Code:
    - Decoupling: Keep the workflow steps decoupled. Implementation changes should minimally affect the other steps.
    - Repeatable: Each workflow step should be repeatable given the previous steps have been completed. IE, the results of each step should be recorded and NOT need to be re-run each time.
    - (TODO: Do this for analysisMI_classes) Function Safety: Which functions are available outside of each class? Which functions should be private? Add two underscore in front of functions which should only be used within the class that it is defined EG AsyncMICore.__exponential_filter().
    - (TODO: does python do interfaces?) Interfaces: Closely related to function safety. Each class should have a clear interface on how other classes can interact with it. IE, by using private/public functions, it becomes more clear which functions are intended for use by other classes.
    - (TODO: extract more constants, ensure usage of these constants) Constants: There are certain hardcoded values which should be left as constants EG high/low freq for beta wave filtering and epoch size.
        - (TODO: extract analysis rate to a constant (it is currently 0.1))
 - Threading (VERY IMPORTANT):
    - Any infinitely running threads should have Daemon set to True. What this does is kill the thread when the outer thread (such as your running python code) is ended. Without this, you run a high risk of leaving an infinitely running thread on your machine which can be a huge pain to find and remove, especially if the machine it is running on does not have a UI (like the wheelchair controller). 
 - Performance:
    - The wheelchair controller (or any other integration) will likely have low memory space. When coding, keep memory performance in mind EG see the complex data buffer management in AsyncMICore.__analyse_data(). Notice how it is formulated in a way where the data buffer literally cannot grow beyond a certain size. (TODO: consider adding a warning console output if the data buffer needed trimming? It would indicate a mismatch between constants somewhere EG mismatch between sampling freq, signal length, overlap, and analysis rate)



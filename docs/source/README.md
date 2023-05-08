# Launching a Polydelta Model Using Baseten
January 30, 2023

## Overview
This memo covers launching a pre-trained PolyDelta model using Baseten. The main steps involved are deploying the model to Baseten and building a simple app view to allow frontend input to the model.

## Setup
Follow these steps to set up the folders and environments needed for deployment. 

### VS Code Setup
1. Locally clone the **baseten-deploy-demo** from the PolyDelta github.
2. Create a folder **model-name-deployment** filling in model-name, then open it in VS Code.
    1. It will be helpful to have the project folder of the model you want to deploy (henceforth referred to as “the model”) open in another VS Code window for easy copy-pasting. The same goes for the cloned baseten-deploy-demo folder.
3. Create a folder **model_files** in the **model-name-deployment** folder.
4. From the **baseten-deploy-demo** folder, copy the **baseten-deploy.ipynb** file,  paste it in the **model-name-deployment folder.**
5. Open a terminal and `cd` into the **model-name-deployment** folder. Then create and activate a conda env **model-name-baseten-deploy** for the project.
6. Copy the model file(s) from the model’s project folder  (.pkl, .pb, .h5, etc) into the **model_files** folder of the **model-name-deployment** folder.

### Baseten Setup
1. Log in to PolyDelta’s Baseten account, go to the models page, and click “**Deploy your own model**”.
2. Follow the instructions up until, but not including copying the deployment script. Name the model using lowercase letters and dashes (e.g. model-name).

## Deployment
Follow these steps to deploy the model to Baseten. Once completed, the model can be called in code and using the curl command.

1. Open the **baseten-deploy.ipynb** file in the **model-name-deployment** folder. This file will be modified to fit the model being launched.
2. In the **Imports** cell, add whatever imports are necessary to load a trained, callable version of the model.
3. Paste the **MODEL_API_KEY** in the **Login** cell.
4. Write code that loads a trained, callable version of the model in the **Load** cell. 
    1. Example load of a trained, pickled model is shown.
5. In the **Create** cell, replace occurrences of **model_name**,  following the present convention.
6. Run the **Import**, **Login**, **Load**, and **Create** cells. A folder called **model_name_truss** should be created.
7. Open **model.py** in the **model_name_truss** folder and add the line `model_input = model_input['input']` before the first line in the `predict` function. `model_input` can be of any format, but it is formatted this way to allow for easy POST requests to the API.
8. If the model input preprocessing step (or output post-processing) involves the use of other models, the **model_name_truss** folder needs to be modified as follows: 
    1. Paste the trained model file(s) of the preprocessor model(s) into the **model_name_truss/data** folder.
    2. In the **model_name_truss**, open **model.py**. Copy and refactor the preprocessing code from the model project folder into the `preprocess` function. Include any necessary imports here as well.
    3. If other files are needed **after** a preprocessing model is used and before the input is fed to the model, place these files in the **data** folder as well.
    4. Look through **model.py** in the **jobs_classifier_truss** folder in **baseten-deploy-demo** for a simple preprocessing example with two preprocessor models. Pre/post processing required imports can be added to the `requirements` section of the truss folder’s **config.yaml**.
    5. For post-processing models, follow the above steps, instead pasting in any post-processing files used **before** the last post-processing model is used. To combine multiple model outputs into one API call (not pre/post processor models), follow the steps in the **Deployment Extra** section below.
9. In the “**Deploy**” cell of **baseten-deploy.ipynb**, replace occurrences of `model-name` and run the cell to deploy the `model_name_truss` to Baseten.
    1. Once deployed, navigate to Polydelta’s Baseten models page and click the newly created model. In the left "Versions" nav-bar, "Draft" should be selected. Note the “**Call via Baseten Client**” code in the top right corner. The model version ID shown here is used to call the model.
10. In the first **Test** cell, copy, paste, and refactor preprocessing code (that doesn’t involve other models, covered earlier). Format the `model_input` variable as described. Run this cell.
11. In the second **Test** cell, paste the model version ID (from the deployed model’s Baseten page) in the specified place. Perform any remaining post-processing here and print/save the output for debugging. Run this cell and ensure the deployed model is outputting expected results.
    1. Note the formatting of `model_input` in this cell. When making Curl or POST requests, the request body should be formatted the same way (`{ 'input': ["desired_model_input"] }`).
12. Test, and re-deploy until the deployed model is outputting expected results. Then in the model's Baseten page, click the 3 dots by the "Draft" version and select "Promote to primary". Now the model can be called using using the model ID instead of the model version ID. The primary model is also what responds to API calls.

## Deployment Extra: Combining Multiple Models Into Single API Deployment
Combining multiple models into a single deployment to, say, get output from 2 or more models in a single API call is similar to adding pre/post processor models. First follow the steps in the **Deployment** section for the main model being deployed. Then for each additional model being combined with the main model, follow these steps:
1. Follow steps 4-6 in the **Deployment** section for the additional model.
    1. If the additional model has pre/post processor models, hold off on following those steps until after this model has been added to the main model's truss.
2. Open the **config.yaml** files of the truss created for the additional model and the main model and navigate to the `requirements` sections. In the main model truss config's `requirements` section, add any requirements from the (newly created) additional model's truss config that are not arlready present.
3. In the main model's truss **config.ymal** `requirements` section, add any missing requirements needed to load a callable version of the model in code.
4. Copy the additional model's model file(s) into the **data** folder of the main model truss.
5. The remaining actions are done in the main model truss. In **model.py**: 
    1. Import any modules needed for loading and processing the additional model and its inputs/outputs.
    2. In the `__init__` function, initialize the additionnal model to `None`, like how the main model is initialized. You may need to add params to the **config.yaml**, note how yaml params are fetched to see how to do this.
    3. In the `load` function, load a callable version of the additional model and set the additional model's variable (currently `None`) to the loaded model.
    4. To add the additional model's output to the API's `model_output`, write a function(s) that call the additional model and get its output, then in the `predict` function, add a field to the `model_output` dict. It should be a line like: `model_output['addtl_model_output'] = getAddtlModelOutput(model_input)`.
6. Proceed deploying the main model's truss as described in step 7 of **Deployment** above.

## Build App in Baseten
This step involves creating and refactoring pre and post processing code files, creating a model calling worklet, and creating a view to allow frontend model calls. Once completed: 
- A model calling worklet API will be autogenerated, allowing one to call the model in code with nigh-on unprocessed user input.
- A frontend view that takes in user input and outputs processed model output will be accessible from an auto-generated url. This view can aslo be exported as an iframe.
The **USA Jobs Location Classifier App Test** app example in Polydelta’s Baseten is a valuable reference for this section. Have it open for layout and code snippet guidance. Follow these steps to build an app using a deployed model in Baseten:

### Set up Files Section
1. Navigate to Polydelta’s Baseten Applications page and click **Create an application**. In the resulting application builder page, click the **Untitled Application**’s name in the top left corner and rename it.
2. In the **File** tab in the bottom left, click **main.py**. Add two functions `preprocess` and `postprocess` with the same params and return value as the given `passthrough` function example.
    1. **Main.py** functions require this function signature to be accessed by worklets.
3. Upload/copy pre and post processing files not requiring other models into the **Files** section, similar to how it was done in the **model-name-deployment** folder.
4. In the **Files** section, open **requirements.txt** and add any requirements necessary for pre and post processing, then click “**Save & install**”.
5. Copy, paste, and refactor pre and post-processing code written in **baseten-deploy.ipynb** into the `preprocess` and `postprocess` functions in the Baseten app’s **main.py**. 
    1. In the `preprocess` function, the `block_input[“inputs”]` variable contains user input. 
    2. In `postprocess`, the `block_input[“model_output”]` variable contains the `model_output` dictionary. Then `model_output[“predictions”]` contains the model predictions.
    3. This naming and nesting of model output may vary slightly based on the model framework. Take note of what (and what type of) data is inputted and outputted by different steps in the model execution pipeline.
    4. Non-output variables that need to be used in downstream pipeline functions (ex: user input from pre-processing used in results display coded in post-processing) should be stored in the env dictionary like so: `env[“var_to_store”] = var_to_store`.

### Create Model Calling Worklet
1. In the app’s **Worklets** section open **Worklet1**. Hover over **Worklet1** and click the three dots, and rename the worklet (ex: Feed Model).
2. Rename the "Untitled code block" worklet node **Preprocess**, set **File** to **main.py** and **Function** to `preprocess`. 
3. Click **Add block** and select **Model**. Set **Model** to the deployed model and **Version** to **Primary**.
4. Click “**Add block**” and select **Code**. Set **File** to **main.py** and **Function** to `postprocess`.
5. Click “**Run worklet**” to test the worklet. In the “**JSON Input**” section, format input like so:
    1. `{ “inputs”: “USER_INPUT_HERE” }`

### Create View
1. Click **View1** in the app’s Views section and rename if desired.
2. Use the drag and drop view builder to build a simple frontend for the app. See the “**USA Jobs Location Classifier Test**”  app for guidance setting up event handlers, accessing worklets/code, and controlling components and their values.
3. Click **Share** in the top right corner to get a public facing url for the app.

## Debugging
The most common and easiest to solve error is a file reference error. Many files are copied, pasted, and moved around throughout this process. Whenever referenced in code, ensure they are properly navigated to, taking note of their new locations.

### Deployment
- The deployed model’s logs sometimes provide more info on failure outputs in the VS Code terminal.
- If the error “This endpoint must be given a valid JSON dictionary” (or an error 400 in the model logs)  appears on calling the deployed model, the model input is being formatted incorrectly. Take careful note of what and what type of data the model ingests.

### Build App in Baseten
- If requirements.txt fails to install, be sure unnecessary model framework libraries (e.g. scikit-learn) are not being imported. If the model requires other models for pre or post processing, this procedure is explained in step 6 of the Deployment section.
- If testing the model calling worklet fails, ensure that pre and post processing code main.py is properly refactored and test input in the “**JSON Input**” section of the worklet tester is formatted correctly.

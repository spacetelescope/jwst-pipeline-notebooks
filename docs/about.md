# What does this CI system do?
There are a few different actions that provide different CI functionalty.
- Validation/Execution - ci_validation.yml
  - This workflow exercises the notebook to validate that it properly executes without failure, and validates the output.
  - Execution of the notebook is accomplished through the use of the jupyter utility 'nbconvert'
    - https://nbconvert.readthedocs.io/en/latest/
  - Validation is performed using pytest and a pytest plugin 'nbval' 
    - https://nbval.readthedocs.io/en/latest/
- HTML Builder/Deployment
  - Static HTML pages of rendered/executed notebooks are deployed to Github pages.
  - The workflow uses "Jupyter-Book" as a backend to perform the rendering, the page inclusion as well as the overall look and feel.
    -  https://jupyterbook.org/en/stable/intro.html
-  Nightly/Weekly Builds
  - Notebooks are exercised on a scheduled cycle that can be defined in the workflow. The nightly build performs the validation and execution steps as the validation workflow, but does not regenerate HTML.
  - The workflow breaks up notebooks into a matrix and executes each individually on its own worker node, errors are reported in a summary under the actions tab of the repository as well as emailed to the watchers.
  - The intent is to capture issues regarding updates to requirements that cause notebook failures or any other transient environmental issues.

## Getting started
The easiest method for creating a new repository with the CI build machinery is to use the deployable template.  This will provide the required directory structure support configuration files required to operate the CI system.
- Navigate to https://github.com/TheRealZoidberg/notebook_ci_template (This will eventually be moved to STScI repos)
- On the top right side of the page, select the green button labeled "Use this template"
- Select the repository 'owner' (Your own personal github repo for example) and enter a new repository name.
- ** It is important to select "Include all branches" as github pages requires its own documents branch.
- Finally select the "Create repository from template" button.  A new repository will be created with all the required files/structure.

### Configuration
Now that a new repository has been created, there are a few more steps to finish.
- Jupyter-book configuration: _config.yml
  -  This configuration file contains all of the variables to customize the rendered HTML pages.  The entries that should be edited are marked with '(CHANGE THIS)'.
  -  General settings:
    - Title: The title of the notebook collection
    - author: STScI or a specific author to the notebook collection
    - logo: log.png - a logo that displays the mission or a special feature that defines the collection.
  - execute: 
    -  execute_notebooks: force - defines how and when notebooks are executed during HTML generation - See https://jupyterbook.org/content/execute.html  
  - html:
    -  google_analytics_id: - applies a google analytics tracking ID to every html page generated
    -  use_issues_button: true or false - Adds a button to report an issue directly to github
    -  use_repository_button: true or false - Adds a button that allows the user to directly visit the repository for the notebooks
  - launch_buttons:
    -  thebe: true or false - Adds a button that implements thebe into the notebook, this uses a mybinder kernel in the background to allow cell execution from the static pages.
    -  colab: true or false - Adds a button that opens the notebook in Google colab - allowing the user to fully run the notebook on an active node.

- Notebook Requirements (This section is currently under development, and may change) 
  - Typically when a notebook is added to the repository, it will come with a developer created 'requirements.txt' file.  When there is a large collection of notebooks the contents of these files can contain many dupilcates of requirements but potentially all with different versions.
  - When running in a CI environment it is important to keep a consistant environment.  
  - To do this there is a script included in the template that scans for notebooks and uses a utility 'pipreqsnb' to extract only the needed requirements from each notebook. It then creates a global requirements file in the repository root that contains all of the unique requirements from the collection, unpinned from versions, ensuring that the latest releases are used.
  - To run the script, first 'pip install pipreqsnb' - and then execute the script './reqBuilder.sh'


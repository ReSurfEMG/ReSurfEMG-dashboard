# ReSurfEMG-dashboard

Dashboard to use the ReSurfEMG library

## Getting started

This dashboard requires that you have an environment with certain dependencies including dash. We recommend that you do the following:

    Install all Python packages required, using conda and the
    `environment.yml` file.
   * The command for Windows/Anaconda users can be something like:
     `conda env create -f environment.yml`.
   * Linux users can create their own environment by hand.

Once you have entered an environment with the necessary packages, run python  resurfemg-dashboard/index.py and a url for the dashboard should appear in your terminal (open the url). 
    `python resurfemg-dashboard/index.py`.

## Building executable file

To ease the distribution and the use of the ReSurfEMG Dashboard, it is possible to build an executable file, through the following steps:

- Activate the virtual environment 
- Install the PyInstaller by running `pip install pyinstaller`
- Run `pyinstaller main.spec`

If the process is successful, the resurfemg_dashboard.exe file can be found in the /dist/main folder. By launching the executable file, the dashboard will be prompted. 

N.B. The dist folder containing the executable file should be created and uploaded when a new release of the dashboard is created.


### Author: Aaron Rehfeldt

# Covid19-Config-Generator
Sister Application to Covid19 Vulnerable Data Viewer. Used to generate a configurable file for all measures so our visualization tool may safely fetch and use data from the CDC's NEPHTN API

# Functions
### View\modify working config (In Progress)
1. View list of all measures (Complete)
2. View details of all measures (Complete)
3. View details of a selected measure (In Progress)
4. Modify parameters of a selected measure (In Progress)
5. Delete a measure from working config file (In Progress)

### Load new measures into working config from NEPHTN API (Complete)
1. Select Content Area
2. Select Indicator Area
3. Select Measure Name
4. Test Measure is valid for our tool
5. Initialize Measure Parameters

### Load a config from disk and overwrite/append to current config (In Progress)
1. Load a config and overwrite working config (Complete)
2. Load a config and append to working config (Complete)
3. Test that config is in correct format (In Progress)
4. Test that each measure is in the correct format (In Progress)
5. Prompt for choice to initialize missing parameters of certain measures (In Progress
5. Promt for choice to remove extra paramaters of certain measures (In Progress)

### Clear working config file from memory (Complete)
1. Ask for confirmation

### Publish config file for use in visualization tool (In Progress)
1. Publish config under input filename (Complete)
2. Allow user to look over config file before publishing (Complete)
3. Allow user to make final modification to config before publishing (In Progress)

# Features

### Confirmation messages for every modification action on config/measure

### Test cases to ensure additional measures are valid
  **TODO:** 
  * Add easy method to implement new tests

### Automatically set certain measures from API fetches

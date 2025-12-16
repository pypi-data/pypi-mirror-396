# Sponsor this project
Follow [this link](https://github.com/sponsors/billingross) to support development of the Circuity Database Management System.

# circuitydatabase
Source for the Circuity Database designed to be distributed through PyPI.

# Installation instructions
```
python3 -m pip install circuitydatabase
```

# Running circuity from the command-line
From the command line or terminal application on my computer I can invoke the following commands to operate an instance of Circuity Database.
```
% python3 -m pip install circuitydatabase
% circuity --csv-path example/directory/data_file.csv --query 'arizona cardinals wide receiver name'
team,position,first name,last name
arizona cardinals,wide receiver,andre,baccellia
arizona cardinals,wide receiver,michael,wilson
arizona cardinals,wide receiver,xavier,weaver
arizona cardinals,wide receiver,zay,jones
arizona cardinals,wide receiver,simi,fehoko
arizona cardinals,wide receiver,marvin,harrison jr.
arizona cardinals,wide receiver,greg,dortch
```

# Example dataset
Find an example comma separated values file with ESPN National Football League roster data [here](https://drive.google.com/file/d/1OYTkVTk7ZbTOCtsv-6kems1GvTLpyxod/view?usp=share_link).

# Developer instructions
## Publishing new versions

```
% python3 -m build
% twine upload dist/*
```

## Install unpublished changes
```
# Install existing pip versions of Circuity to avoid collisions
% python3 -m pip uninstall circuitydatabase
# Install Circuity from local source in the root directory
% cd circuitydatabase
% python3 -m pip install . --force
```

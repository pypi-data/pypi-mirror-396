# geocif


[![image](https://img.shields.io/pypi/v/geocif.svg)](https://pypi.python.org/pypi/geocif)
[![image](https://img.shields.io/conda/vn/conda-forge/geocif.svg)](https://anaconda.org/conda-forge/geocif)


**Generate Climatic Impact-Drivers (CIDs) from Earth Observation (EO) data**

[Climatic Impact-Drivers for Crop Yield Assessment at NASA Harvest](https://www.loom.com/share/5c2dc62356c6406193cd9d9725c2a6a9)

**Models to visualize and forecast crop conditions and yields**


-   Free software: MIT license
-   Documentation: https://ritviksahajpal.github.io/yield_forecasting/


### Upload package to pypi
1. Update requirements.txt
2. Update version="A.B.C" in setup.py
3. Navigate to the directory containing `setup.py` and run the following command:
```python
pipreqs . --force --savepath requirements.txt
mamba env export > environment.yml
python setup.py sdist
twine upload dist/geocif-A.B.C.tar.gz
```


## Credits

This package was created with [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the [giswqs/pypackage](https://github.com/giswqs/pypackage) project template.

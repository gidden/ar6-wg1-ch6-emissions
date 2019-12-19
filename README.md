# Requires

- `pandas`
- [`pyam v0.3.0`](https://pyam-iamc.readthedocs.io/) or greater

# Data

Data comes from a variety of sources, including the RCPDB for RCP and RCP
historical data, van Marle et al. and Hoesly et al. for CMIP6 historical data,
and Gidden et al. for CMIP6 data.

# Files

- `add_categories.py` provides some `pyam` processing for specific color palletes
- `plotting.yaml` provides configuration for `pyam` plot properties
- `plots.py` generates the plots themselves
- `*.csv` is the data from which the plots are generated
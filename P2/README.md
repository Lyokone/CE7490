# RAID 6 Implementation
## Librairies
In order to use this implementation, you need to install the `pyfinite` librairie.
```
pip3 install pyfinite
```
This implementation have been tested with Python 3.6

## How to use
Put `controller.py` and `parity.py` in the same folder. First launch can take longer.

Initialize RAID6 with default parameters (can be changed in \_\_init__):
```python
import controller

R = controller.RAID6()
```

Write data from user input:
```python
R.write_data("Data to store on RAID6", "name_of_the_data")
```

Write data from file:
```python
R.write_data_from_file("picture.jpg", "picture")
```

Update data from file:
```python
R.update_data_from_file("picture_updated.jpg", "picture")
```

Get data to console:
```python
R.get_data_from_name("picture")
```

Get data to file:
```python
R.get_data_to_file_from_name("picture_out.jpg","picture")
```

Recover up to 2 disks:
```python
R.recovering_disks([3,4])
```


## Acknowledgment
We thank the professor Anwitaman DATTA for teaching the course CE7490 Advanced Topics in Distributed Systems. This work was done during an exchange semester at Nanyang Technological University in 2018 by Bernos Guillaume, Bindics Gergery and Finck Quentin Nicolas.
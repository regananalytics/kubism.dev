# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from kubism.kubism import Model, Object, Field


# %%
# Create new model
model = Model()
rpi = Object('RpiTherm')
model += rpi


# %%
rpi.add_field('Temp_C', 'double precision')
rpi.add_field('Temp_F', 'double precision')
rpi.set_deployment('./examples/py/therm.py',
        parent_image='arm32v7/python:3-buster',
        host='172.24.12.160',
        volumes='/sys/bus/w1/devices/')


# %%
print(rpi.get_yaml())


# %%
print('Done!')
from pyDataverse.api import NativeApi
from pyDataverse.models import Dataverse
from pyDataverse.models import Dataset
from pyDataverse.models import Datafile
from pyDataverse.utils import read_file

api = NativeApi('http://172.26.63.115:8080', 'dbcdd06e-2883-4db1-9771-bbf8210fa8f2')

resp = api.get_info_version()
print(resp.json())

dv = Dataverse()
dv_filename = "dataverse/dataverse.json"
dv.from_json(read_file(dv_filename))
dv.get()
type(dv.get())

# Dataverse
resp = api.create_dataverse(":root", dv.json())
resp = api.publish_dataverse("test-pyDataverse")

# Dataset
ds = Dataset()
ds_filename = "dataverse/dataset.json"
ds.from_json(read_file(ds_filename))
ds.get()
resp = api.create_dataset("test-pyDataverse", ds.json())
resp.json()

# Datafile
df = Datafile()
df_filename = "dataverse/datafile.txt"

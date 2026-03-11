from pynetdicom import AE
from pynetdicom.sop_class import CTImageStorage
import pydicom

ds = pydicom.dcmread("test.dcm")

ae = AE()
ae.add_requested_context(CTImageStorage)

assoc = ae.associate("dicom_server", 11112)

if assoc.is_established:
    status = assoc.send_c_store(ds)
    print("status:", status)
    assoc.release()
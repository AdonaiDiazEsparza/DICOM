from pynetdicom import AE, evt
from pynetdicom.sop_class import CTImageStorage
import os

STORE_PORT = 11113

def handle_store(event):

    ds = event.dataset
    ds.file_meta = event.file_meta

    filename = f"/data_received/{ds.SOPInstanceUID}.dcm"

    ds.save_as(filename)

    print(f"[CLIENT] imagen recibida -> {filename}")

    return 0x0000

handlers = [(evt.EVT_C_STORE, handle_store)]
ae = AE() 

ae.add_supported_context(CTImageStorage)

print(f"Receptor DICOM escuchando en puerto {STORE_PORT}...")
ae.start_server(("0.0.0.0", STORE_PORT), block=True, evt_handlers=handlers)
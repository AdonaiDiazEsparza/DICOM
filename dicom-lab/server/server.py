from pynetdicom import AE, evt, StoragePresentationContexts
import pydicom
import os

STORE_DIR = "/data"

def handle_store(event):
    ds = event.dataset
    ds.file_meta = event.file_meta
    
    filename = os.path.join(STORE_DIR, f"{ds.SOPInstanceUID}.dcm")
    ds.save_as(filename)

    print("Recibido:", filename)

    return 0x0000

handlers = [(evt.EVT_C_STORE, handle_store)]

ae = AE()

for context in StoragePresentationContexts:
    ae.add_supported_context(context.abstract_syntax)

ae.start_server(("0.0.0.0", 11112), evt_handlers=handlers)
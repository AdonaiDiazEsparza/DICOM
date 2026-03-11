from pynetdicom import AE, evt, StoragePresentationContexts
import pydicom
import os

STORE_DIR = "./data"

def handle_store(event):
    ds = event.dataset
    ds.file_meta = event.file_meta
    
    filename = os.path.join(STORE_DIR, f"{ds.SOPInstanceUID}.dcm")
    ds.save_as(filename)

    print("a:", filename)

    return 0x0000

handlers = [(evt.EVT_C_STORE, handle_store)]

ae = AE(ae_title="SERVIDOR_DICOM")

ae.add_supported_context(CTImageStorage)
ae.add_supported_context(MRImageStorage)
ae.add_supported_context(SecondaryCaptureImageStorage)

print("Iniciando servidor DICOM en puerto 11112...")

ae.start_server(("0.0.0.0", 11112), evt_handlers=handlers)

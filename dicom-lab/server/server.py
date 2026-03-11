from pynetdicom import AE, evt
from pynetdicom.sop_class import Verification, CTImageStorage

import pydicom

def handle_store(event):
    ds = event.dataset
    ds.file_meta = event.file_meta

    ds.save_as("/data/received.dcm")

    print("Imagen recibida")

    return 0x0000


handlers = [(evt.EVT_C_STORE, handle_store)]

ae = AE()

ae.add_supported_context(Verification)
ae.add_supported_context(CTImageStorage)

print("Servidor escuchando en puerto 11112")

ae.start_server(("0.0.0.0", 11112), evt_handlers=handlers)
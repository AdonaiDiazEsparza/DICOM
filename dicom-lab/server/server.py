from pynetdicom import AE, evt
from pynetdicom.sop_class import (
    Verification,
    CTImageStorage,
    StudyRootQueryRetrieveInformationModelFind,
    StudyRootQueryRetrieveInformationModelMove
)

import pydicom
from pydicom.dataset import Dataset


# -------------------------
# C_ECHO
# -------------------------
def handle_echo(event):
    addr = event.assoc.requestor.address
    print(f"[C-ECHO] Peticion de verificacion desde {addr}")
    return 0x0000


# -------------------------
# C_STORE
# -------------------------
def handle_store(event):

    ds = event.dataset
    ds.file_meta = event.file_meta

    filename = f"/data/{ds.SOPInstanceUID}.dcm"

    ds.save_as(filename)

    print(f"[C-STORE] Imagen recibida y guardada -> {filename}")

    return 0x0000


# -------------------------
# C_FIND
# -------------------------
def handle_find(event):

    ds = event.identifier

    print("[C-FIND] Consulta recibida")
    print(ds)

    # no hay base de datos aún
    yield (0x0000, None)


# -------------------------
# C_MOVE
# -------------------------
def handle_move(event):

    print("[C-MOVE] Peticion de transferencia recibida")

    yield (0x0000, None)


# -------------------------
# Asociaciones
# -------------------------
def handle_assoc(event):
    addr = event.assoc.requestor.address
    print(f"[ASSOC] Conexion desde {addr}")


handlers = [
    (evt.EVT_REQUESTED, handle_assoc),
    (evt.EVT_C_ECHO, handle_echo),
    (evt.EVT_C_STORE, handle_store),
    (evt.EVT_C_FIND, handle_find),
    (evt.EVT_C_MOVE, handle_move),
]


ae = AE()

ae.add_supported_context(Verification)
ae.add_supported_context(CTImageStorage)
ae.add_supported_context(StudyRootQueryRetrieveInformationModelFind)
ae.add_supported_context(StudyRootQueryRetrieveInformationModelMove)

print("Servidor DICOM escuchando en puerto 11112")

ae.start_server(("0.0.0.0", 11112), evt_handlers=handlers)
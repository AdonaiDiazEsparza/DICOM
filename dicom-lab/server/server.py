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
    try:
        ds.save_as(filename, write_like_original=False)
        print(f"[C-STORE] Imagen recibida y guardada -> {filename}")
        return 0x0000
    except Exception as e:
        print(f"[C-STORE] Error guardando {filename}: {e}")
        return 0xA700  # out-of-resources or similar status


# -------------------------
# C_FIND
# -------------------------
def handle_find(event):
    identifier = event.identifier
    print("[C-FIND] Consulta recibida")
    print(identifier)

    # Buscamos en /data cualquier .dcm y construimos respuestas
    import os
    from pydicom import dcmread
    data_dir = "/data"

    files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.lower().endswith(".dcm")]
    if not files:
        # no matches: final success with no dataset
        yield (0x0000, None)
        return

    for fpath in files:
        try:
            ds = dcmread(fpath, stop_before_pixels=True)
        except Exception as e:
            print(f"[C-FIND] Error leyendo {fpath}: {e}")
            continue

        # Construc. dataset de respuesta: incluir los tags que quieras que el SCU vea
        resp = Dataset()
        resp.PatientName = getattr(ds, "PatientName", "")
        resp.PatientID = getattr(ds, "PatientID", "")
        resp.StudyInstanceUID = getattr(ds, "StudyInstanceUID", "")
        resp.QueryRetrieveLevel = "STUDY"

        # 0xFF00 = pending (hay resultados)
        yield (0xFF00, resp)

    # Finalmente indicar éxito y fin de resultados
    yield (0x0000, None)


# -------------------------
# C_MOVE
# -------------------------
def handle_move(event):

    # IP del cliente que pidió el MOVE
    client_ip = event.assoc.requestor.address

    # puerto donde el cliente debe aceptar C-STORE
    client_port = 11113

    print(f"[C-MOVE] Cliente solicitante: {client_ip}")

    # decirle a pynetdicom dónde enviar las imágenes
    yield (client_ip, client_port)

    files = [f"/data/{f}" for f in os.listdir("/data") if f.endswith(".dcm")]

    print(f"[C-MOVE] Enviando {len(files)} archivos")

    for f in files:
        ds = pydicom.dcmread(f)
        yield ds


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
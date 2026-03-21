from pynetdicom import AE, evt
from pynetdicom.sop_class import (
    Verification,
    CTImageStorage,
    StudyRootQueryRetrieveInformationModelFind,
    StudyRootQueryRetrieveInformationModelMove,
    StudyRootQueryRetrieveInformationModelGet
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
# C_GET
# -------------------------
def handle_get(event):
    import os

    addr = event.assoc.requestor.address
    identifier = event.identifier
    requested_study_uid = getattr(identifier, "StudyInstanceUID", None)

    print(f"[C-GET] StudyInstanceUID solicitado: '{requested_study_uid}'")

    data_dir = "/data"
    matched_files = []

    for f in os.listdir(data_dir):
        if not f.endswith(".dcm"):
            continue

        fpath = os.path.join(data_dir, f)

        try:
            meta = pydicom.dcmread(fpath, stop_before_pixels=True)
            file_uid = str(getattr(meta, "StudyInstanceUID", "")).strip()
            req_uid  = str(requested_study_uid).strip() if requested_study_uid else None

            # Debug: ver qué UIDs hay en disco
            print(f"[C-GET] Archivo: {f} | UID en archivo: '{file_uid}'")

            if req_uid and file_uid != req_uid:
                continue

            matched_files.append(fpath)

        except Exception as e:
            print(f"[C-GET] Error leyendo metadata de {f}: {e}")


    yield len(matched_files)

    for fpath in matched_files:
        try:
            ds = pydicom.dcmread(fpath)
            print(f"[C-GET] Enviando: {os.path.basename(fpath)}")
            yield (0xFF00, ds)
        except Exception as e:
            print(f"[C-GET] Error enviando {fpath}: {e}")
            yield (0xC000, None)  # error en sub-operacion

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
    (evt.EVT_C_GET, handle_get),
]


ae = AE()

ae.add_supported_context(Verification)
ae.add_supported_context(CTImageStorage)
ae.add_supported_context(StudyRootQueryRetrieveInformationModelFind)
ae.add_supported_context(StudyRootQueryRetrieveInformationModelMove)
ae.add_supported_context(StudyRootQueryRetrieveInformationModelGet)

print("Servidor DICOM escuchando en puerto 11112")

ae.start_server(("0.0.0.0", 11112), evt_handlers=handlers)
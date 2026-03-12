from pynetdicom import AE, evt
from pynetdicom.sop_class import (
    Verification,
    CTImageStorage,
    StudyRootQueryRetrieveInformationModelFind,
    StudyRootQueryRetrieveInformationModelMove
)

import pydicom
from pydicom.dataset import Dataset
import argparse
import threading

SERVER = "dicom_server"
PORT = 11112
STORE_PORT = 11113


# -------------------------
# Handler para recibir C-STORE
# -------------------------
def handle_store(event):

    ds = event.dataset
    ds.file_meta = event.file_meta

    filename = f"/data/{ds.SOPInstanceUID}.dcm"

    ds.save_as(filename)

    print("Archivo recibido:", filename)

    return 0x0000


# -------------------------
# Servidor para recibir archivos
# -------------------------
def start_storage_scp():

    ae = AE()

    ae.add_supported_context(CTImageStorage)

    handlers = [(evt.EVT_C_STORE, handle_store)]

    print(f"[CLIENT] Storage SCP escuchando en {STORE_PORT}")

    ae.start_server(("0.0.0.0", STORE_PORT), block=True, evt_handlers=handlers)


# -------------------------
# C-ECHO
# -------------------------
def c_echo():

    ae = AE()
    ae.add_requested_context(Verification)

    assoc = ae.associate(SERVER, PORT)

    if assoc.is_established:

        status = assoc.send_c_echo()

        if status:
            print("C-ECHO OK")

        assoc.release()

    else:
        print("No se pudo establecer la asociacion")


# -------------------------
# C-STORE
# -------------------------
def c_store(path):

    ae = AE()
    ae.add_requested_context(CTImageStorage)

    ds = pydicom.dcmread(path)

    assoc = ae.associate(SERVER, PORT)

    if assoc.is_established:

        status = assoc.send_c_store(ds)

        print(status)

        assoc.release()


# -------------------------
# C-FIND
# -------------------------
def c_find(patient_name="*"):

    ae = AE()
    ae.add_requested_context(StudyRootQueryRetrieveInformationModelFind)

    assoc = ae.associate(SERVER, PORT)

    if assoc.is_established:

        ds = Dataset()
        ds.QueryRetrieveLevel = "STUDY"
        ds.PatientName = patient_name

        responses = assoc.send_c_find(
            ds,
            StudyRootQueryRetrieveInformationModelFind
        )

        for status, identifier in responses:

            if status:
                print("STATUS:", status)

            if identifier:
                print(identifier)

        assoc.release()


# -------------------------
# C-MOVE
# -------------------------
def c_move(study_uid):

    # arrancar SCP en segundo plano
    t = threading.Thread(target=start_storage_scp, daemon=True)
    t.start()

    ae = AE()

    ae.add_requested_context(StudyRootQueryRetrieveInformationModelMove)
    ae.add_requested_context(CTImageStorage)

    assoc = ae.associate(SERVER, PORT)

    if assoc.is_established:

        ds = Dataset()
        ds.QueryRetrieveLevel = "STUDY"
        ds.StudyInstanceUID = study_uid

        responses = assoc.send_c_move(
            ds,
            "CLIENT",
            StudyRootQueryRetrieveInformationModelMove
        )

        for status, identifier in responses:
            print("MOVE STATUS:", status)

        assoc.release()

    else:
        print("No se pudo establecer la asociacion")


# -------------------------
# CLI
# -------------------------
if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--action", required=True)
    parser.add_argument("--path")
    parser.add_argument("--patient")
    parser.add_argument("--study_uid")

    args = parser.parse_args()

    if args.action == "C_ECHO":
        c_echo()

    elif args.action == "C_STORE":
        c_store(args.path)

    elif args.action == "C_FIND":
        c_find(args.patient)

    elif args.action == "C_MOVE":
        c_move(args.study_uid)

    else:
        print("Accion no soportada")
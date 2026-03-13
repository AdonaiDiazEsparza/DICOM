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
def c_move(study_uid, device):
    ae = AE(ae_title=b'CLIENT_SCU')
    ae.add_requested_context(StudyRootQueryRetrieveInformationModelMove)
    
    assoc = ae.associate(SERVER, PORT)
    if assoc.is_established:
        ds = Dataset()
        ds.QueryRetrieveLevel = "STUDY"
        ds.StudyInstanceUID = study_uid
        
        responses = assoc.send_c_move(ds, device.encode(), StudyRootQueryRetrieveInformationModelMove)
        
        for status, identifier in responses:
            print(f"Estado del movimiento: {status.Status}")
        assoc.release()

# -------------------------
# CLI
# -------------------------
if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--action", required=True)
    parser.add_argument("--path")
    parser.add_argument("--patient")
    parser.add_argument("--study_uid")
    parser.add_argument("--device")

    args = parser.parse_args()

    if args.action == "C_ECHO":
        c_echo()

    elif args.action == "C_STORE":
        c_store(args.path)

    elif args.action == "C_FIND":
        c_find(args.patient)

    elif args.action == "C_MOVE":
        if args.device:
            c_move(args.study_uid, args.device)
        else:
            print("Falto agregar el dispositivo a mover")

    else:
        print("Accion no soportada")
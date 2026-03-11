from pynetdicom import AE
from pynetdicom.sop_class import (
    Verification,
    CTImageStorage,
    StudyRootQueryRetrieveInformationModelFind,
    StudyRootQueryRetrieveInformationModelMove
)

import pydicom
from pydicom.dataset import Dataset
import argparse

MESSAGE = """

Este es el cliente puede generar peticiones al servidor

Bienvenidos a la Villa APT!!!

"""

action_help = """
Puedes realizar las siguientes acciones

Acciones disponibles:
- C_ECHO: ver si hay conexion en el servidor
- C_STORE: Transferir imagen
- C_FIND: Encontrar Imagen
- C_MOVE: Pedir que se envien imagenes a otro

"""

# SERVER = "dicom_server"
SERVER = "127.0.0.1"

PORT = 11112


# Funcion para realizar el C_ECHO
def c_echo():
    ae = AE()
    ae.add_requested_context(Verification)

    assoc = ae.associate(SERVER, PORT)

    if assoc.is_established:

        status = assoc.send_c_echo()

        if status:
            print("C-ECHO OK")
        else:
            print("C-ECHO fallo")

        assoc.release()

    else:
        print("No se pudo establecer la asociacion con el servidor")

# Funcion para Realizar el C_STORE
def c_store(path):
    ae = AE()
    ae.add_requested_context(CTImageStorage)

    ds = pydicom.dcmread(path)

    assoc = ae.associate(SERVER, PORT)

    if assoc.is_established:
        status = assoc.send_c_store(ds)

        if status:
            print("C-STORE enviado correctamente")
        else:
            print("Error en C-STORE")

        assoc.release()
    
    else:
        print("No se pudo establecer la asociacion con el servidor")

# Funcion para realizar el C_FIND nos ayuda a encontrar los estudios de los pacientes
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

        for (status, identifier) in responses:
            if status and identifier:
                print(identifier)

        assoc.release()
    
    else:
        print("No se pudo establecer la asociacion con el servidor")

# Funcion que nos ayuda a obtener el estudio en especifico de un cliente
def c_move(study_uid, destination_ae="CLIENT"):
    ae = AE()
    ae.add_requested_context(StudyRootQueryRetrieveInformationModelMove)

    assoc = ae.associate(SERVER, PORT)

    if assoc.is_established:

        ds = Dataset()
        ds.QueryRetrieveLevel = "STUDY"
        ds.StudyInstanceUID = study_uid

        responses = assoc.send_c_move(
            ds,
            destination_ae,
            StudyRootQueryRetrieveInformationModelMove
        )

        for (status, identifier) in responses:
            print(status)

        assoc.release()

    else:
        print("No se pudo establecer la asociacion con el servidor")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=MESSAGE)

    parser.add_argument("--action", required=True, help=action_help)
    parser.add_argument("--path", help="Es la ruta del archivo que se enviara con la accion C_STORE")
    parser.add_argument("--patient", help="El Paciente que se busca en el servidor")
    parser.add_argument("--study_uid", help="")

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
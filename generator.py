import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import CTImageStorage, ExplicitVRLittleEndian, generate_uid
import datetime
import argparse

# Firma
Lab_Raiz = "2.4.100"
proyecto_id = "1"
version = "1.0"

implementation_uid = f"{Lab_Raiz}.{proyecto_id}.{version}"

def create_dummy_dicom(patien_name ,filename, path="Dataset"):
    # Metadatos
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = CTImageStorage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.ImplementationClassUID = implementation_uid # ID de tu lab
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

    # Generar dataset
    ds = FileDataset(filename, {}, file_meta=file_meta, preamble=b"\0" * 128)
    
    # Datos que se usan en C_FIND
    ds.PatientName = patien_name
    ds.PatientID = "ID-001"
    ds.ContentDate = datetime.datetime.now().strftime('%Y%m%d')
    ds.ContentTime = datetime.datetime.now().strftime('%H%M%S')
    
    # Datos que se usan en C_MOVE
    ds.StudyInstanceUID = generate_uid()
    ds.SeriesInstanceUID = generate_uid()
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.SOPClassUID = CTImageStorage
    
    # ubicacion 
    ubicacion=f"{path}/{filename}.dcm"

    # Guardar
    ds.save_as(ubicacion)
    print(f"Archivo creado exitosamente en: {ubicacion}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Script para la creacion de archivos DICOM")

    parser.add_argument("--name", required=True, help="Nombre del archivo DICOM")

    parser.add_argument("--patient",required=True, help="Nombre del Paciente")

    parser.add_argument("--path", required=True, help="Ubicacion donde se guardara el archivo")

    args = parser.parse_args()

    create_dummy_dicom(args.patient, args.name, args.path)


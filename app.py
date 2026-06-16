import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re
import math
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# --- FUNCIONES BASE ---
def sanitize_name(s, max_len=120):
    s = "" if s is None or (isinstance(s, float) and math.isnan(s)) else str(s)
    s = re.sub(r'[\\/:*?"<>|\r\n\t]+', " ", s).strip()
    s = re.sub(r'\s+', " ", s)
    return s[:max_len] if len(s) > max_len else s

def load_corredores(excel_file):
    if not excel_file: return {}
    try:
        raw = pd.read_excel(excel_file, sheet_name=0)
        num_col, name_col = raw.columns[0], raw.columns[1] 
        def clean_num(x):
            if pd.isna(x): return ""
            try: return str(int(float(x)))
            except: return str(x).strip()
        return dict(zip(raw[num_col].apply(clean_num), raw[name_col].astype(str)))
    except Exception as e:
        st.error(f"Error leyendo excel de corredores: {e}")
        return {}

def extract_page_data(layout_text, fulltext):
    clean = re.sub(r"\s+", " ", layout_text or "")
    ref, poliza, org, corredor, certificado, vig_desde = (None,)*6
    
    m = re.search(r"\b(\d{5,8})\s+(\d{4,8})\s+\d+\s+(\d{7})\s+(\d{7})\s+(\d{9,12})", clean)
    if m: ref, poliza, org, corredor, certificado = m.groups()
    
    aseg_m = re.search(r"Sr\./es:\s*(.*?)\s+Cliente", clean, re.I)
    asegurado = aseg_m.group(1).strip() if aseg_m else "SIN_NOMBRE"
    
    m_ramo = re.search(r'\d{2}-0?(\d{3,4})20\d{2}', fulltext)
    ramo = m_ramo.group(1) if m_ramo else "SIN_RAMO"

    return {"referencia": ref, "poliza": poliza, "org": org, "corredor": corredor, "asegurado": asegurado, "ramo": ramo}

def obtener_texto_opcion(opcion, txt_personalizado=""):
    if opcion == "Opción 1: Cláusula 350 Completa":
        return ("A PARTIR DE LA RENOVACIÓN APLICA CLÁUSULA N° 350: EXCLUSION DE RAPIÑA O HURTO TOTAL - SISTEMA DE "
                "RASTREO O LOCALIZACION DE VEHICULOS. Queda entendido y convenido que es requisito para la viabilidad "
                "de esta cobertura...")
    elif opcion == "Opción 2: Unidad con equipo instalado":
        return "CLÁUSULA N° 350: ESTA UNIDAD CUENTA CON SISTEMA DE RASTREO O LOCALIZACION DE VEHICULOS"
    elif opcion == "Opción 3: Texto Personalizado":
        return txt_personalizado
    return ""

# --- INTERFAZ WEB CON STREAMLIT ---
st.set_page_config(page_title="Sancor Seguros - Suite Web", page_icon="🏢", layout="wide")

st.title("Procesador de Pólizas y Flotas (V27 Web)")
st.markdown("Sube tus PDFs, cruza los datos y descarga todo organizado en un archivo ZIP.")

col1, col2 = st.columns(2)

with col1:
    st.header("1. Carga de Archivos")
    uploaded_pdfs = st.file_uploader("Selecciona los PDFs a separar", type=['pdf'], accept_multiple_files=True)
    excel_maestro = st.file_uploader("Excel Corredores (Opcional)", type=['xlsx', 'xls'])
    excel_clausula = st.file_uploader("Excel Opciones Cláusula (Opcional)", type=['xlsx', 'xls'])

with col2:
    st.header("2. Edición (Cláusula 350)")
    opcion_seleccionada = st.radio(
        "¿Qué acción deseas realizar con los PDFs?",
        ("Opción 1: Cláusula 350 Completa", 
         "Opción 2: Unidad con equipo instalado", 
         "Opción 3: Texto Personalizado", 
         "Opción 4: No editar (Solo Separar)")
    )
    
    txt_personalizado = ""
    if opcion_seleccionada == "Opción 3: Texto Personalizado":
        txt_personalizado = st.text_area("Escribe tu texto personalizado aquí:")

# --- LÓGICA DE PROCESAMIENTO ---
if st.button("PROCESAR ARCHIVOS", type="primary"):
    if not uploaded_pdfs:
        st.warning("⚠️ Por favor, sube al menos un archivo PDF para procesar.")
    else:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_dir = temp_path / "inputs"
            output_dir = temp_path / "outputs"
            input_dir.mkdir()
            output_dir.mkdir()

            map_corredores = load_corredores(excel_maestro)

            progress_text = "Procesando documentos. Por favor espera..."
            my_bar = st.progress(0, text=progress_text)
            
            pdf_paths = []
            for pdf_file in uploaded_pdfs:
                path = input_dir / pdf_file.name
                with open(path, "wb") as f:
                    f.write(pdf_file.getbuffer())
                pdf_paths.append(path)

            records = []
            total_pdfs = len(pdf_paths)
            
            for i, pdf_path in enumerate(pdf_paths):
                progreso = (i + 1) / total_pdfs
                my_bar.progress(progreso, text=f"Procesando: {pdf_path.name}")
                
                try:
                    with fitz.open(pdf_path) as doc:
                        for page_idx in range(len(doc)):
                            page = doc[page_idx]
                            text = page.get_text("text")
                            data = extract_page_data(text, text)
                            
                            ramo = data["ramo"] or "SIN_RAMO"
                            org = data["org"] or "ORG"
                            corredor = data["corredor"] or "CORREDOR"
                            
                            folder = output_dir / sanitize_name(f"Ramo {ramo}") / sanitize_name(f"ORG {org}") / sanitize_name(f"Corredor {corredor}")
                            folder.mkdir(parents=True, exist_ok=True)
                            
                            out_pdf_path = folder / f"REF {data['referencia']}_Pagina_{page_idx}.pdf"
                            
                            new_doc = fitz.open()
                            new_doc.insert_pdf(doc, from_page=page_idx, to_page=page_idx)
                            
                            if opcion_seleccionada != "Opción 4: No editar (Solo Separar)":
                                page_new = new_doc[0]
                                page_new.insert_text((50, 150), obtener_texto_opcion(opcion_seleccionada, txt_personalizado), fontsize=8, color=(1,0,0))
                                
                            new_doc.save(out_pdf_path)
                            new_doc.close()
                            
                            records.append({"Archivo Original": pdf_path.name, "Referencia": data["referencia"], "Estado": "Procesado"})
                except Exception as e:
                    st.error(f"Error en {pdf_path.name}: {e}")

            if records:
                df = pd.DataFrame(records)
                df.to_excel(output_dir / "Resumen_Proceso.xlsx", index=False)

            my_bar.progress(1.0, text="¡Procesamiento completo! Comprimiendo archivos...")

            zip_path = temp_path / "Archivos_Procesados"
            shutil.make_archive(zip_path, 'zip', output_dir)

            st.success("✅ ¡Todo listo! Ya puedes descargar tus archivos.")

            with open(f"{zip_path}.zip", "rb") as f:
                st.download_button(
                    label="📥 DESCARGAR ARCHIVOS ZIP",
                    data=f,
                    file_name=f"Sancor_Procesados_{datetime.now().strftime('%d%m%Y_%H%M')}.zip",
                    mime="application/zip",
                    type="primary"
                )
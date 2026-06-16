# 📋 Sancor Seguros - Procesador de Pólizas y Flotas

Suite web para procesar, separar y editar pólizas de seguros en PDF. Desarrollado con **Streamlit**.

## 🚀 Características

- ✅ Carga múltiples PDFs
- ✅ Extrae datos de pólizas (referencia, número, organización, corredor)
- ✅ Inserta cláusula 350 personalizable
- ✅ Organiza archivos por Ramo/Organización/Corredor
- ✅ Descarga todo en ZIP

## 📦 Requisitos

- Python 3.8+
- streamlit
- PyMuPDF
- pandas
- openpyxl

## 🔧 Instalación Local

```bash
pip install -r requirements.txt
```

## ▶️ Ejecutar Localmente

```bash
streamlit run app.py
```

Accede a: http://localhost:8502

## 🌐 Desplegar en Streamlit Cloud

1. Sube este repositorio a GitHub
2. Accede a [streamlit.io/cloud](https://share.streamlit.io)
3. Conecta tu cuenta GitHub
4. Selecciona este repositorio
5. ¡Listo! Tu app estará en línea automáticamente

## 📋 Archivos Principales

- **app.py** - Aplicación principal Streamlit
- **requirements.txt** - Dependencias Python
- **.streamlit/config.toml** - Configuración de Streamlit

## 📝 Uso

1. Sube los PDFs de pólizas
2. (Opcional) Carga Excel de corredores
3. Selecciona opción de cláusula 350
4. Haz clic en "PROCESAR ARCHIVOS"
5. Descarga el ZIP generado

---

**Desarrollado por:** Sancor Seguros

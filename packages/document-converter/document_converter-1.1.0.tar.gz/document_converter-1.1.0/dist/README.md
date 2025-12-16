# Document Converter v1.1.0 - Standalone Executable

Este ejecutable incluye **dos modos de uso**: modo interactivo y modo línea de comandos.

## 🎯 Modo Interactivo (Recomendado para usuarios)

### Uso
**Haz doble click** en `document-converter.exe`

El programa mostrará un menú interactivo:

```
======================================================================
                    DOCUMENT CONVERTER v1.1.0
======================================================================

Selecciona una opción:

  1. Convertir un archivo
  2. Batch - Convertir carpeta completa
  3. Ver información de archivo
  4. Ver estadísticas de caché
  5. Limpiar caché
  0. Salir
```

### Características
✅ **Fácil de usar** - Sin necesidad de conocimientos técnicos
✅ **Validación automática** - Verifica que los archivos existan
✅ **Mensajes claros** - En español, fáciles de entender
✅ **Progreso visible** - Muestra el avance de las conversiones
✅ **Manejo de errores** - Explicaciones claras si algo falla

---

## 💻 Modo Línea de Comandos (Para usuarios avanzados)

### Uso
Abre **CMD** o **PowerShell** en esta carpeta y ejecuta:

```bash
# Ver ayuda
document-converter.exe --help

# Convertir un archivo
document-converter.exe convert input.pdf output.txt

# Batch processing
document-converter.exe batch ./documentos ./salida --from-format docx --to-format pdf

# Ver información de archivo
document-converter.exe info documento.pdf

# Cache statistics
document-converter.exe cache-stats

# Limpiar cache
document-converter.exe cache-clear
```

### Comandos Disponibles

#### 1. `convert` - Convertir archivo individual
```bash
document-converter.exe convert entrada.pdf salida.txt
document-converter.exe convert documento.docx documento.html
```

#### 2. `batch` - Convertir carpeta completa
```bash
# Convertir todos los DOCX de una carpeta a PDF
document-converter.exe batch ./docs ./output --from-format docx --to-format pdf

# Con más workers para mayor velocidad
document-converter.exe batch ./docs ./output --from-format txt --workers 8

# Recursivo (incluir subcarpetas)
document-converter.exe batch ./docs ./output --from-format md --recursive
```

#### 3. `info` - Información de archivo
```bash
document-converter.exe info documento.pdf
```

#### 4. `cache-stats` - Estadísticas de caché
```bash
document-converter.exe cache-stats
```

#### 5. `cache-clear` - Limpiar caché
```bash
document-converter.exe cache-clear
```

---

## 📋 Formatos Soportados

### Conversiones Disponibles

- **PDF** → TXT, DOCX (con OCR para PDFs escaneados)
- **DOCX** → PDF, HTML, Markdown, TXT
- **TXT** → HTML, PDF
- **Markdown (.md)** → HTML, PDF
- **HTML** → PDF, DOCX
- **ODT** → Múltiples formatos

---

## ⚡ Características

### Sistema de Caché Inteligente
- **Conversiones instantáneas** para archivos ya procesados
- **Dos niveles**: memoria (ultrarrápido) + disco (persistente)
- **Hasta 138x más rápido** con caché activo

### Procesamiento Paralelo
- **Múltiples workers** para procesar varios archivos simultáneamente
- **50-200 archivos/segundo** (dependiendo del tamaño)
- Perfecto para conversiones masivas

### Plantillas Personalizables
- Motor de plantillas integrado
- Variables, loops, condicionales
- Ideal para generar reportes

---

## 📦 Requisitos del Sistema

✅ **Windows 10 o superior**
✅ **Sin dependencias** - Todo incluido en el .exe
✅ **~11 MB** de espacio en disco
✅ **No requiere Python instalado**

---

## 🚀 Ejemplos de Uso

### Ejemplo 1: Convertir PDF a TXT
**Modo Interactivo:**
1. Doble click en el .exe
2. Selecciona opción `1`
3. Ingresa ruta del PDF
4. Ingresa ruta de salida .txt
5. ¡Listo!

**Modo comando:**
```bash
document-converter.exe convert factura.pdf factura.txt
```

### Ejemplo 2: Convertir carpeta de DOCX a PDF
**Modo Interactivo:**
1. Doble click en el .exe
2. Selecciona opción `2`
3. Ingresa carpeta de documentos DOCX
4. Ingresa carpeta de salida
5. Formato origen: `docx`
6. Formato destino: `pdf`
7. Workers: `4` (o más para mayor velocidad)

**Modo comando:**
```bash
document-converter.exe batch ./documentos ./pdfs --from-format docx --to-format pdf --workers 8
```

### Ejemplo 3: Ver información de archivo
```bash
document-converter.exe info importante.docx
```

Mostrará:
- Tamaño del archivo
- Formato detectado
- Ruta absoluta
- Más información

---

## 💡 Consejos

### Para Mejor Rendimiento
1. **Usa caché**: Las conversiones repetidas son instantáneas
2. **Más workers**: Para carpetas grandes, usa 8-16 workers
3. **Formato correcto**: Especifica el formato para evitar detección automática

### Resolución de Problemas

**El ejecutable se abre y cierra inmediatamente**
- ✅ Esto es normal cuando se hace doble click
- ✅ El menú interactivo debería mostrarse
- ❌ Si no aparece, ejecuta desde CMD para ver errores

**"No se puede convertir archivo"**
- Verifica que el archivo existe
- Comprueba que el formato es soportado
- Revisa que tienes permisos de lectura/escritura

**Conversión muy lenta**
- Primera vez siempre es más lenta (sin caché)
- PDFs grandes con OCR pueden tardar
- Aumenta el número de workers para batch

---

## 📞 Soporte

- **Repositorio**: [github.com/MikeAMSDev/document-converter](https://github.com/MikeAMSDev/document-converter)
- **Problemas**: Abre un issue en GitHub
- **Changelog**: Ver CHANGELOG.md
- **Release Notes**: Ver RELEASE_NOTES.md

---

## 📄 Licencia

MIT License - Ver archivo LICENSE para detalles

---

**Versión**: 1.1.0  
**Fecha**: Diciembre 2024  
**Construido con**: Python 3.13 + PyInstaller

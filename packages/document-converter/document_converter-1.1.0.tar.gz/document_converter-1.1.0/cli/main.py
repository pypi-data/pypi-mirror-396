"""
Document Converter CLI - Main Entry Point

Provides both command-line interface and interactive mode.
"""
import click
import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# CLI Mode (Click commands)
# ============================================================================

@click.group()
@click.version_option(version='1.1.0')
def cli():
    """Document Converter CLI tool."""
    pass

# Import and register commands
from cli.commands.convert import convert_command
from cli.commands.batch import batch_command
from cli.commands.info import info_command
from cli.commands.cache import cache_clear_command, cache_stats_command

cli.add_command(convert_command)
cli.add_command(batch_command)
cli.add_command(info_command)
cli.add_command(cache_clear_command)
cli.add_command(cache_stats_command)

# ============================================================================
# Interactive Mode (Menu-driven)
# ============================================================================

def clear_screen():
    """Clear console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_header():
    """Display application header."""
    print("=" * 70)
    print(" " * 20 + "DOCUMENT CONVERTER v1.1.0")
    print("=" * 70)
    print()

def show_main_menu():
    """Display main menu options."""
    print("Selecciona una opción:")
    print()
    print("  1. Convertir un archivo")
    print("  2. Batch - Convertir carpeta completa")
    print("  3. Ver información de archivo")
    print("  4. Ver estadísticas de caché")
    print("  5. Limpiar caché")
    print("  0. Salir")
    print()

def wait_for_enter():
    """Wait for user to press Enter."""
    input("\nPresiona Enter para continuar...")

def convertir_archivo_interactivo():
    """Interactive file conversion."""
    clear_screen()
    show_header()
    print("CONVERTIR ARCHIVO")
    print("-" * 70)
    print()
    
    # Show supported conversions
    print("Conversiones soportadas:")
    print("  PDF    → TXT, DOCX (con OCR para PDFs escaneados)")
    print("  DOCX   → PDF, HTML, Markdown, TXT")
    print("  TXT    → HTML, PDF")
    print("  MD     → HTML, PDF")
    print("  HTML   → PDF, DOCX")
    print("  ODT    → PDF, DOCX, HTML, TXT")
    print()
    print("-" * 70)
    print()
    
    # Get input file
    while True:
        print("Archivo de entrada:")
        input_path = input("  » ").strip()
        
        if not input_path:
            print("❌ Debes especificar un archivo")
            continue
            
        if input_path.lower() == 'cancelar':
            return
            
        if not os.path.exists(input_path):
            print(f"❌ El archivo '{input_path}' no existe")
            retry = input("¿Intentar de nuevo? (s/n): ").lower()
            if retry != 's':
                return
            continue
            
        if not os.path.isfile(input_path):
            print(f"❌ '{input_path}' no es un archivo válido")
            continue
            
        break
    
    # Get output file
    print()
    print("Archivo de salida:")
    output_path = input("  » ").strip()
    
    if not output_path:
        print("❌ Debes especificar un archivo de salida")
        wait_for_enter()
        return
    
    # Show tip
    print()
    print("💡 Tip: La extensión del archivo de salida determina el formato")
    print("   Ejemplo: 'salida.pdf' convierte a PDF, 'salida.html' a HTML")
    print()
    
    # Perform conversion
    print("🔄 Convirtiendo...")
    print()
    
    try:
        # Import here to avoid circular imports
        from converter.engine import ConversionEngine
        from converter.formats.txt_converter import TXTConverter
        from converter.formats.markdown_converter import MarkdownConverter
        from converter.formats.html_converter import HTMLConverter
        from converter.formats.pdf_converter import PDFConverter
        from converter.formats.docx_converter import DOCXConverter
        
        engine = ConversionEngine()
        engine.register_converter('txt', TXTConverter)
        engine.register_converter('md', MarkdownConverter)
        engine.register_converter('html', HTMLConverter)
        engine.register_converter('pdf', PDFConverter)
        engine.register_converter('docx', DOCXConverter)
        
        success = engine.convert(input_path, output_path)
        
        print()
        if success:
            print("✅ ¡Conversión exitosa!")
            print(f"📄 Archivo guardado: {os.path.abspath(output_path)}")
        else:
            print("❌ La conversión falló")
            
    except Exception as e:
        print()
        print(f"❌ Error durante la conversión:")
        print(f"   {str(e)}")
    
    wait_for_enter()

def batch_interactivo():
    """Interactive batch processing."""
    clear_screen()
    show_header()
    print("BATCH - CONVERTIR CARPETA COMPLETA")
    print("-" * 70)
    print()
    
    # Get input directory
    while True:
        print("Carpeta de entrada:")
        input_dir = input("  » ").strip()
        
        if not input_dir:
            print("❌ Debes especificar una carpeta")
            continue
            
        if input_dir.lower() == 'cancelar':
            return
            
        if not os.path.exists(input_dir):
            print(f"❌ La carpeta '{input_dir}' no existe")
            retry = input("¿Intentar de nuevo? (s/n): ").lower()
            if retry != 's':
                return
            continue
            
        if not os.path.isdir(input_dir):
            print(f"❌ '{input_dir}' no es una carpeta válida")
            continue
            
        break
    
    # Get output directory
    print()
    print("Carpeta de salida:")
    output_dir = input("  » ").strip()
    
    if not output_dir:
        print("❌ Debes especificar una carpeta de salida")
        wait_for_enter()
        return
    
    # Get format to convert from
    print()
    print("Formato origen (txt, docx, pdf, html, md):")
    from_format = input("  » ").strip().lower()
    
    if not from_format:
        from_format = 'txt'
        print(f"  Usando formato por defecto: {from_format}")
    
    # Get format to convert to
    print()
    print("Formato destino (txt, docx, pdf, html, md):")
    to_format = input("  » ").strip().lower()
    
    if not to_format:
        to_format = 'pdf'
        print(f"  Usando formato por defecto: {to_format}")
    
    # Ask for worker count
    print()
    print("Número de workers paralelos (1-16, default=4):")
    workers_input = input("  » ").strip()
    
    try:
        max_workers = int(workers_input) if workers_input else 4
        max_workers = max(1, min(16, max_workers))
    except ValueError:
        max_workers = 4
    
    print(f"  Usando {max_workers} workers")
    
    # Perform batch conversion
    print()
    print("🔄 Escaneando archivos...")
    print()
    
    try:
        from converter.batch_processor import BatchProcessor
        from converter.formats.txt_converter import TXTConverter
        from converter.formats.markdown_converter import MarkdownConverter
        from converter.formats.html_converter import HTMLConverter
        
        processor = BatchProcessor(max_workers=max_workers)
        processor.engine.register_converter('txt', TXTConverter)
        processor.engine.register_converter('md', MarkdownConverter)
        processor.engine.register_converter('html', HTMLConverter)
        
        count = processor.scan_directory(
            input_dir=input_dir,
            output_dir=output_dir,
            from_format=from_format,
            to_format=to_format
        )
        
        print(f"📁 Encontrados {count} archivos para convertir")
        
        if count == 0:
            print("⚠️  No se encontraron archivos para procesar")
            wait_for_enter()
            return
        
        print()
        confirm = input("¿Continuar con la conversión? (s/n): ").lower()
        if confirm != 's':
            print("Operación cancelada")
            wait_for_enter()
            return
        
        print()
        print("🔄 Procesando archivos...")
        
        # Simple progress counter
        progress = [0]
        def show_progress():
            progress[0] += 1
            print(f"  Procesado {progress[0]}/{count} archivos", end='\r')
        
        report = processor.process_queue(progress_callback=show_progress)
        
        print()
        print()
        print("✅ Proceso completado")
        print(f"   Total: {report.total}")
        print(f"   Exitosos: {report.success}")
        print(f"   Fallidos: {report.failed}")
        
    except Exception as e:
        print()
        print(f"❌ Error durante el procesamiento:")
        print(f"   {str(e)}")
    
    wait_for_enter()

def info_interactivo():
    """Interactive file info display."""
    clear_screen()
    show_header()
    print("VER INFORMACIÓN DE ARCHIVO")
    print("-" * 70)
    print()
    
    while True:
        print("Archivo a inspeccionar:")
        file_path = input("  » ").strip()
        
        if not file_path:
            print("❌ Debes especificar un archivo")
            continue
            
        if file_path.lower() == 'cancelar':
            return
            
        if not os.path.exists(file_path):
            print(f"❌ El archivo '{file_path}' no existe")
            retry = input("¿Intentar de nuevo? (s/n): ").lower()
            if retry != 's':
                return
            continue
            
        break
    
    print()
    print("📄 Información del archivo:")
    print("-" * 70)
    
    try:
        # Basic file info
        file_size = os.path.getsize(file_path)
        file_ext = os.path.splitext(file_path)[1]
        
        print(f"Nombre: {os.path.basename(file_path)}")
        print(f"Ruta: {os.path.abspath(file_path)}")
        print(f"Tamaño: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
        print(f"Extensión: {file_ext}")
        
        # Try to detect format
        from converter.base.format_detector import FormatDetector
        detector = FormatDetector()
        detected = detector.detect(file_path)
        
        if detected:
            print(f"Formato detectado: {detected.upper()}")
        
    except Exception as e:
        print(f"❌ Error al leer información: {str(e)}")
    
    wait_for_enter()

def mostrar_cache_stats():
    """Display cache statistics."""
    clear_screen()
    show_header()
    print("ESTADÍSTICAS DE CACHÉ")
    print("-" * 70)
    print()
    
    try:
        from core.cache_manager import CacheManager
        
        cache = CacheManager()
        stats = cache.get_stats()
        
        print(f"📊 Elementos en caché: {stats['items']}")
        print(f"💾 Tamaño total: {stats['total_size_bytes']:,} bytes")
        print(f"    ({stats['total_size_bytes'] / 1024 / 1024:.2f} MB)")
        
        if stats['items'] > 0:
            avg_size = stats['total_size_bytes'] / stats['items']
            print(f"📏 Tamaño promedio: {avg_size:,.0f} bytes")
        
    except Exception as e:
        print(f"❌ Error al obtener estadísticas: {str(e)}")
    
    wait_for_enter()

def limpiar_cache():
    """Clear all cache."""
    clear_screen()
    show_header()
    print("LIMPIAR CACHÉ")
    print("-" * 70)
    print()
    
    print("⚠️  Esto eliminará todos los archivos en caché.")
    confirm = input("¿Estás seguro? (s/n): ").lower()
    
    if confirm != 's':
        print("Operación cancelada")
        wait_for_enter()
        return
    
    try:
        from core.cache_manager import CacheManager
        
        cache = CacheManager()
        cache.clear()
        
        print()
        print("✅ Caché limpiado exitosamente")
        
    except Exception as e:
        print()
        print(f"❌ Error al limpiar caché: {str(e)}")
    
    wait_for_enter()

def interactive_mode():
    """Main interactive mode loop."""
    while True:
        clear_screen()
        show_header()
        show_main_menu()
        
        opcion = input("Opción: ").strip()
        
        if opcion == '1':
            convertir_archivo_interactivo()
        elif opcion == '2':
            batch_interactivo()
        elif opcion == '3':
            info_interactivo()
        elif opcion == '4':
            mostrar_cache_stats()
        elif opcion == '5':
            limpiar_cache()
        elif opcion == '0':
            clear_screen()
            print()
            print("¡Gracias por usar Document Converter!")
            print()
            break
        else:
            print()
            print("❌ Opción no válida. Por favor selecciona 0-5.")
            wait_for_enter()

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    # Detect if running with arguments (CLI mode) or without (interactive mode)
    if len(sys.argv) == 1:
        # No arguments = Interactive mode
        try:
            interactive_mode()
        except KeyboardInterrupt:
            print("\n\nInterrumpido por el usuario")
            sys.exit(0)
    else:
        # With arguments = CLI mode
        cli()

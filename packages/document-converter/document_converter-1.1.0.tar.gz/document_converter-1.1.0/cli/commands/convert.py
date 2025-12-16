import click
import os
import sys
import logging
import json
from converter.engine import ConversionEngine
from converter.template_engine import TemplateEngine

logger = logging.getLogger(__name__)

@click.command('convert')
@click.argument('input_path', type=click.Path(exists=True))
@click.argument('output_path', type=click.Path())
@click.option('--format', '-f', help='Target format (if different from extension)')
@click.option('--template', '-t', help='Path to template file for custom output')
@click.option('--ocr/--no-ocr', default=False, help='Enable OCR for scanned documents')
@click.option('--lang', default='auto', help='Language for OCR (default: auto)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def convert_command(input_path, output_path, format, template, ocr, lang, verbose):
    """Convert a single document."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    click.echo(f"Converting '{input_path}' to '{output_path}'...")
    
    try:
        # Template mode
        if template:
            if not os.path.exists(template):
                click.echo(click.style(f"Error: Template file not found: {template}", fg='red'))
                sys.exit(1)
                
            click.echo(f"Using template: {template}")
            
            # For template mode, input is treated as data context
            # Currently supporting JSON inputs
            # TODO: Support YAML or other data sources?
            # Also TODO: Support document-to-document with template styling if Engine supports it? 
            # For now, implementing Data(JSON) + Template -> Output
            
            try:
                with open(input_path, 'r', encoding='utf-8') as f:
                    # Basic detection: try JSON
                    context = json.load(f)
            except json.JSONDecodeError:
                click.echo(click.style("Error: Input file must be valid JSON when using templates.", fg='red'))
                sys.exit(1)
            except Exception as e:
                click.echo(click.style(f"Error reading input: {e}", fg='red'))
                sys.exit(1)
                
            engine = TemplateEngine()
            
            with open(template, 'r', encoding='utf-8') as f:
                tmpl_content = f.read()
                
            result = engine.render(tmpl_content, context)
            
            # Ensure output dir
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result)
                
            click.echo(click.style("Template rendered successfully!", fg='green'))
            return

        # Standard conversion mode
        # Initialize engine
        engine = ConversionEngine()
        
        success = engine.convert(
            input_path, 
            output_path, 
            ocr_enabled=ocr, 
            ocr_lang=lang
        )
        
        if success:
            click.echo(click.style("Conversion successful!", fg='green'))
        else:
            click.echo(click.style("Conversion failed.", fg='red'))
            sys.exit(1)
            
    except ImportError as e:
        click.echo(click.style(f"Error: Missing dependency. {e}", fg='red'))
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg='red'))
        if verbose:
            logger.exception("Conversion error")
        sys.exit(1)

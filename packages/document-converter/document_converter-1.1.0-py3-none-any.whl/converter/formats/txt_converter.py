import os
import chardet
from typing import Dict, Any, Optional
from converter.base.converter_base import BaseConverter

class TXTConverter(BaseConverter):
    """
    Converter for plain text files.
    Handles encoding detection and basic text processing.
    """

    def convert(self, input_path: str, output_path: str, **kwargs) -> bool:
        """
        Convert a text file to another text file (potentially changing encoding or just copying).
        For now, it reads with detected encoding and writes as UTF-8.
        
        Args:
            input_path: Path to the input file.
            output_path: Path to the output file.
            **kwargs: Additional arguments (e.g., 'encoding' to force output encoding).
            
        Returns:
            True if successful, False otherwise.
        """
        if not self.validate_input(input_path):
            return False

        self._ensure_output_directory(output_path)

        try:
            # Detect encoding
            encoding = self._detect_encoding(input_path)
            
            # Read content
            with open(input_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # Write content (default to utf-8)
            output_encoding = kwargs.get('encoding', 'utf-8')
            with open(output_path, 'w', encoding=output_encoding) as f:
                f.write(content)
                
            return True
        except Exception as e:
            print(f"Error converting TXT: {e}")
            return False

    def validate_input(self, input_path: str) -> bool:
        """
        Validate if the input file is a valid text file.
        """
        if not os.path.exists(input_path):
            return False
            
        # Simple check: try to read a bit with chardet or just check extension
        # For robustness, we could check if it's binary, but for now let's rely on extension/existence
        # and maybe a quick read attempt.
        return True

    def extract_metadata(self, input_path: str) -> Dict[str, Any]:
        """
        Extract metadata from text file (lines, words, encoding).
        """
        if not os.path.exists(input_path):
            return {}

        try:
            encoding = self._detect_encoding(input_path)
            with open(input_path, 'r', encoding=encoding) as f:
                content = f.read()
                
            return {
                "encoding": encoding,
                "lines": len(content.splitlines()),
                "words": len(content.split()),
                "characters": len(content)
            }
        except Exception:
            return {}

    def _detect_encoding(self, file_path: str) -> str:
        """
        Detect file encoding using chardet.
        """
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000) # Read first 10KB
        
        result = chardet.detect(raw_data)
        return result['encoding'] or 'utf-8'

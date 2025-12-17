"""File compilation utilities for importing various file types to TapeFile format."""

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from supertape.core.file.api import TapeFile


@dataclass
class FileCompilationResult:
    """Result of file compilation attempt."""

    success: bool
    tape_file: Optional["TapeFile"] = None  # TapeFile object if successful
    error_message: Optional[str] = None


class FileCompiler:
    """Handles compilation of various file types to TapeFile format."""

    SUPPORTED_EXTENSIONS = {".k7", ".bas", ".asm", ".c"}

    @staticmethod
    def is_supported_file(filename: str) -> bool:
        """Check if file extension is supported.

        Args:
            filename: Path to file

        Returns:
            True if file extension is supported
        """
        ext = Path(filename).suffix.lower()
        return ext in FileCompiler.SUPPORTED_EXTENSIONS

    @staticmethod
    def compile_k7_file(filename: str) -> FileCompilationResult:
        """Load native .k7 file.

        Args:
            filename: Path to .k7 file

        Returns:
            FileCompilationResult with loaded TapeFile or error
        """
        try:
            from supertape.core.file.load import file_load

            tape = file_load(filename)
            return FileCompilationResult(success=True, tape_file=tape)
        except ImportError as e:
            return FileCompilationResult(
                success=False,
                error_message=f"Supertape library not available: {e}",
            )
        except FileNotFoundError:
            return FileCompilationResult(
                success=False,
                error_message=f"File not found: {filename}",
            )
        except Exception as e:
            return FileCompilationResult(
                success=False,
                error_message=f"Failed to load .k7 file: {e}",
            )

    @staticmethod
    def compile_basic_file(filename: str) -> FileCompilationResult:
        """Compile .bas file to BASIC TapeFile (type 0x00).

        Args:
            filename: Path to .bas file

        Returns:
            FileCompilationResult with compiled TapeFile or error
        """
        try:
            from supertape.core.basic.encode import BasicEncoder, BasicFileCompiler
            from supertape.core.basic.minification import minify_basic
            from supertape.core.basic.preprocess import preprocess_basic

            # Read BASIC source
            with open(filename) as f:
                basic_code = f.read()

            # Preprocess and minify
            basic_code = preprocess_basic(basic_code)
            basic_code = minify_basic(basic_code)

            # Encode to binary instructions
            encoder = BasicEncoder()
            instructions = [encoder.encode(line) for line in basic_code.splitlines()]

            # Compile to TapeFile
            compiler = BasicFileCompiler()
            tape = compiler.compile_instructions(filename, instructions)

            return FileCompilationResult(success=True, tape_file=tape)
        except ImportError as e:
            return FileCompilationResult(
                success=False,
                error_message=f"Supertape library not available: {e}",
            )
        except FileNotFoundError:
            return FileCompilationResult(
                success=False,
                error_message=f"File not found: {filename}",
            )
        except Exception as e:
            return FileCompilationResult(
                success=False,
                error_message=f"BASIC compilation error: {e}",
            )

    @staticmethod
    def compile_assembly_file(filename: str, as_machine: bool) -> FileCompilationResult:
        """Compile .asm file to either MACHINE (0x02) or ASMSRC (0x05).

        Args:
            filename: Path to .asm file
            as_machine: If True, assemble to MACHINE code, else store as ASMSRC text

        Returns:
            FileCompilationResult with compiled TapeFile or error
        """
        try:
            # Read assembly source
            with open(filename) as f:
                asm_code = f.read()

            if as_machine:
                # Compile to MACHINE code (executable)
                from supertape.core.asm.assembler import M6803Assembler
                from supertape.core.asm.encoder import create_machine_file

                assembler = M6803Assembler()
                machine_code, load_addr, exec_addr = assembler.assemble(asm_code)
                tape = create_machine_file(filename, machine_code, load_addr, exec_addr)
            else:
                # Store as ASMSRC (text)
                from supertape.core.assembly.encode import create_assembly_file

                tape = create_assembly_file(filename, asm_code)

            return FileCompilationResult(success=True, tape_file=tape)
        except ImportError as e:
            return FileCompilationResult(
                success=False,
                error_message=f"Supertape library not available: {e}",
            )
        except FileNotFoundError:
            return FileCompilationResult(
                success=False,
                error_message=f"File not found: {filename}",
            )
        except Exception as e:
            return FileCompilationResult(
                success=False,
                error_message=f"Assembly error: {e}",
            )

    @staticmethod
    def compile_c_file(filename: str) -> FileCompilationResult:
        """Compile .c file to MACHINE TapeFile (type 0x02).

        Args:
            filename: Path to .c file

        Returns:
            FileCompilationResult with compiled TapeFile or error
        """
        try:
            from supertape.core.asm.assembler import M6803Assembler
            from supertape.core.asm.encoder import create_machine_file
            from supertape.core.c.compiler import compile_c_to_assembly
            from supertape.core.c.errors import CCompilerError, FCCNotFoundError

            # Compile C to assembly
            c_path = Path(filename)
            asm_path = c_path.with_suffix(".asm")

            try:
                compile_c_to_assembly(c_path, asm_path, cpu="6803")
            except FCCNotFoundError:
                return FileCompilationResult(
                    success=False,
                    error_message=(
                        "The FCC compiler is required to compile C files but was not found.\n\n"
                        "Please install FCC from:\n"
                        "https://github.com/EtchedPixels/Fuzix-Compiler-Kit\n\n"
                        "Or ensure 'fcc' is in your system PATH."
                    ),
                )
            except CCompilerError as e:
                return FileCompilationResult(
                    success=False,
                    error_message=f"C compilation failed:\n\n{e}",
                )

            # Read generated assembly
            with open(asm_path) as f:
                asm_code = f.read()

            # Assemble to machine code
            assembler = M6803Assembler()
            machine_code, load_addr, exec_addr = assembler.assemble(asm_code)
            tape = create_machine_file(str(c_path), machine_code, load_addr, exec_addr)

            return FileCompilationResult(success=True, tape_file=tape)
        except ImportError as e:
            return FileCompilationResult(
                success=False,
                error_message=f"Supertape library not available: {e}",
            )
        except FileNotFoundError:
            return FileCompilationResult(
                success=False,
                error_message=f"File not found: {filename}",
            )
        except Exception as e:
            return FileCompilationResult(
                success=False,
                error_message=f"Compilation error: {e}",
            )

    @staticmethod
    def compile_file(filename: str, asm_as_machine: bool = False) -> FileCompilationResult:
        """Compile a file to TapeFile format based on extension.

        Args:
            filename: Path to file
            asm_as_machine: For .asm files, if True compile to MACHINE, else ASMSRC

        Returns:
            FileCompilationResult with compiled TapeFile or error
        """
        ext = Path(filename).suffix.lower()

        if ext == ".k7":
            return FileCompiler.compile_k7_file(filename)
        elif ext == ".bas":
            return FileCompiler.compile_basic_file(filename)
        elif ext == ".asm":
            return FileCompiler.compile_assembly_file(filename, asm_as_machine)
        elif ext == ".c":
            return FileCompiler.compile_c_file(filename)
        else:
            return FileCompilationResult(
                success=False,
                error_message=f"Unsupported file type: {ext}",
            )

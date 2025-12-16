# -*- coding: utf-8 -*-
import subprocess


def render_notebook_to_pdf(
        working_directory: str,
        file_directory: str,
        notebook_file_name: str,
) -> bool:
    """
    Renders a notebook to PDF using Quarto.

    Args:
        working_directory (str): Directory from which the command is executed
        file_directory (str): Directory where the file is located.
        notebook_file_name (str): Name of the notebook file to render.

    Returns:
        bool: True if PDF generation was successful, False otherwise.
    """
    # Build Quarto command with options
    quarto_cmd = ["quarto", "render", f"files/clean/{notebook_file_name}", "--to", "pdf"]

    # Render the notebook to PDF using Quarto from (CWD) the reports directory
    try:
        subprocess.run(
            quarto_cmd,
            cwd=working_directory,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Quarto render failed: {e}")
        raise


def render_dagstermill_notebook_to_pdf(
        working_directory: str,
        executed_notebook_file_name: str,
        file_directory: str,
) -> bool:
    """
    Renders a Dagstermill-executed notebook to PDF using Quarto.

    Args:
        working_directory (str): Directory from which the command is executed
        executed_notebook_file_name (str): Name of the executed notebook file to render.
        file_directory (str): Directory where the file is located.

    Returns:
        bool: True if PDF generation was successful, False otherwise.
    """
    return render_notebook_to_pdf(
        working_directory=working_directory,
        notebook_file_name=executed_notebook_file_name,
        file_directory=file_directory,
    )

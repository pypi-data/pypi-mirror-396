from pathlib import Path
# from os import getcwd
from os import chdir, getcwd

def get_root_path(
    max_folder_depth: int = 7,
    project_markers: list[str] = [
        "requirements.txt",
        "readme.md",
        "dockerfile",
        ".gitignore",
        ".env",
        ".git",
        ".github",
        "setup.py",
        "pyproject.toml",
    ],
    ) -> Path:
    """Attempts to find the root of a project by traversing the directory tree upwards.

    Args:
        max_folder_depth (int, optional): The maximum number of folders to traverse before giving up. Defaults to 7.
        project_markers (list[str], optional): A list of file or folder names that are commonly found in the root of a project. Defaults to a list of common GitHub repository files.

    Returns:
        Path: The path to the project root.
    """

    # Common project markers that indicate the root directory
    project_markers = [marker.lower() for marker in project_markers]
 
    if __name__ == '__main__':
        current_path = Path(__file__).parent
    else:
        current_path = Path(getcwd())
    
    # Look for project markers in current and parent directories
    original_path = current_path
    
    for _ in range(max_folder_depth):
        # Check if any project marker exists in current directory
        if any((current_path / marker.lower()).exists() for marker in project_markers):
            chdir(current_path)
            return current_path
            
        parent = current_path.parent
        if parent == current_path:  # Reached filesystem root
            break
        current_path = parent
    
    # If no project root found, fall back to the original directory
    chdir(original_path)
    return original_path


package_path = Path(__file__).parent
project_path = get_root_path()

logpath  = project_path /'icclogs'
logpath.mkdir(parents=True,exist_ok=True)
logfile  = logpath / 'error_logs.txt'

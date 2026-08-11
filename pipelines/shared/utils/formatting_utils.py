

def format_size(size_bytes: int) -> str:
    
    for unit in ("B", "KB", "MB", "GB"):
        
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        
        size_bytes /= 1024
        
    return f"{size_bytes:.2f} TB"
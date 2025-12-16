import difflib
import jsbeautifier

def create_beautified_diff(old_code: str, new_code: str, filename: str) -> str:
    """Creates a diff between two formatted versions of code."""
    opts = jsbeautifier.default_options()
    opts.indent_size = 2
    try: beautified_old = jsbeautifier.beautify(old_code, opts)
    except: beautified_old = old_code
    try: beautified_new = jsbeautifier.beautify(new_code, opts)
    except: beautified_new = new_code
    diff_lines = difflib.unified_diff(
        beautified_old.splitlines(keepends=True),
        beautified_new.splitlines(keepends=True),
        fromfile=f'a/{filename}',
        tofile=f'b/{filename}',
    )
    return ''.join(diff_lines)

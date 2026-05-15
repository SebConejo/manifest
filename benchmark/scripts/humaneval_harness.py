"""Production-grade HumanEval pass@1 harness for TaskBench code generation validation."""
import json, glob, os, subprocess, tempfile, re, textwrap
import sys

TYPING_IMPORTS = {
    'List': 'from typing import List',
    'Dict': 'from typing import Dict',
    'Tuple': 'from typing import Tuple',
    'Optional': 'from typing import Optional',
    'Set': 'from typing import Set',
    'Any': 'from typing import Any',
    'Union': 'from typing import Union',
}

def strip_markdown(code):
    """Remove markdown code blocks and artifacts."""
    code = code.strip()
    # Match ```python ... ``` or ``` ... ```
    match = re.search(r'```(?:python)?\s*\n(.*?)```', code, re.DOTALL)
    if match:
        code = match.group(1)
    # Remove stray backticks
    code = code.replace('```', '')
    # Remove leading "python" word artifact
    if code.lstrip().startswith('python\n'):
        code = code.lstrip()[7:]
    return code.strip()

def has_function_def(code, entry_point):
    """Check if code contains a def for the entry point."""
    pattern = r'^def\s+' + re.escape(entry_point) + r'\s*\('
    return bool(re.search(pattern, code, re.MULTILINE))

def extract_before_def(code, entry_point):
    """Split code into (imports/helpers before def, def+body)."""
    lines = code.split('\n')
    def_line = None
    for i, line in enumerate(lines):
        if re.match(r'def\s+' + re.escape(entry_point) + r'\s*\(', line.strip()):
            def_line = i
            break
    if def_line is None:
        return '', code
    return '\n'.join(lines[:def_line]), '\n'.join(lines[def_line:])

def extract_imports_from_body(code):
    """Extract import lines from the beginning of a function body."""
    lines = code.split('\n')
    imports = []
    body_lines = []
    in_imports = True
    for line in lines:
        stripped = line.strip()
        if in_imports and (stripped.startswith('import ') or stripped.startswith('from ')):
            imports.append(stripped)  # imports go at module level, no indent
        else:
            in_imports = False
            body_lines.append(line)
    return '\n'.join(imports), '\n'.join(body_lines)

def detect_missing_imports(code):
    """Scan for typing names used but not imported."""
    needed = []
    for name, imp in TYPING_IMPORTS.items():
        if re.search(r'\b' + name + r'\b', code) and imp not in code:
            needed.append(imp)
    # Common stdlib imports
    if 'math.' in code or 'math.sqrt' in code or 'math.floor' in code:
        if 'import math' not in code:
            needed.append('import math')
    if 'hashlib.' in code and 'import hashlib' not in code:
        needed.append('import hashlib')
    if 'itertools.' in code and 'import itertools' not in code:
        needed.append('import itertools')
    if 'collections.' in code and 'import collections' not in code:
        needed.append('import collections')
    return '\n'.join(needed)

def build_program(prompt, response, entry_point, tests):
    """
    Build a runnable Python program from prompt + model response + tests.
    Returns a list of candidate programs to try (first success wins).
    """
    code = strip_markdown(response)
    candidates = []
    
    # Strategy A: response contains the full function definition
    if has_function_def(code, entry_point):
        before, func_code = extract_before_def(code, entry_point)
        missing = detect_missing_imports(func_code)
        # Also check if prompt has imports we need
        prompt_imports = '\n'.join(l for l in prompt.split('\n') if l.strip().startswith(('import ', 'from ')))
        preamble = '\n'.join(filter(None, [prompt_imports, missing, before]))
        program = preamble + '\n\n' + func_code + '\n\n' + tests + f'\ncheck({entry_point})\n'
        candidates.append(program)
    
    # Strategy B: response is function body — dedent then indent into prompt
    # Extract any imports from the body first
    body_imports, clean_body = extract_imports_from_body(code)
    
    # Smart indentation: try multiple strategies, all become candidates
    lines = clean_body.split('\n')
    non_empty = [l for l in lines if l.strip()]
    indent_variants = []
    if not non_empty:
        indent_variants.append('    pass')
    else:
        indents = [len(l) - len(l.lstrip()) for l in non_empty]
        min_indent = min(indents)
        max_indent = max(indents)

        if min_indent >= 4:
            # Already indented — use as-is
            indent_variants.append(clean_body)

        if min_indent == 0:
            # Strategy B1: add 4 to ALL lines (uniform shift)
            indent_variants.append(textwrap.indent(clean_body, '    '))

            # Strategy B2: add 4 only to 0-indent lines (preserves nested structure)
            if max_indent > 0:
                mixed = []
                for line in lines:
                    if not line.strip():
                        mixed.append(line)
                    elif len(line) - len(line.lstrip()) == 0:
                        mixed.append('    ' + line)
                    else:
                        mixed.append(line)
                indent_variants.append('\n'.join(mixed))

        if 0 < min_indent < 4:
            # Partially indented — dedent then indent
            dedented = textwrap.dedent(clean_body)
            indent_variants.append(textwrap.indent(dedented, '    '))

    # Build a candidate program for each indent variant
    missing = detect_missing_imports(code)
    preamble = '\n'.join(filter(None, [missing, body_imports]))

    for indented in indent_variants:
        if preamble:
            program = preamble + '\n\n' + prompt + indented + '\n\n' + tests + f'\ncheck({entry_point})\n'
        else:
            program = prompt + indented + '\n\n' + tests + f'\ncheck({entry_point})\n'
        candidates.append(program)

    # Strategy C: response as-is appended to prompt (for already-indented code)
    program_c = prompt + code + '\n\n' + tests + f'\ncheck({entry_point})\n'
    if program_c not in candidates:
        candidates.append(program_c)
    
    return candidates

def run_program(program, timeout=5):
    """Execute a program and return (passed, error_type, stderr)."""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(program)
            tmpfile = f.name
        result = subprocess.run(['python3', tmpfile], capture_output=True, text=True, timeout=timeout)
        os.unlink(tmpfile)
        if result.returncode == 0:
            return True, 'pass', ''
        stderr = result.stderr
        if 'IndentationError' in stderr:
            return False, 'indentation', stderr[-300:]
        elif 'SyntaxError' in stderr:
            return False, 'syntax', stderr[-300:]
        elif 'assert' in stderr.lower() or 'AssertionError' in stderr:
            return False, 'assertion', stderr[-300:]
        elif 'NameError' in stderr:
            return False, 'name_error', stderr[-300:]
        elif 'TypeError' in stderr:
            return False, 'type_error', stderr[-300:]
        elif 'ImportError' in stderr or 'ModuleNotFoundError' in stderr:
            return False, 'import_error', stderr[-300:]
        else:
            return False, 'runtime', stderr[-300:]
    except subprocess.TimeoutExpired:
        try: os.unlink(tmpfile)
        except: pass
        return False, 'timeout', ''
    except Exception as e:
        try: os.unlink(tmpfile)
        except: pass
        return False, 'exception', str(e)

def evaluate_case(prompt, response, entry_point, tests):
    """Try all strategies, return (passed, error_type)."""
    candidates = build_program(prompt, response, entry_point, tests)
    
    best_error = 'no_candidates'
    for program in candidates:
        passed, etype, stderr = run_program(program)
        if passed:
            return True, 'pass'
        # Assertion = real model error, stop trying
        if etype == 'assertion':
            return False, 'assertion'
        # Keep trying other strategies for format errors
        if etype in ('indentation', 'syntax', 'name_error', 'import_error'):
            best_error = etype
            continue
        # Runtime/type errors are likely real
        if etype in ('type_error', 'runtime'):
            return False, etype
        best_error = etype
    
    return False, best_error

if __name__ == '__main__':
    print('HumanEval harness loaded. Use evaluate_case() to run.')

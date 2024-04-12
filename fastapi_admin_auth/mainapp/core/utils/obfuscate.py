import re
import ast
import random
import io
import tokenize
import os
import string
from corusadmin.wordfilter.models import FilterPolicy
from django.contrib.auth.models import User


def masking_forbidden(code, table, user):
    """개인정보 패턴과 불용어를 찾아서 마스킹 처리 
    """
    input_msg = code

    forbidden_words = []
    forbidden_patterns = []
    is_block = False   # 하나의 그룹이라도 True면 전체 Block

    group_list = user.groups.all()  # 일단 다 가져옴. 
    for group in group_list:
        try:
            policy = FilterPolicy.objects.get(group=group)
        except FilterPolicy.DoesNotExist:
            continue
        if policy.is_active:    
            res = policy.check_forbidden(message=input_msg)
            forbidden_words += res['keywords']
            forbidden_patterns += res['patterns']
            if res['is_block']:
                raise Exception("금지어가 포함되어 있습니다.")

    forbidden_keywords = list(set(forbidden_words))
    forbidden_patterns = list(set(forbidden_patterns))

    if len(forbidden_keywords+forbidden_patterns) <= 0:
        forbidden_patterns = []
        forbidden_keywords = []

    # patterns = {
    #     r'\b[0-9]{6}-[1-4][0-9]{6}\b': 'XXXXXX-XXXXXXX',  # 주민등록번호
    #     r'\b[A-Z][0-9]{8}\b': 'XXXXXXXXX',  # 여권번호
    #     r'\b[0-9]{2}-[0-9]{2}-[0-9]{6}-[0-9]{2}\b': 'XX-XX-XXXXXX-XX',  # 운전면허번호
    #     r'\b[0-9]{6}-[5-8][0-9]{6}\b': 'XXXXXX-XXXXXXX'  # 외국인등록번호
    # }


    for pattern in forbidden_patterns:
        code = re.sub(pattern, lambda match: re.sub(r'[^-]', 'X', match.group()), code)

    masked_code = code
    for keyword in forbidden_keywords:
        key = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(len(keyword)))
        table.pairs[key] = keyword
        masked_code = re.sub(fr"\b({keyword})\b", key, masked_code, flags=re.MULTILINE)

    return masked_code


def detect_language(source_code, filename):

    # 1st. 파일 확장자로 언어 판단
    file_ext = os.path.splitext(filename)[1]
    if (file_ext in ['.py']):
        return 'python'
    elif (file_ext in ['.java']):
        return 'java'
    else:
        return 'not supported'
    """
    lines = source_code.split('\n')

    # 2nd. import 키워드가 있는지 확인하여 언어 판단
    if sum(1 for line in lines if 'from ' in line and 'import ' in line) > 0:
        return 'python'
    if sum(1 for line in lines if 'import ' in line and line.strip().endswith(';')) > 0:
        if sum(1 for line in lines if 'import ' in line and ' from ' in line) == 0:
            return 'java'
    if sum(1 for line in lines if '#include ' in line) > 0:
        return 'not supported'

    # 3rd. 'class' 키워드를 포함하는 라인의 끝 문자에 따라 언어 판단
    java_keywords = ['public ', 'package ', 'private ', 'extends ', 'implements ', 'this.']

    if sum(1 for line in lines if 'class ' in line and line.strip().endswith(':')) > 0 :
        return 'python'
    if sum(1 for line in lines if 'class ' in line and line.strip().endswith('{')) > 0 :
        for keyword in java_keywords:
            if re.findall(fr"\b({keyword})\b", source_code):
                return 'java'

    # 4th. 특정 키워드를 포함하는 라인의 끝 문자에 따라 언어 판단
    java_keywords = ['public ', 'package ', 'private ', 'extends ', 'implements ', 'this.']
    python_keywords = ['def ', 'elif', 'None', 'self.']

    semicolon_ends = sum(1 for line in lines if line.strip().endswith(';'))
    colon_ends = sum(1 for line in lines if line.strip().endswith(':'))

    if semicolon_ends >= 1:
        for keyword in java_keywords:
            if re.findall(fr"\b({keyword})\b", source_code):
                return 'java'

    if colon_ends >= 1:
        for keyword in python_keywords:
            if re.findall(fr"\b({keyword})\b", source_code):
                return 'python'

    return 'not detected'
    """

def remove_comments_java(code):
    pattern = r'(\".*?\"|\'.*?\'|/\*.*?\*/|//.*?$)'
    tokens = re.split(pattern, code, flags=re.DOTALL|re.MULTILINE)

    out = []
    for token in tokens:
        if token.startswith('//'):
            continue
        if token.startswith('/*') and token.endswith('*/'):
            continue
        out.append(token)

    return ''.join(out)


def remove_comments_python(code):
    io_obj = io.StringIO(code)
    out = ""
    prev_toktype = tokenize.INDENT
    last_lineno = -1
    last_col = 0
    for tok in tokenize.generate_tokens(io_obj.readline):
        token_type = tok[0]
        token_string = tok[1]
        start_line, start_col = tok[2]
        end_line, end_col = tok[3]
        if start_line > last_lineno:
            last_col = 0
        if start_col > last_col:
            out += (" " * (start_col - last_col))
        if token_type == tokenize.COMMENT:
            pass
        elif token_type == tokenize.STRING:
            if (prev_toktype != tokenize.INDENT) and (prev_toktype != tokenize.DEDENT):
                if prev_toktype != tokenize.NEWLINE:
                    if start_col > 0:
                        out += token_string
        else:
            out += token_string
        prev_toktype = token_type
        last_col = end_col
        last_lineno = end_line
    out = '\n'.join(l for l in out.splitlines() if l.strip())
    return out


def remove_comments(code, language):
    """This function effectively removes the documented section (comments)
       from the provided source code and delivers the refined code
    """
    if language == 'python':
        return remove_comments_python(code)
    elif language == 'java':
        return remove_comments_java(code)
    else:
        return code


def generate_unique_name(used):
    """Create a unique name to convert not included in the used set."""
    while True:
        new_name = "".join(random.choice(["I", "l"]) for i in range(random.randint(8, 20)))
        if new_name not in used:
            used.add(new_name)
            return new_name


def obfuscate_code_java(code, table):
    renamed_code = code
    pairs = table.pairs
    used = table.used

    class_names = []
    method_names = []
    parameter_names = []
    variable_names = []

    def find_variables(code):
        variables = re.findall(r'\b(?:[A-Z][a-zA-Z0-9_]*\s*(?:<.*?>)?|long|float|double|String|boolean|char|byte|short|int)*\s*(\w+)(?:\[\])*\s*=', code)
        return variables

    def find_methods(code):
        methods = re.finditer(r'\b(?:public|private|protected|static)*\s+(?:[\w\[\]]+\s+)*(\w+)\s*\(([^)]*?)\)\s*{', code)
        return methods

    def find_classes(code):
        classes = re.finditer(r'\b(?:public|private\s+)?\bclass\b\s+(\w+)', code)
        return classes
    
    for class_match in find_classes(renamed_code):  # find classes
        class_name = class_match.group(1)
        class_names.append(class_name)

        class_body_start = class_match.end()
        brace_count = 0
        for i in range(class_body_start, len(renamed_code)):
            if renamed_code[i] == '{':
                brace_count += 1
            elif renamed_code[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    class_body_end = i
                    break

        class_body = renamed_code[class_body_start:class_body_end]

        variables = find_variables(class_body) # find variables in class
        variable_names += variables

        for method_match in find_methods(class_body):  # find mathods in class
            method_name = method_match.group(1)
            method_names.append(method_name)

            parameters = method_match.group(2)  # find parameters
            param_names = [re.split(r'\s+', param.strip())[-1] for param in parameters.split(',') if param.strip()]
            parameter_names += param_names

            method_body_start = method_match.end()  # find variables in method
            method_body_end = method_body_start + class_body[method_body_start:].find('}')
            method_body = class_body[method_body_start:method_body_end]

            variables = find_variables(method_body)
            variable_names += variables

    total_names = set(class_names + method_names + parameter_names + variable_names)

    for name in total_names:
        if name in ["main"]:
            continue
        pairs[f'{generate_unique_name(used)}'] = name

    for key, value in pairs.items():
        pairs[key] = re.sub(r'(\w+)\[\]', r'\1', value)


    import_regex = r'^\s*(import).*?$'
    string_regex = r"('|\")[\x1f-\x7e]{1,}?('|\")"
    placeholder = os.urandom(16).hex()
    originals = []
    imports = re.finditer(import_regex, renamed_code, flags=re.MULTILINE)
    strings = re.finditer(string_regex, renamed_code, flags=re.MULTILINE)    
    original_strings = list(imports) + list(strings)

    for matchNum, match in enumerate(original_strings, start=1):
        originals.append(match.group().replace("\\", "\\\\"))

    renamed_code = re.sub(string_regex, f"'{placeholder}'", renamed_code, flags=re.MULTILINE)
    renamed_code = re.sub(import_regex, f"'{placeholder}'", renamed_code, flags=re.MULTILINE)

    for key, value in pairs.items():
        renamed_code = re.sub(fr"\b({value})\b", key, renamed_code, flags=re.MULTILINE)

    replace_placeholder = r"('|\")" + placeholder + r"('|\")"
    for original in originals:
        renamed_code = re.sub(replace_placeholder, original, renamed_code, 1, flags=re.MULTILINE)

    return renamed_code, pairs


def obfuscate_code_python(code, table):
    renamed_code = code
    pairs = table.pairs
    used = table.used

    try:
        parsed = ast.parse(renamed_code)
    except SyntaxError:
        raise Exception("코드의 문법이 맞지 않습니다.")

    funcs = { node for node in ast.walk(parsed) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) }
    classes = { node for node in ast.walk(parsed) if isinstance(node, ast.ClassDef) }
    args = { node.id for node in ast.walk(parsed) if isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Load) }
    attrs = { node.attr for node in ast.walk(parsed) if isinstance(node, ast.Attribute) and not isinstance(node.ctx, ast.Load) }

    for func in funcs:
        if func.args.args:
            for arg in func.args.args:
                args.add(arg.arg)
        if func.args.kwonlyargs:
            for arg in func.args.kwonlyargs:
                args.add(arg.arg)
        if func.args.vararg:
            args.add(func.args.vararg.arg)
        if func.args.kwarg:
            args.add(func.args.kwarg.arg)

    for func in funcs:
        if func.name in ["__init__", "__call__"]:
            continue
        pairs[fr'{generate_unique_name(used)}'] = func.name

    for _class in classes:
        pairs[fr'{generate_unique_name(used)}'] = _class.name

    for arg in args:
        if arg in ["self"]:
            continue
        pairs[fr'{generate_unique_name(used)}'] = arg

    for attr in attrs:
        pairs[fr'{generate_unique_name(used)}'] = attr

    string_regex = r"('|\")[\x1f-\x7e]{1,}?('|\")"
    original_strings = re.finditer(string_regex, code, flags=re.MULTILINE)
    originals = []

    for matchNum, match in enumerate(original_strings, start=1):
        originals.append(match.group().replace("\\", "\\\\"))

    placeholder = os.urandom(16).hex()
    code = re.sub(string_regex, f"'{placeholder}'", code, flags=re.MULTILINE)

    # for i in range(len(originals)):
    #     for key, value in pairs.items():
    #         originals[i] = re.sub(r"({.*)(" + value + r")(.*})", "\\1" + key + "\\3", originals[i], re.MULTILINE)


    for key, value in pairs.items():
        code = re.sub(fr"\b({value})\b", key, code, flags=re.MULTILINE)

    replace_placeholder = r"('|\")" + placeholder + r"('|\")"
    for original in originals:
        code = re.sub(replace_placeholder, original, code, 1, flags=re.MULTILINE)

    return code, pairs


def obfuscate_code(code, table, language):
    """Obfuscate code by renaming classes, variables and functions."""

    if language == 'python':
        code, pairs = obfuscate_code_python(code, table)
    elif language == 'java':
        code, pairs = obfuscate_code_java(code, table)
    return code, pairs





def convert_to_obf(code: str, filename: str, user: User):
    """The function renames functions, classes, arguments, and attributes in the provided source code with randomly
       generated names while preserving the original code structure and string literals
    """
    class ObfuscateTable():
        pairs: dict = {}
        used: set = set()

    table_ = ObfuscateTable()

    try:
        lang_ = detect_language(code, filename)
        if (lang_ == 'not_supported'):
            return code, {}
        
        code_ = remove_comments(code, lang_)
        code_ = masking_forbidden(code_, table_, user)
        resp = obfuscate_code(code_,  table_, lang_)
        return resp
    
    except Exception as e:
        raise Exception(f"Failed to obfuscate {filename} due to {e}")



def restore_from_obf(response, pairs):
    """The function restores the original names of functions, classes, arguments, and attributes
       in the provided source code
    """
    if (pairs) == {}:
        return response

    pairs = dict(sorted(pairs.items(), key=lambda x: len(x[0]), reverse=True))

    for key, value in pairs.items():
        response = response.replace(key, value)
        for key, value in pairs.items():
            response = response.replace(key, value)

    return response

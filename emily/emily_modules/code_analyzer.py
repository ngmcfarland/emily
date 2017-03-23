from fnmatch import fnmatch
import yaml
import os
import re

curdir = os.path.dirname(__file__)
with open(os.path.join(curdir,'conf/code_analyzer_config.yaml'),'r') as f:
    config = yaml.load(f.read())


def analyze_python(root_dir,ignore_files=[],max_levels=0,verbose=False):
    file_results = {}
    python_files,local_stuff = get_python_files(search_dir=root_dir,ignore_files=ignore_files,max_levels=max_levels)
    for file in python_files:
        file_results[file] = get_line_counts(file=file,local_stuff=local_stuff)
    summary,functions,classes,dependencies,variables,counts = summarize_results(file_results=file_results,verbose=verbose)
    results = {'summary':summary,'files':list(file_results),'functions':functions,'classes':classes,'dependencies':dependencies,'variables':variables,'counts':counts}
    return results


def get_python_files(search_dir,ignore_files=[],python_files=[],local_stuff=[],level=1,max_levels=0):
    for file in os.listdir(search_dir):
        if True not in [fnmatch(file,x) for x in ignore_files]:
            if file.endswith('.py'):
                python_files.append("{}/{}".format(search_dir,file))
                local_stuff.append(file.replace('.py',''))
            elif max_levels == 0 or level <= max_levels:
                try:
                    python_files,local_stuff = get_python_files(search_dir="{}/{}".format(search_dir,file),ignore_files=ignore_files,python_files=python_files,local_stuff=local_stuff,level=level+1,max_levels=max_levels)
                    if '__init__.py' in os.listdir("{}/{}".format(search_dir,file)):
                        local_stuff.append(file)
                except:
                    pass
    return python_files,local_stuff


def get_line_counts(file,local_stuff):
    comments = 0
    code = 0
    fors = 0
    whiles = 0
    ifs = 0
    withs = 0
    functions = []
    classes = []
    dependencies = []
    variables = []
    comment_block = False
    with open(file,'r') as f:
        lines = f.read().splitlines()
    for file_line in lines:
        line = file_line.strip()
        if len(line) > 0:
            if line[:3] == '"""' or (comment_block and line[-3:] == '"""'):
                comments += 1
                comment_block = not comment_block
            elif line[0] == '#':
                comments += 1
            elif line[:4] == 'def ':
                functions += get_object_details(code_line=line,obj_type='function')
                code += 1
            elif line[:6] == 'class ':
                classes += get_object_details(code_line=line,obj_type='class')
                code += 1
            elif line[:7] == 'import ' or line[:5] == 'from ':
                dependencies += get_object_details(code_line=line,obj_type='dependency',local_stuff=local_stuff)
                code += 1
            elif line[:4] == 'for ':
                fors += 1
                code += 1
            elif line[:6] == 'while ':
                whiles += 1
                code += 1
            elif line[:3] == 'if ':
                ifs += 1
                code += 1
            elif line[:5] == 'with ':
                withs += 1
                code += 1
            else:
                variables += get_object_details(code_line=line,obj_type='variable')
                code += 1
    result = {'comments':comments,
        'code':code,
        'fors':fors,
        'whiles':whiles,
        'ifs':ifs,
        'withs':withs,
        'functions':functions,
        'classes':classes,
        'dependencies':dependencies,
        'variables':variables}
    return result



def get_object_details(code_line,obj_type,local_stuff=None):
    details = []
    if obj_type == 'function':
        match = re.match(r"^def\s([A-Za-z0-9_\-\.]+)\((.+)?\)\:$",code_line)
        name = match.group(1)
        args = match.group(2) if len(match.groups()) == 2 else None
        if args is not None:
            details.append({'name':name,'args':args})
        else:
            details.append({'name':name})
    elif obj_type == 'class':
        match = re.match(r"^class\s([A-Za-z0-9_\-\.]+)\((.+)?\)\:$",code_line)
        name = match.group(1)
        args = match.group(2) if len(match.groups()) == 2 else None
        if details is not None:
            details.append({'name':name,'args':args})
        else:
            details.append({'name':name})
    elif obj_type == 'dependency':
        line = code_line.split(' as ')[0]
        if re.search(r"^import",code_line):
            match = re.match(r"^import\s(.+)$",line)
            for dependency in match.group(1).split(','):
                if dependency.strip() not in local_stuff:
                    details.append({'name':dependency.strip()})
        elif re.search(r"^from",code_line):
            match = re.match(r"^from\s([A-Za-z0-9_\-\.]+)\simport\s(.+)",line)
            for dependency in match.group(2).split(','):
                if match.group(1) not in ['.','..'] and match.group(1).split('.')[0] not in local_stuff:
                    details.append({'name':"{}.{}".format(match.group(1),dependency.strip())})
    elif obj_type == 'variable':
        match = re.match(r"^([A-Za-z0-9_\-]+)\s?=",code_line)
        if match is not None:
            details.append({'name':match.group(1)})
    return details


def summarize_results(file_results,verbose=False):
    total_code = 0
    total_comments = 0
    total_fors = 0
    total_whiles = 0
    total_ifs = 0
    total_withs = 0
    all_functions = []
    all_classes = []
    all_dependencies = []
    all_variables = []
    for file in file_results:
        module = file.split('/')[-1].replace('.py','')
        total_code += file_results[file]['code']
        total_comments += file_results[file]['comments']
        total_fors += file_results[file]['fors']
        total_whiles += file_results[file]['whiles']
        total_ifs += file_results[file]['ifs']
        total_withs += file_results[file]['withs']
        all_functions += ["{}.{}".format(module,x['name']) for x in file_results[file]['functions']]
        all_classes += ["{}.{}".format(module,x['name']) for x in file_results[file]['classes']]
        all_dependencies += [x['name'] for x in file_results[file]['dependencies']]
        all_variables += [x['name'] for x in file_results[file]['variables']]
    functions = sorted(all_functions)
    classes = sorted(all_classes)
    dependencies = sorted(set(all_dependencies))
    variables = sorted(all_variables)
    summary = config['summary_template'].format(file_count=len(file_results),
        code_count=total_code,
        comment_count=total_comments,
        function_count=len(functions),
        class_count=len(classes),
        dependency_count=len(dependencies),
        variable_count=len(variables),
        if_count=total_ifs,
        with_count=total_withs,
        for_count=total_fors,
        while_count=total_whiles)
    counts = {'python_files': len(file_results),
        'code':total_code,
        'comments':total_comments,
        'functions':len(functions),
        'classes':len(classes),
        'dependencies':len(dependencies),
        'variables':len(variables),
        'if_statements':total_ifs,
        'with_statments':total_withs,
        'for_loops':total_fors,
        'while_loops':total_whiles}
    return summary,functions,classes,dependencies,variables,counts
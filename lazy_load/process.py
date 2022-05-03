import json
from subprocess import check_output
import sys
import re

def get_section(fn, s):
  out = check_output(f"wasm-objdump -j {s} -x {fn}".split()).decode().strip().split('\n')
  for i, l in enumerate(out):
    if s in l:
      break
  return out[i+1:]

def get_f_names(fn):
  imports = get_section(fn, "Import")
  exports = get_section(fn, "Export")
  p = re.compile(r' - func\[([0-9]+)\].*<- env\.(.*)')
  imports = [(int(p.match(s).group(1)), p.match(s).group(2)) for s in imports if p.match(s)]
  p = re.compile(r' - func\[([0-9]+)\].*-> "(.*)"')
  exports = [(int(p.match(s).group(1)), p.match(s).group(2)) for s in exports if p.match(s)]
  return dict(imports + exports)
  
def get_import_indices(fn):
  imports = get_section(fn, "Import")
  p = re.compile(r' - func\[([0-9]+)\].*<- (.*)')
  imports = [int(p.match(s).group(1)) for s in imports if p.match(s)]
  return list(imports)

def get_imports(fn):
  imports = get_section(fn, "Import")
  imports = [s.split('<- env.')[1] for s in imports]
  imports = filter(lambda x:x!="memory", imports)
  return list(imports)

def get_exports(fn):
  exports = get_section(fn, "Export")
  exports = filter(lambda x:x.startswith(" - func"), exports)
  exports = [s.split('-> "')[1][:-1] for s in exports]
  exports = filter(lambda x:x!="__wasm_call_ctors", exports)
  return list(exports)

def get_fn_deps(fn):
  imports = get_section(fn, "Import")
  fn_idx = filter(lambda x:x.startswith(" - func"), [s.split(' <- env.')[0] for s in imports])
  p = re.compile(r' - func\[([0-9]+)\].*')
  fn_idx = [int(p.match(s).group(1)) for s in fn_idx]
  out = check_output(f"wasm-objdump -d {fn}".split()).decode().strip().split('\n')
  for i, l in enumerate(out):
    if l == "Code Disassembly:":
      break
  code = out[i+2:]
  func_calls = {} 
  cur_fn = None
  fn_start = re.compile(r'[0-9a-f]+ func\[([0-9]+)\].*')
  call_instr = re.compile(r'.*\| call ([0-9]+) <.*')
  for l in code:
    m = fn_start.match(l)
    if m:
      cur_fn = int(m.group(1))
    m = call_instr.match(l)
    if m:
      if cur_fn not in func_calls:
        func_calls[cur_fn] = []
      func_calls[cur_fn].append(int(m.group(1)))
  return func_calls

def get_import_deps(fn):
  import_deps = {}
  raw_fn_deps = get_fn_deps(fn)
  import_indices = get_import_indices(fn)
  def resolve(f_idx):
    if f_idx in import_indices:
      return [f_idx]
    if f_idx in import_deps: # recursive case (cycles as well)
      return import_deps[f_idx]
    import_deps[f_idx] = set()
    if f_idx in raw_fn_deps:
      for call in raw_fn_deps[f_idx]:
        import_deps[f_idx] = import_deps[f_idx].union(resolve(call))
    return import_deps[f_idx] 
  for f_idx in raw_fn_deps:
    resolve(f_idx)
  named_import_deps = {}
  names = get_f_names(fn)
  for k in import_deps:
    named_import_deps[names[k]] = []
    for call in import_deps[k]:
      named_import_deps[names[k]].append(names[call])
  return named_import_deps

export_locs = {}
module_imports = {}
func_import_deps = {}
for fn in sys.argv[1:]:
  print(f"processing {fn}...")
  module_imports[fn] = get_imports(fn)
  for exp in get_exports(fn):
    export_locs[exp] = fn
  imps = get_import_deps(fn)  
  for k in imps:
    func_import_deps[k] = imps[k]

j = json.dumps({
  "module_imports": module_imports,
  "func_locations": export_locs,
  "func_import_deps": func_import_deps 
}, indent=2)
with open('processed.json', 'w') as f:
  f.write(j)

function log(...args) {
  const str = args.join(" ");
  document.querySelector('#output').appendChild(document.createTextNode(str));
  document.querySelector('#output').appendChild(document.createElement('br'));
}

async function benchmark(f) {
  const w0 = performance.now();
  for (let i = 0; i < 100; ++i) {
    await f();
  }
  const w1 = performance.now();
  const iters = 10000;// / (w1 - w0);
  const t0 = performance.now();
  for (let i = 0; i < iters; ++i) {
    await f();
  }
  const t1 = performance.now();
  return Math.round(1e3 * iters / (t1 - t0));
}

const memory = new WebAssembly.Memory({initial:10, maximum:1000});

class Func {
  constructor(fn, loader) {
    this.loaded = false;
    this.loader = loader;
    this.fn = fn;
    this.func = null;
  }

  async call(...args) {
    if (!this.loaded) {
      try {
        await this.loader.load(this.fn);
      } catch(e) {
        console.log(e);
      }
    }
    return this.func(...args);
  }
}

class Loader {
  constructor(json_file) {
    this.json_file = json_file;
  }

  async init() {
    this.json = await (await fetch(this.json_file)).json();
    this.module_imports = this.json.module_imports;
    this.func_locations = this.json.func_locations;
    this.funcs = {};
    for (let func of Object.keys(this.func_locations)) {
      this.funcs[func] = new Func(func, this);
    }
    this.func_import_deps = this.json.func_import_deps;
  }

  async load(fn) {
    console.log(`loading fn ${fn}`);
    if (this.funcs[fn].loaded) {
      console.log(`found cached ${fn}`);
      return;
    }
    if (fn in this.func_import_deps) {
      for (let dep of this.func_import_deps[fn]) {
        if (this.funcs[dep].loaded) {
          continue;
        }
        try {
          await this.load(dep);
        } catch(e) {
          console.log(e);
        }
      }
    }
    try {
      await this.load_wasm(this.func_locations[fn]);
    } catch(e) {
      console.log(e);
    }
    console.log(`done with fn ${fn}`);
  }

  async load_wasm(wasm_fn) {
    console.log(`loading module ${wasm_fn}`);
    const imports = { env: { memory: memory } };
    if (wasm_fn in this.module_imports) {
      for (let imp of this.module_imports[wasm_fn]) {
        imports.env[imp] = this.funcs[imp].func;
      }
    }
    try {
      const m = await WebAssembly.instantiateStreaming(fetch(wasm_fn), imports);
      const exports = m.instance.exports;
      for (let e of Object.keys(exports)) {
        if (e in this.funcs) {
          this.funcs[e].func = exports[e];
          this.funcs[e].loaded = true;
        }
      }
    } catch(e) {
      console.log(e);
    }
    console.log(`done with ${wasm_fn}`);
  }

}

try{
  async function benchmark_loader(l) {
    return await benchmark(async() => {
      await l.call(1);
    });
  }
  async function bench(r) {
    return await benchmark(async() => {
      r(1);
    });
  }
  let t0 = performance.now();
  window.loader = new Loader('processed.json');
  await window.loader.init();
  log(`calculating loader.f_96(1):`, await loader.funcs._Z4f_96j.call(1));
  log(`calculating loader.f_5(1):`, await loader.funcs._Z3f_5j.call(1));
  log(`calculating loader.f_109(1):`, await loader.funcs._Z5f_109j.call(1));
  let t1 = performance.now();
  log(`${Math.round(t1 - t0)} ms to load + calculate`);
  log(`benchmarking loader.f_96 (iter/sec):`, await benchmark_loader(loader.funcs._Z4f_96j));
  log(`benchmarking loader.f_5 (iter/sec):`, await benchmark_loader(loader.funcs._Z3f_5j));
  log(`benchmarking loader.f_109 (iter/sec):`, await benchmark_loader(loader.funcs._Z5f_109j));

  t0 = performance.now();
  const imports = { env: { memory: memory } };
  const m = await WebAssembly.instantiateStreaming(fetch('f_all.wasm'), imports);
  window.ref = m.instance.exports;
  log(`calculating f_96(1):`, ref._Z4f_96j(1));
  log(`calculating f_5(1):`, ref._Z3f_5j(1));
  log(`calculating f_109(1):`, ref._Z5f_109j(1));
  t1 = performance.now();
  log(`${Math.round(t1 - t0)} ms to load + calculate`);
  log(`benchmarking f_96 (iter/sec):`, await bench(ref._Z4f_96j));
  log(`benchmarking f_5 (iter/sec):`, await bench(ref._Z3f_5j));
  log(`benchmarking f_109 (iter/sec):`, await bench(ref._Z5f_109j));
} catch(e) {
  console.log(e);
}

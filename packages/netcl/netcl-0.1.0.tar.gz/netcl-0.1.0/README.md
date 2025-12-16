# PyOpenCL KI-Framework Plan

## Ueberblick & Ziele
- Hochperformantes KI-Framework auf Basis von PyOpenCL mit klarer Trennung zwischen Low-Level-Kernel-Implementierungen und High-Level-Ausfuehrungsmodellen.
- Minimierung des Host-Device-Overheads durch effiziente Speicherverwaltung, asynchrone Transfers und Kernel-Fusion.
- Multi-GPU-Skalierung (Daten- und perspektivisch Modellparallelismus) mit reproduzierbarem Verhalten und robustem Autograd.

## Leitprinzipien
- Trennung der Schichten: Devices/Memory/Kernels (Low-Level) vs. Ops/Autograd/Runtime/Distributed (High-Level).
- Alle Ops setzen auf rudimentaere OpenCL-Bausteine (Loads/Stores, simple Arithmetik, lokale Reduktionen); komplexe Ops werden als Komposition/Fusion daraus erzeugt.
- Datenbewegungen minimieren: Reuse von Buffern, Pinned Host Memory, Overlap von Compute & Copy, Zero-Copy wo moeglich.
- Determinismus optional: reproduzierbare Seeds, konsistente Reduktionen.
- Erweiterbarkeit: neue Ops, neue Devices, austauschbare Kernel-Build-Parameter via Cache, Autotuning und dynamische Kernel-Generierung.
- Graph/Pipeline-fokussiert: Aehnlich TF: User baut ANN/Graph; Runtime generiert eine Pipeline aus elementaren Ops, alloziert/reused Buffer, minimiert Python-Interaktion zur Laufzeit.

## Anforderungen
- Funktional:
  - Geraete-Discovery, Kontext- und Queue-Management mit Fallback-Strategie.
  - Speicher-Allocator/Pool (Buckets, Reuse, Sub-Buffers), Pinned Host Buffers, asynchrone Copies.
  - Kernel-Bibliothek: Matmul/GEMM, Convolution (im2col + Spezialfaelle), Elementwise (unary/binary), Reduktionen, Softmax, LayerNorm/BatchNorm, Scatter/Gather, RNG.
  - Autograd-Engine mit Grad-Registrierung pro Op; Unterstuetzung fuer Gradient-Accumulation.
  - Multi-GPU-Kollektive: AllReduce, Broadcast, Scatter/Gather; Datenparallelismus als erster Modus.
  - API: Tensor mit Dtype/Device/Strides, Eager-Ausfuehrung; optional Graph/Lazy spaeter.
  - Profiling/Tracing: Event-Timing, Bandbreitenmessung, Kernel-Stats.
- Nicht-funktional:
  - Performance-Portabilitaet ueber OpenCL; Feature-Detection (Subgroups, FP16/BF16, Images).
  - Stabilitaet unter Stress (viele kleine Kernels, grosse Tensors); sauberes Fehler-Handling (Build-Fail, OOM).
  - Klare Fehlermeldungen und Debug-Optionen (Assertions fuer Shapes/Strides).

## Architektur (Schichten)
- `core.devices`: Device/Kontext/Queue-Discovery, Capability-Cache, Seed-Management.
- `core.memory`: Buffer-Objekte, Pool/Allocator, Pinned Host Buffers, Sub-Buffers, Async Copy.
- `core.kernels`: Kernel-Quellen, Build/Cache, Feature-Gates, Tuning-Parameter (Workgroup, Vectorization).
- `ops` (Low-Level): Matmul, Conv2D/Depthwise, Elementwise, Reduce, Softmax, LayerNorm/BatchNorm, RNG.
- `autograd`: Tape oder Graph, Grad-Registrierung pro Op, Backward-Kernels, Grad-Accumulation.
- `distributed`: AllReduce/Broadcast/Scatter-Gather, Parameter-Sharding, Host-Relay als Fallback.
- `runtime`: Scheduler fuer Queues/Events, Stream-Ordering, Overlap von Compute/Copy (Double-Buffering); Graph Executor der ANN/Op-Graph in Pipelines uebersetzt und Buffer-Lebenszeiten verwaltet.
- `api`: Tensor-Klasse, Module/Layer-Primitives, Optimizer (SGD/Adam), Checkpointing.
- `profiling`: Event-Timing, Bandwidth/Flops-Schaetzung, Kernel-Stats Dump.

## Speicher- & Transfer-Strategie
- Memory Pool mit Buckets; Reuse ueber Lebenszeit-Tracking; Minimierung von Fragmentation.
- Pinned Host Memory fuer H2D/D2H; `enqueue_copy` asynchron mit Events; Batch-Transfers.
- Zero-Copy nutzen, wenn Plattform Host-Device-Sharing erlaubt; sonst Staging-Puffer.
- Layout-Planer (z. B. NHWC vs. NCHW) abhaengig vom Kernel; Stride-Awareness in Ops.
- Double-/Triple-Buffering fuer Datenpipelines, um IO und Compute zu ueberlappen.
- Graph-basierte Buffer-Reuse: Lebenszeit-Analyse des ANN/Op-Graphs fuer Platzierung/Reuse; Inplace- und Alias-Strategien wo sicher.

## Kernel-Bibliothek & Optimierung
- Primitives: Load/Store, einfache Arithmetik, Shuffle/Subgroup-Reduce (falls verfuegbar), lokale Speicher-Kacheln, atomare Operationen. Alle komplexen Ops bauen darauf auf.
- Dynamischer Kernel-Generator: erzeugt Quellcode basierend auf Hyperstrategie (Layout, Fusion, Tiling) und Device-Capabilities; wendet Template-Parameter und Konstantenfaltung an.
- Matmul/GEMM: Tiling + lokale Speicher-Kacheln; Vectorization; Autotuning von M/N/K-Tiles und Workgroup-Groessen.
- Convolution: Im2col + GEMM als Baseline; Spezialkernel fuer 1x1 und 3x3; Depthwise-Kernels.
- Elementwise: Fused Kernel Generator (AST -> OpenCL C) fuer Ketten (bias + activation).
- Reduktionen: Hierarchisch (Workgroup-Reduktion -> global), optionale Subgroup-Optimierung; deterministische Pfade.
- RNG: Counter-based (z. B. Philox/Threefry); pro Work-Item Streams; reproduzierbare Seeds.
- Mixed Precision: FP16/BF16 wenn verfuegbar; Akkumulation in FP32; Fallback auf FP32.

## Multi-GPU & Distributed
- Datenparallel: Parameter repliziert; Batch-Sharding; Gradient AllReduce (Ring/Tree). Start mit Host-Relay (Copy -> Reduce -> Scatter), spaetere Device-zu-Device-Pfade pruefen.
- Modellparallel (spaeter): Parameter-Shards, Pipeline-Parallelismus, Punkt-zu-Punkt Copies.
- Konsistenz: Events/Barrieren fuer Ordering; deterministische Reduktionen optional; FP32 Master Weights moeglich.
- Hyperstrategie fuer Ressourcenaufteilung: Tiling/Partitionierung pro Device (Batch-Splits, Tensor-Shards) wird dynamisch nach Device-Memory/Compute/Link-Bandbreite bestimmt; Scheduler verteilt Work-Items und Buffers entsprechend.

## Build/Cache & Autotuning
- Kernel-Build-Cache pro Device (Hash aus Source, Build-Options, Treiber-Version).
- Autotuning-DB pro Device (Tile- und Workgroup-Sizes); Persistenz auf Disk; konservative Defaults ohne Tuning.
- Capability-Checks (Subgroups, FP16/BF16, Images vs. Buffers) steuern Kernel-Pfade.

## API-Skizze (Python)
- `Tensor(device, shape, dtype, data=None, requires_grad=False)`
- `ops.matmul(a, b)`, `ops.conv2d(x, w, stride, pad)`, `ops.relu(x)`, `ops.softmax(x, axis)`, `ops.layer_norm(x, gamma, beta)`
- `tensor.backward(grad=None)`; `optimizer.step()`, `optimizer.zero_grad()`
- `with device.stream(): ...` fuer explizite Queue/Stream-Wahl.
- `distributed.init(devices=[...])`, `distributed.all_reduce(tensor)`
- Graph/Pipeline: `with graph(): y = model(x)` erzeugt statischen Graph; `executor.run(graph, inputs)` uebersetzt in Pipeline mit minimaler Python-Beteiligung.

## High-Level Interface (Plan)
- `netcl.Tensor`: Zentrale Datenstruktur; Flags fuer `requires_grad`; Methoden `to_host()`, `from_host()`, `from_shape(pool=...)`.
- `netcl.autograd`:
  - `tensor(x, requires_grad=False)` -> Node
  - Ops: `add`, `relu`, `bias_add`, `matmul_op` (weitere Ops folgen: conv2d, softmax, reduce_sum)
  - `Tape.backward(loss, grad=None)` mit Grad-Akkumulation und ones_like-Seed.
- Optimizer (geplant):
  - Basis: `Optimizer(params, lr)`, API: `step()`, `zero_grad()`, `clip_grad(norm)` optional.
  - Implementierungen: `SGD(lr, momentum=0, weight_decay=0)`, `Adam(lr, betas=(0.9,0.999), eps=1e-8, weight_decay=0)`.
  - Params sind `Tensor` mit `requires_grad=True`; Grad-Lesen via `tensor.grad`.
- `netcl.ops` (High-Level Wrappers auf Kernels):
  - Elementwise: `elementwise_binary(expr)`, `relu`, `bias_add`
  - Reduktionen: `reduce_sum(x, axis=None/0/1)`
  - Softmax: `softmax(x, axis=1)`
  - Matmul: `matmul(a, b, pool=None)`
  - Conv: `conv2d(x, w, pool=None)` (NCHW, stride=1, pad=0 als Start)
- Layers (geplant):
  - `Linear(in_features, out_features, bias=True)` -> nutzt `matmul + bias_add`; init Xavier/kaiming; Parameter sind Tensoren.
  - `Conv2d(in_channels, out_channels, kernel_size, stride=1, padding=0)` -> nutzt `conv2d`; Parameter: weights (+ optional bias).
  - Aktivierungen: `ReLU`, `Sigmoid`, `Tanh`, `LeakyReLU`, `Dropout(p)`.
  - Pooling: `max_pool2d`.
  - `Sequential(*layers)` -> Vorwaertsverkettung, sammelt Parameter fuer Optimizer.
- Convenience-Funktionen:
  - Initializer: `xavier_uniform(tensor)`, `kaiming_uniform(tensor)`.
  - Losses: `mse_loss(pred, target)`, `cross_entropy(logits, targets)` (Softmax + NLL).
  - Data movement: `to_host()`, `from_host()`, `to(device)` (spaeter).
  - Graph shortcuts: `Graph.from_layers(layers, input_tensors)` baut Ops-Graph aus Layer-Liste.
- Serialisierung/Checkpointing (ohne andere AI-Framework-Imports):
  - Format-Vorschlag: Metadaten als JSON (Layer-Typ, Shapes, Hyperparams), Gewichte als `.npz` (NumPy-kompatibel) oder Binär-Blob pro Tensor.
  - API: `save(model, path)` schreibt JSON+Gewichte; `load(path, device=None)` rekonstruiert Layer/Tensoren; kompatibel mit Lazy-Loading fuer grosse Gewichte.
  - Graph-Snapshots: `save_graph(graph, path)` speichert Op-Listen und Topologie; `load_graph(path)` rekonstruiert fuer Executor.
  - Versionierung: Schema-Version im JSON, Hash pro Gewicht fuer Integritaet.
- Training Loop (geplant Muster):
  ```
  tape = Tape()
  model = Sequential(Linear(784, 256), ReLU(), Linear(256, 10))
  opt = Adam(model.parameters(), lr=1e-3)
  out = model(tensor(x, True), tape=tape)
  loss = cross_entropy(out, tensor(targets))
  tape.backward(loss)
  opt.step(); opt.zero_grad()
  ```
- Progress/Monitoring:
  - `ProgressBar(total, epoch=None)` aus `netcl.utils.progress`; `update(step, info={"loss":..., "acc":..., "it/s":...})` zeigt animierten Balken (it/s, ETA, Epochen).
- Graph/Pipeline:
  - `Graph.add_op(name, fn, inputs, shape, dtype)` -> TensorRef
  - `GraphExecutor.run(graph)` mit Toposort, optionaler `fusion_hook`, BufferPool-Reuse, (spaeter) async overlap.
- Memory/Pooling:
  - `BufferPool` bucket-basiert; Tensor speichert `pool_handle`; Executor gibt Buffers nach Refcount frei.
- Distributed (Platzhalter):
  - API-Signaturen: `all_reduce`, `broadcast`, `scatter`, `gather` (Implementierung folgt).
- Profiling:
  - `EventTimer.time_event(event)` -> Dauer in ms; spaeter: Hook in Executor.

## High-Level Usage-Fluss (geplant)
1) Daten auf Device laden: `tx = Tensor.from_host(queue, x, dtype="float32")`.
2) Modelldefinition mit Autograd-Nodes: `tape = Tape(); y = relu(matmul_op(tensor(tx, True), tensor(w, True), tape=tape))`.
3) Loss berechnen (zu ergaenzen: MSE/CrossEntropy Ops) und `tape.backward(loss)`.
4) Parameter-Update (zu ergaenzen: Optimizer-API).
5) Fuer statische Ausfuehrung: Graph aufbauen (`Graph`), Pipeline aus Ops, Executor run -> minimale Python-Interaktion.

## Profiling/Tracing & Debug
- Event-basierte Timings pro Kernel/Copy; Bandbreitenmessung; Roofline-Hinweise.
- Kernel-Stats (Auslastung, Workgroup-Groesse, Registerdruck falls verfuegbar).
- Debug-Modus: zusaetzliche Checks (NaN/Inf, Bounds, Shape/Stride-Assertions), deterministische Reduktionen.

## Testplan
- Unit-Tests:
  - Kernels gegen NumPy/Referenz: Matmul, Conv, Reduce, Softmax, LayerNorm.
  - Gradient Checks (finite differences) pro Op.
  - Memory Pool: Reuse, Fragmentation, Leak-Detection.
  - RNG: deterministische Sequenzen pro Seed/Device.
- Kernel-Generator: erzeugte Kernels aus Primitives muessen korrekt und deterministisch sein; AST/Template-Expansion Tests.
- Integrationstests:
  - Mehr-Op-Graph mit aktivierter Fusion; Ergebnisvergleich zu NumPy/PyTorch.
  - Autograd ueber kleine Netze (MLP, CNN) mit Loss; Gradients gegen PyTorch.
  - Multi-GPU: AllReduce-Korrektheit (sum/mean), Sharded Batch; deterministische Runs.
  - Overlap-Test: Compute+Copy parallel (Timing via Events).
- Performance-/Regressions-Tests:
  - Benchmarks pro Device: GEMM-GFLOPs, Conv-Throughput, Bandbreite.
  - Autotuning/Hyperstrategie: waehlt beste Config (Tiling/Partitionierung) und bleibt korrekt.
- Pipeline/Executor: Test, dass Graph-zu-Pipeline-Plan mit Buffer-Reuse erzeugt wird und zur Laufzeit minimale Python-Overhead verursacht (Timing-basierte Smoke-Tests).
- Stress-/Robustheitstests:
  - Grosse Tensors, viele kleine Kernels (Scheduler/Pool-Stabilitaet).
  - Fehlerpfade: Build-Failure, OOM -> sauberes Recovery ohne Leaks.

## Roadmap (iterativ)
1. Core: Device/Queue-Management, Memory Pool, Tensor-Basis; Definition der rudimentaeren OpenCL-Primitives.
2. Kernels: Elementwise, Reduce, Matmul (mit leichtem Autotuning) auf Basis der Primitives; dynamischer Kernel-Generator MVP.
3. Autograd: Tape + Grad-Registrierung; Grund-Ops mit Backward; Grad-Check-Tests.
4. Ops: Conv2D (im2col), Softmax, Normen; Fusion-Generator erweitert Hyperstrategie (Layout/Tiling-Auswahl).
5. Graph/Executor: Graph-Capture (ANN-Style), Buffer-Lebenszeit-Planung, Pipeline-Executor mit minimaler Python-Interaktion, Memory-Pooling-Integration.
6. Distributed: AllReduce/Broadcast (Host-Relay zuerst, spaeter direkte Pfade); dynamische Partitionierung nach Device-Profilen.
7. Profiling/Tracing + Benchmark-Suite; Ressourcenselektions-Heuristiken evaluieren.
8. Stabilisierung: Tests/Performance-Regressions, deterministische Modi, BF16/FP16-Support; Persistenz von Tuning/Hyperstrategie-Entscheidungen.

## Offene Fragen / Entscheidungen
- Mixed Precision Prioritaet: BF16 vs. FP16 Verfuegbarkeit auf Zielgeraeten?
- Autograd-Modell: nur Eager oder zusaetzlich Graph-basiert mit JIT-Fusion?
- Kommunikationspfad Multi-GPU: reicht Host-Relay oder braucht es P2P/OpenCL-Extensions?
- Zielgeraete: nur GPUs oder auch CPU/FPGA (beeinflusst Kernel-Optimierung und Workgroup-Strategie)?

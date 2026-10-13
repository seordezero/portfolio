// Goya 58: exporta el modelo de Rhino a public/goya58/model.bin para la web.
// Se ejecuta dentro de Rhino (RhinoCommon, p. ej. con el MCP execute_rhinocommon_csharp_code);
// `doc` es el RhinoDoc abierto y `output` un StringBuilder.
//
// Formato: "G58\0" + uint32 longitud de cabecera + cabecera JSON (rellena a 4 bytes) + datos.
// Por pieza: posiciones Int16 en mm (x, z, -y respecto al centro del modelo) e índices
// Uint16/Uint32. La cabecera lleva rooms (cajas por ambiente), views (vistas guardadas
// de Rhino por ambiente) e items (kind, room, code, name, color, opt, offsets).
//
// Muebles: capas 02_MOBILIARIO::<AMBIENTE>::<Bloque>. Un mueble alternativo lleva el texto
// de usuario OPTION=<id> y vive en su capa oculta; se exporta igual y la web lo muestra
// cuando se elige esa opción en data.json.
var mp = MeshingParameters.FastRenderMesh;
Func<GeometryBase, Mesh> toMesh = g => {
  Mesh r = null;
  if (g is Mesh m) r = m.DuplicateMesh();
  else if (g is Extrusion e) { var ms = Mesh.CreateFromBrep(e.ToBrep(), mp); r = new Mesh(); if (ms != null) foreach (var x in ms) r.Append(x); }
  else if (g is Brep br) { var ms = Mesh.CreateFromBrep(br, mp); r = new Mesh(); if (ms != null) foreach (var x in ms) r.Append(x); }
  else if (g is SubD sd) r = Mesh.CreateFromSubD(sd, 0);
  if (r != null) r.Faces.ConvertQuadsToTriangles();
  return r; };
// vertex clustering: Mesh.Reduce falla con las mallas importadas, esto no
Func<Mesh, double, Mesh> cluster = (m, cell) => {
  var map = new Dictionary<long, int>(); var sum = new List<Point3d>(); var cnt = new List<int>(); var idx = new int[m.Vertices.Count];
  for (int i = 0; i < m.Vertices.Count; i++) { var v = m.Vertices[i];
    long kx = (long)Math.Floor(v.X / cell) + 1000000, ky = (long)Math.Floor(v.Y / cell) + 1000000, kz = (long)Math.Floor(v.Z / cell) + 1000000;
    long key = (kx * 2000003L + ky) * 2000003L + kz;
    if (!map.TryGetValue(key, out int ni)) { ni = sum.Count; map[key] = ni; sum.Add(Point3d.Origin); cnt.Add(0); }
    idx[i] = ni; sum[ni] += (Vector3d)(Point3d)v; cnt[ni]++; }
  var r = new Mesh(); for (int i = 0; i < sum.Count; i++) r.Vertices.Add(sum[i] / cnt[i]);
  foreach (var f in m.Faces) { int a = idx[f.A], b = idx[f.B], c = idx[f.C]; if (a != b && b != c && a != c) r.Faces.AddFace(a, b, c); }
  r.Compact(); return r; };
Func<string, string> catOf = path => {
  var p = path.ToUpper();
  if (p.Contains("PISO MADERA")) return "SUELO_MADERA"; if (p.Contains("PISO CERAMICO")) return "SUELO_CERAMICO"; if (p.Contains("LOSA SUELO")) return "LOSA";
  if (p.Contains("::MUROS")) return "MURO"; if (p.Contains("A_PUERTA")) return "PUERTA"; if (p.Contains("A_MARCO")) return "MARCO";
  if (p.Contains("VENTANA")) return "VIDRIO"; if (p.Contains("A_MANILLA")) return "HERRAJE"; if (p.Contains("A_BARANDA")) return "BARANDA";
  if (p.Contains("A_ZOCALO")) return "ZOCALO"; if (p.Contains("A_ARMARIO")) return "ARMARIO"; if (p.Contains("LIBRERO")) return "LIBRERO";
  if (p.Contains("INSTALACIONES")) return "INSTALACION"; return "OTRO"; };
// las piezas de Explode vienen en coordenadas del bloque: hay que aplicarles su transformación
Func<InstanceObject, List<(Mesh m, ObjectAttributes a)>> explodeWorld = io => {
  RhinoObject[] pieces; ObjectAttributes[] at; Transform[] xf; io.Explode(true, out pieces, out at, out xf);
  var res = new List<(Mesh, ObjectAttributes)>();
  for (int k = 0; k < pieces.Length; k++) { var pm = toMesh(pieces[k].Geometry); if (pm == null) continue; pm.Transform(xf[k]); res.Add((pm, at[k])); }
  return res; };
var items = new List<(Dictionary<string, object> meta, Mesh mesh)>();
Action<Dictionary<string, object>, Mesh, int> addItem = (meta, m, cap) => {
  if (m == null || m.Faces.Count == 0) return;
  m.Vertices.CombineIdentical(true, true); m.Faces.CullDegenerateFaces(); m.Compact();
  foreach (var cell in new[] { 0.002, 0.004, 0.007, 0.011, 0.017, 0.025, 0.04 }) { if (m.Faces.Count <= cap) break; m = cluster(m, cell); }
  items.Add((meta, m)); };

// el enumerador no devuelve objetos de capas ocultas: las opciones se recogen aparte
var objs = doc.Objects.GetObjectList(new ObjectEnumeratorSettings { NormalObjects = true, LockedObjects = true, HiddenObjects = false }).ToList();
// techos y falsos techos: ocultos en Rhino, en la web salen con un botón
var ceilings = doc.Objects.GetObjectList(new ObjectEnumeratorSettings { NormalObjects = true, LockedObjects = true, HiddenObjects = true })
  .Where(o => { var fp = doc.Layers[o.Attributes.LayerIndex].FullPath; return fp.StartsWith("01_ARQ::TECHOS") || (o.IsHidden && fp.StartsWith("01_ARQ::MUROS")); }).ToList();
var ceilMesh = new Mesh(); foreach (var o in ceilings) { var pm = toMesh(o.Geometry); if (pm != null) ceilMesh.Append(pm); }
objs.RemoveAll(o => ceilings.Contains(o));
foreach (var l in doc.Layers.Where(l => !l.IsDeleted && l.FullPath.StartsWith("02_MOBILIARIO")))
  objs.AddRange(doc.Objects.FindByLayer(l).Where(o => o.Attributes.GetUserString("OPTION") != null && !objs.Contains(o)));
var archAcc = new Dictionary<string, Mesh>();
var doorParts = new Dictionary<string, (Mesh m, InstanceObject io, ObjectAttributes a)>();
foreach (var o in objs) {
  var lay = doc.Layers[o.Attributes.LayerIndex]; string opt = o.Attributes.GetUserString("OPTION");
  if (!lay.IsVisible && opt == null) continue;
  var path = lay.FullPath;
  if (path.StartsWith("02_MOBILIARIO") && o is InstanceObject io) {
    var m = new Mesh(); foreach (var p in explodeWorld(io)) m.Append(p.m);
    var c = o.Attributes.ColorSource == ObjectColorSource.ColorFromObject ? o.Attributes.ObjectColor : System.Drawing.Color.FromArgb(180, 180, 180);
    string code = o.Attributes.GetUserString("ID_CODE") ?? "";
    string name = o.Attributes.GetUserString("ID_NAME") ?? io.InstanceDefinition.Name;
    string room = path.Split(new[] { "::" }, StringSplitOptions.None)[1];
    var meta = new Dictionary<string, object> { { "kind", "mueble" }, { "room", room }, { "code", code }, { "name", name }, { "color", $"#{c.R:X2}{c.G:X2}{c.B:X2}" } };
    if (opt != null) meta["opt"] = opt;
    addItem(meta, m, 6000);
  } else if (path.StartsWith("01_ARQ")) {
    if (o is InstanceObject ai) {
      string nm = ai.Attributes.Name ?? "";
      bool door = ai.Attributes.GetUserString("DOOR_SIGN") != null, pair = ai.Attributes.GetUserString("DOOR_PAIR") != null;
      int leaf = 0;
      foreach (var p in explodeWorld(ai)) { var pl = doc.Layers[p.a.LayerIndex].FullPath; if (pl == "0") pl = path; string cat = catOf(pl);
        if (door || pair) {
          // una pieza por categoría y puerta; cada hoja corredera aparte con su vector
          string key = cat + "|" + nm + (pair ? "|" + (leaf++) : "");
          if (!doorParts.ContainsKey(key)) doorParts[key] = (new Mesh(), ai, p.a); doorParts[key].m.Append(p.m); continue; }
        string k2 = cat + "|" + cat;
        if (!archAcc.ContainsKey(k2)) archAcc[k2] = new Mesh(); archAcc[k2].Append(p.m); }
    } else { var pm = toMesh(o.Geometry); if (pm == null) continue; string cat = catOf(path); string key = cat + "|" + cat;
      if (!archAcc.ContainsKey(key)) archAcc[key] = new Mesh(); archAcc[key].Append(pm); }
  }
}
foreach (var kv in archAcc) { var parts = kv.Key.Split('|'); var meta = new Dictionary<string, object> { { "kind", "arq" }, { "cat", parts[0] }, { "name", parts[1] } };
  addItem(meta, kv.Value, 12000); }

// puertas: bisagra, sentido y ángulo (batientes) o vector de cada hoja (correderas)
foreach (var kv in doorParts) { var parts = kv.Key.Split('|'); var io = kv.Value.io; var A = io.Attributes;
  var meta = new Dictionary<string, object> { { "kind", "arq" }, { "cat", parts[0] }, { "name", parts[1] }, { "door", parts[1] },
    { "state", A.GetUserString("DOOR_STATE") ?? "closed" } };
  if (A.GetUserString("DOOR_SIGN") != null) {
    var h = io.InsertionPoint; meta["hingeR"] = new[] { h.X, h.Y, h.Z };
    meta["sign"] = int.Parse(A.GetUserString("DOOR_SIGN")); meta["angle"] = double.Parse(A.GetUserString("DOOR_ANGLE") ?? "90", System.Globalization.CultureInfo.InvariantCulture);
  } else { // Explode no trae el texto de usuario de las hojas: se lee de la definición del bloque
    var sv = io.InstanceDefinition.GetObjects()[int.Parse(parts[2])].Attributes.GetUserString("DOOR_SLIDE"); if (sv != null) { var v = sv.Split(',').Select(x => double.Parse(x, System.Globalization.CultureInfo.InvariantCulture)).ToArray();
      meta["slide"] = new[] { v[0], v[2], -v[1] }; } }
  addItem(meta, kv.Value.m, 12000); }
if (ceilMesh.Faces.Count > 0) addItem(new Dictionary<string, object> { { "kind", "arq" }, { "cat", "TECHO" }, { "name", "TECHO" } }, ceilMesh, 12000);

// ambientes: caja de la capa PINTURA de cada uno; terraza: alrededor de sus muebles
var roomIds = new Dictionary<string, string> { { "ENTRADA", "f7a8e500-ccdf-4580-bbc2-4bc3ad8a21b2" }, { "COMEDOR", "37c5ae39-eee4-4b4e-9963-f88980f8e657" },
  { "SALÓN", "7833f7c8-7185-416d-928a-ce345e751e55" }, { "ESTUDIO", "62dbd457-3be3-40ee-98be-9494f6608e05" }, { "DORMITORIO", "34cdba6e-475e-49d2-8c27-8be833337ca6" } };
var all = BoundingBox.Empty; foreach (var it in items) all.Union(it.mesh.GetBoundingBox(true));
var ctr = all.Center; ctr.Z = 0;
var IC = System.Globalization.CultureInfo.InvariantCulture;
Func<Point3d, double[]> p3 = p => new[] { p.X - ctr.X, p.Z, -(p.Y - ctr.Y) };
Func<BoundingBox, double[]> bb3 = b => new[] { b.Min.X - ctr.X, b.Min.Z, -(b.Max.Y - ctr.Y), b.Max.X - ctr.X, b.Max.Z, -(b.Min.Y - ctr.Y) };
var rooms = new Dictionary<string, object>();
foreach (var kv in roomIds) { var b = doc.Objects.FindId(new Guid(kv.Value)).Geometry.GetBoundingBox(true); b.Max = new Point3d(b.Max.X, b.Max.Y, 2.6); rooms[kv.Key] = bb3(b); }
var tb = BoundingBox.Empty; foreach (var it in items) if ((string)it.meta["kind"] == "mueble" && (string)it.meta["room"] == "TERRAZA") tb.Union(it.mesh.GetBoundingBox(true));
tb.Inflate(0.6, 0.5, 0); tb.Max = new Point3d(tb.Max.X, tb.Max.Y, 1.2); rooms["TERRAZA"] = bb3(tb);
// vistas guardadas de Rhino = cámara de cada ambiente
var viewMap = new Dictionary<string, string> { { "ENTRADA", "ENTRADA" }, { "DORMITORIO", "DORMITORIO" }, { "SALÓN", "SALÓN" }, { "DESPACHO", "ESTUDIO" }, { "COMEDOR", "COMEDOR" }, { "TERRAZA", "TERRAZA" } };
var views = new Dictionary<string, string>();
foreach (var nv in doc.NamedViews) { if (!viewMap.ContainsKey(nv.Name)) continue; var vp = nv.Viewport;
  double dA, v, h; vp.GetCameraAngles(out dA, out v, out h);   // ángulos reales del encuadre guardado
  views[viewMap[nv.Name]] = "{\"pos\":[" + string.Join(",", p3(vp.CameraLocation).Select(x => x.ToString("0.###", IC))) + "],\"target\":[" +
    string.Join(",", p3(vp.TargetPoint).Select(x => x.ToString("0.###", IC))) + "],\"lens\":" + vp.Camera35mmLensLength.ToString("0.##", IC) + ",\"hfov\":" + (2 * h * 180 / Math.PI).ToString("0.#", IC) + ",\"vfov\":" + (2 * v * 180 / Math.PI).ToString("0.#", IC) + "}"; }

// bisagras a coordenadas de la web
foreach (var it in items) if (it.meta.ContainsKey("hingeR")) { var h = (double[])it.meta["hingeR"]; it.meta.Remove("hingeR"); it.meta["hinge"] = p3(new Point3d(h[0], h[1], h[2])); }
var data = new System.IO.MemoryStream(); var bw = new System.IO.BinaryWriter(data);
var metas = new List<Dictionary<string, object>>(); int tris = 0;
foreach (var it in items) {
  var m = it.mesh; var meta = it.meta;
  while (data.Length % 4 != 0) bw.Write((byte)0);
  meta["v"] = (int)data.Length; meta["nv"] = m.Vertices.Count;
  foreach (var v in m.Vertices) { bw.Write((short)Math.Round((v.X - ctr.X) * 1000)); bw.Write((short)Math.Round(v.Z * 1000)); bw.Write((short)Math.Round(-(v.Y - ctr.Y) * 1000)); }
  while (data.Length % 4 != 0) bw.Write((byte)0);
  bool big = m.Vertices.Count > 65535; meta["i"] = (int)data.Length; meta["ni"] = m.Faces.Count * 3; meta["i32"] = big;
  foreach (var f in m.Faces) { if (big) { bw.Write(f.A); bw.Write(f.B); bw.Write(f.C); } else { bw.Write((ushort)f.A); bw.Write((ushort)f.B); bw.Write((ushort)f.C); } }
  tris += m.Faces.Count; metas.Add(meta);
}
bw.Flush();
Func<object, string> Js = v => v is string s ? "\"" + s.Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"" : v is bool b ? (b ? "true" : "false")
  : v is double[] arr ? "[" + string.Join(",", arr.Select(x => x.ToString("0.####", IC))) + "]" : Convert.ToString(v, IC);
var sbh = new System.Text.StringBuilder("{\"scale\":0.001,\"rooms\":{");
sbh.Append(string.Join(",", rooms.Select(kv => "\"" + kv.Key + "\":" + Js(kv.Value)))); sbh.Append("},\"views\":{");
sbh.Append(string.Join(",", views.Select(kv => "\"" + kv.Key + "\":" + kv.Value))); sbh.Append("},\"items\":[");
sbh.Append(string.Join(",", metas.Select(m => "{" + string.Join(",", m.Select(kv => "\"" + kv.Key + "\":" + Js(kv.Value))) + "}"))); sbh.Append("]}");
var hb = System.Text.Encoding.UTF8.GetBytes(sbh.ToString()); int hlen = (hb.Length + 3) / 4 * 4;
string file = @"D:\Website\portfolio\public\goya58\model.bin";
using (var fs = System.IO.File.Create(file)) { var w = new System.IO.BinaryWriter(fs); w.Write(System.Text.Encoding.ASCII.GetBytes("G58\0")); w.Write(hlen); w.Write(hb);
  for (int k = hb.Length; k < hlen; k++) w.Write((byte)0); w.Write(data.ToArray()); }
output.AppendLine("items " + items.Count + " tris " + tris + " bytes " + new System.IO.FileInfo(file).Length);
output.AppendLine("options: " + string.Join(", ", metas.Where(m => m.ContainsKey("opt")).Select(m => m["name"] + "=" + m["opt"])));

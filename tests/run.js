// Functional check for both variants: loads src/index.html in jsdom, takes each test through the UI, checks scoring and result codes, builds both PDFs into tests/out/.
const fs = require("fs"), path = require("path");
const { JSDOM } = require("jsdom");
const ROOT = path.resolve(__dirname, "..", process.argv[2] || "src");
let html = fs.readFileSync(path.join(ROOT, "index.html"), "utf8");
html = html.replace(/<script src="[^"]+jspdf[^"]+"><\/script>/, "");
const jspdfSrc = fs.readFileSync(require.resolve("jspdf/dist/jspdf.umd.min.js"), "utf8");
const errors = [];
const vc = new (require("jsdom").VirtualConsole)();
vc.on("jsdomError", e => { if (!/getContext/.test(e.message)) errors.push(e.message); });
const dom = new JSDOM("<!doctype html><html><head></head><body>" + html + "</body></html>", { runScripts: "outside-only", pretendToBeVisual: true, url: "https://example.test/", virtualConsole: vc });
const w = dom.window, d = w.document;
w.addEventListener("error", e => errors.push(e.message));
w.matchMedia = () => ({ matches: true, addListener(){}, removeListener(){} });
w.HTMLElement.prototype.scrollIntoView = function(){};
w.fetch = async (u) => { const buf = fs.readFileSync(path.join(ROOT, String(u))); return { ok: true, arrayBuffer: async () => buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength) }; };
w.btoa = (s) => Buffer.from(s, "binary").toString("base64");
w.eval(jspdfSrc);
[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].forEach(m => w.eval(m[1]));
const C = w.__condominiul;
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const key = (k) => d.dispatchEvent(new w.KeyboardEvent("keydown", { key: k, bubbles: true }));
async function pdf(name){
  const blob = await C.buildPdf();
  const ab = await new Promise((res, rej) => { const fr = new w.FileReader(); fr.onload = () => res(fr.result); fr.onerror = rej; fr.readAsArrayBuffer(blob); });
  fs.mkdirSync(path.join(__dirname, "out"), {recursive:true}); fs.writeFileSync(path.join(__dirname, "out", name), Buffer.from(ab));
  return ab.byteLength;
}
(async () => {
  console.log("items: complet", C.QUESTIONS.length, "alin", C.ALIN.length, "options per alin item", C.ALIN.every(q => Object.keys(q.o).length === 6));
  // --- complet
  const profile = { G: 5, M: 4, P: 4, E: 2, R: 3, V: 1 }, phaseP = { G: 3, M: 2, P: 5, E: 2, R: 2, V: 1 };
  d.getElementById("startBtn").click();
  for (let i = 0; i < 42; i++) {
    if (i === 30) { d.getElementById("part2Btn").click(); await sleep(5); }
    const q = C.QUESTIONS[i]; key(String(q.part === 1 ? profile[q.t] : phaseP[q.t])); await sleep(190);
  }
  await sleep(450);
  console.log("complet:", d.getElementById("resBase").textContent, "|", d.getElementById("resPhase").textContent, "|", d.getElementById("resCode").textContent);
  console.log("pdf complet bytes:", await pdf("complet.pdf"));
  // --- alin: prefer G > P > E > R > M > V on every item, except item 5 where V comes first
  d.getElementById("tab-alin").click();
  console.log("intro:", d.getElementById("startBtn").textContent, "|", d.getElementById("counter").textContent);
  d.getElementById("startBtn").click();
  for (let i = 0; i < 18; i++) {
    const pref = i === 4 ? ["V","G","P","E","R","M"] : ["G","P","E","R","M","V"];
    const perm = [...d.querySelectorAll("#rankList button")].map(b => b.dataset.t);
    if (i === 0) {  // deselect/renumber check
      key(String(perm.indexOf("G") + 1)); key(String(perm.indexOf("P") + 1)); key(String(perm.indexOf("G") + 1));
      console.log("after deselect:", [...d.querySelectorAll('#rankList button[aria-pressed="true"]')].map(b => b.dataset.t + b.querySelector("i").textContent).join(","), "next disabled:", d.getElementById("rankNext").disabled);
      key("Backspace");
    }
    pref.forEach(k => key(String(perm.indexOf(k) + 1)));
    key("Enter"); await sleep(5);
  }
  await sleep(450);
  const code = d.getElementById("resCode").textContent;
  console.log("alin:", d.getElementById("resBase").textContent, "|", d.getElementById("resPhase").textContent, "|", code);
  console.log("floors:", [...d.querySelectorAll(".floor")].map(f => f.getAttribute("aria-label")).join(" / "));
  const dec = C.decode(code);
  console.log("roundtrip:", dec && dec.variant, C.encode(dec) === code, "sum", Object.values(dec.base).reduce((a, b) => a + b, 0), "bad ->", C.decode(code.slice(0, -1) + (code.endsWith("0") ? "1" : "0")));
  console.log("pdf alin bytes:", await pdf("alin.pdf"));
  console.log("errors:", errors);
})().catch(e => { console.error("FAILED", e); process.exit(1); });

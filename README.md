# Condominiul Personalității

Test de personalitate în limba română, inspirat din Process Communication Model (PCM) al lui Taibi Kahler. Rezultatul e desenat ca o clădire cu șase etaje: parterul e tipul de bază, etajele de deasupra sunt celelalte cinci tipuri, în ordinea intensității.

- **Live (Claude Artifact):** https://claude.ai/artifact/QmPmg2dF7EsZgzhTg2KhV1
- **Live (GitHub Pages):** https://nylasdev.github.io/pcm-test/

## Două variante

| | Testul complet | PCM Alin |
|---|---|---|
| Întrebări | 42 de afirmații (30 bază + 12 fază) | 18 situații, câte 6 reacții |
| Răspuns | scară 1–5 | ordonezi toate cele 6 reacții |
| Scor pe tip | 0–100 | 18–108 puncte (total mereu 378) |
| Faza | da (partea a II-a) | nu |
| Durată | ~6 min | ~8 min |

**PCM Alin** reia cele 18 situații din testul original „Structura ta de personalitate”, cu formulările lui. Locurile 1–6 primesc 6, 5, 4, 3, 2, 1 puncte, adunate pe tip. La egalitate rămâne ordinea Gânditor, Perseverent, Armonizator, Visător, Rebel, Promotor, ca în original. Variantele apar în ordine aleatorie la fiecare situație.

Singura modificare față de original: la situația 9, „să pun oamenii **la ease**” a devenit „să pun oamenii **în largul lor**”. Modificarea e trecută și în `data/pcm-alin.json` (`changes`).

Ambele variante dau un cod de rezultat (13 caractere pentru testul complet, 14 cu prefix `A` pentru PCM Alin). Codul conține scorurile și o cifră de control, iar oricine îl introduce în pagină vede același rezultat. Rezultatul se descarcă și ca PDF A4 de două pagini.

## Structură

```
src/index.html        sursa paginii (formatul Claude Artifact, fără <html>/<head>)
src/fonts/, src/*.png fonturile pentru PDF și gravura templului
data/pcm-alin.json    chestionarul PCM Alin: itemi, coduri de tip, reguli de punctare
docs/                 site-ul static generat, servit de GitHub Pages
scripts/build.py      injectează data/pcm-alin.json în pagină și generează docs/
scripts/render_temple.py  randează procedural fațada templului (sursa gravurii)
tests/run.js          trece ambele teste prin interfață (jsdom), verifică scorurile și generează PDF-urile
```

## Lucru local

```bash
npm install          # jsdom + jsPDF, doar pentru teste
npm run build        # regenerează docs/ din src/ și data/
npm test             # rulează ambele variante cap-coadă, scrie tests/out/*.pdf
python3 -m http.server -d docs 8000   # deschide http://localhost:8000
```

Pagina trebuie servită prin HTTP, nu deschisă ca fișier: PDF-ul își încarcă fonturile cu `fetch()`.

## Design

Stilul vine din [hermes-mythic-design](https://github.com/NylasDev/hermes-mythic-design): pergament, cerneală caldă, serif EB Garamond, mono pentru etichete, ramă dublă de placă tipărită. Gravura cu templul hexastil (șase coloane, câte una pentru fiecare tip) e randată procedural cu `scripts/render_temple.py` și trecută prin `engrave.py` din același repo:

```bash
python3 scripts/render_temple.py temple_src.png
python3 ../hermes-mythic-design/scripts/engrave.py temple_src.png temple-bg.png --style hatch --period 7 --contrast 1.3 --background --fade-direction left --fade-strength 0.45
```

## Limite

Test neoficial. Testul complet are afirmații scrise de la zero; PCM Alin reia afirmațiile testului original. Niciunul nu e inventarul Kahler și nu înlocuiește un profil PCM făcut cu un formator certificat. Modelul are puțină validare independentă publicată; folosește rezultatul ca profil orientativ al preferințelor declarate, nu ca diagnostic sau pentru decizii de angajare. Process Communication Model® este marcă înregistrată Kahler Communications.

## Licențe

- Cod: MIT, vezi `LICENSE`.
- Fonturi (subseturi, în `src/fonts/`): EB Garamond și IBM Plex Mono, SIL Open Font License 1.1, vezi `licenses/`. Subsetul mono e redenumit „Condominiul Mono”, pentru că „Plex” e nume rezervat.
- Afirmațiile PCM Alin provin din testul original „Structura ta de personalitate” și nu sunt acoperite de licența MIT.

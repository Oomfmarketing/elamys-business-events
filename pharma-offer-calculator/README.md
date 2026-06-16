# Elämys Internal Tools

Vercel-projekti jossa salasanasuojattu työkalupakki.

## Setup

1. Tämä kansio on valmis pushattavaksi uuteen GitHub-repoon
2. Vercel-projekti: New Project → Import this repo → Root Directory `.` → Deploy
3. URL: `<project>.vercel.app` · Salasana: `Menestys2026!`

## Uuden työkalun lisääminen

1. Tee oma HTML-tiedosto (yksi tiedosto sisältää CSS+JS+data)
2. Aja:
   ```bash
   python encrypt-tool.py oma-tyokalu.html slug "Otsikko" "Kuvaus"
   ```
3. Skripti generoi `tools/slug.html`
4. Päivitä `index.html`:n picker manuaalisesti (lisää uusi tool-kortti) tai aja `init-vercel-project.py` uudelleen päivitetyllä TOOLS-listalla
5. `git push` → Vercel deployaa

## Salasanan vaihto

Salasana ei ole rajattu mihinkään yhteen tiedostoon — se on käytössä useissa salatuissa palasissa.
Salasanan vaihtamiseksi:
1. Säädä `init-vercel-project.py`:n `PASSWORD`-arvoa
2. Aja skripti uudelleen → ylikirjoittaa `index.html`:n ja `encrypt-tool.py`:n uudella salasanalla
3. Salaa jokainen `tools/*.html` uudelleen samalla salasanalla (aja `encrypt-tool.py` jokaiselle plain-source-tiedostolle)

## Tiedostot

- `index.html` — login + tool picker (sisältää salasana-canaryn)
- `vercel.json` — clean URLs päälle
- `tools/*.html` — salatut työkalut
- `encrypt-tool.py` — apuväline uusien työkalujen lisäämiseen
- `README.md` — tämä tiedosto

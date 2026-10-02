// Saves a backup copy of the Comandator menu to menu-data.json.
// The website loads the menu live from Comandator and falls back to this copy if that fails.
// Run by .github/workflows/update-menu.yml; exits with an error if Comandator's response
// no longer looks like a menu, so the workflow fails and GitHub emails the repo owner.
import { readFile, writeFile } from 'node:fs/promises';

const SLUG = 'capricho-de-costa-del-silencio-tenerife-arona';
const URL = 'https://comandator.com/trpc/establishmentsRouter.getEstablishmentBySlug?input=' +
  encodeURIComponent(JSON.stringify({ slugName: SLUG, language: 'es' }));
const OUT = new globalThis.URL('../menu-data.json', import.meta.url);

const res = await fetch(URL, { headers: { accept: 'application/json' } });
if (!res.ok) throw new Error(`Comandator answered HTTP ${res.status}`);
const data = await res.json();

const menus = data?.result?.data?.menus;
if (!Array.isArray(menus)) throw new Error('Unexpected response: no menus found');

const sections = menus.filter(m => !m.disabled).flatMap(m => m.sections || []).map(sec => ({
  name: sec.name,
  sortOrder: sec.sortOrder,
  disabled: !!sec.disabled,
  isForAdmins: !!sec.isForAdmins,
  items: (sec.items || []).map(i => ({
    name: i.name,
    price: i.price,
    description: i.description || '',
    status: i.status,
    sortOrder: i.sortOrder,
  })),
}));

const cartaItems = sections
  .filter(s => /^\s*carta\s*-/i.test(s.name))
  .flatMap(s => s.items)
  .filter(i => typeof i.name === 'string' && typeof i.price === 'number');
if (!cartaItems.length) throw new Error('Unexpected response: no "Carta - " sections with items');

// Only rewrite the file when the menu itself changed, so the timestamp alone doesn't create commits.
let previous = null;
try { previous = JSON.parse(await readFile(OUT, 'utf8')); } catch {}
if (previous && JSON.stringify(previous.sections) === JSON.stringify(sections)) {
  console.log('Menu unchanged.');
} else {
  await writeFile(OUT, JSON.stringify({ updatedAt: new Date().toISOString(), sections }, null, 1) + '\n');
  console.log(`Menu saved: ${sections.length} sections, ${cartaItems.length} "Carta" items.`);
}

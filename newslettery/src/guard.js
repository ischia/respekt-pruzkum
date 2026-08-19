/**
 * Čtecí pojistka pro přístup do maileru.
 *
 * V mailer UI je mazací ikona hned vedle ikony statistik, takže sběrač nikdy
 * neklikáme – navigujeme přes URL a každý požadavek ještě projde tímhle filtrem:
 *   • cokoli jiného než GET projde jen při jediném přihlášení,
 *   • Nette signály (`?do=…`) jsou zakázané vždy (mazání je právě signál),
 *   • cesty se slovy delete/duplicate/import/unsubscribe… jsou zakázané taky.
 */

export const MAILER_BASE = process.env.MAILER_BASE_URL ?? "https://mailer.respekt.cz";

const DESTRUCTIVE = /(delete|destroy|remove|drop|purge|duplicate|import|unsubscribe|subscribe)/i;
const NETTE_SIGNAL = /[?&]do=/i;

export function isAllowedRequest({ url, method }, { loginAllowed = false, base = MAILER_BASE } = {}) {
  const isMailer = url.startsWith(base);
  const isSignIn = url.startsWith(`${base}/mailer/sign/`);

  if (method !== "GET") return Boolean(loginAllowed && isSignIn);
  if (!isMailer) return true; // statické assety z CDN apod.
  if (NETTE_SIGNAL.test(url)) return false;
  return !DESTRUCTIVE.test(url.slice(base.length));
}

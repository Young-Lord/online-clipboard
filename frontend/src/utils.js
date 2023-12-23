export function getKeyByValue(object, value) {
  return Object.keys(object).find((key) => object[key] === value);
}

export function replaceLastPartOfUrl(href, new_part) {
  // replaceLastPartOfUrl("https://a.com/a/old?aa=1&dd=3#hash", "new") -> "https://a.com/a/new?aa=1&dd=3#hash"
  let url = new URL(href);
  const segments = url.pathname.split("/");
  segments.pop();
  segments.push(new_part);
  url.pathname = segments.join("/");
  return url.href;
}

/** hash a string
 * @param {string} str
 * @returns {string}
 */
function hash(str) {
  let i,
    l,
    hval = 0x811c9dc5;
  for (i = 0, l = str.length; i < l; i++) {
    hval ^= str.charCodeAt(i);
    hval +=
      (hval << 1) + (hval << 4) + (hval << 7) + (hval << 8) + (hval << 24);
  }
  return ("0000000" + (hval >>> 0).toString(16)).substr(-8);
}

if (typeof exports !== "undefined") {
  exports.hash = hash;
}

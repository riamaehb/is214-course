// Detect whether the page is inside an iframe (for example a Moodle assignment).
// Embedded: the navigation buttons stay hidden and links open in a new tab, so the frame never navigates away.
(function () {
  var top = true;
  try { top = (window.self === window.top); } catch (e) { top = false; }
  if (top) {
    document.body.classList.add('standalone');
  } else {
    var links = document.querySelectorAll('a[href]');
    for (var i = 0; i < links.length; i++) {
      links[i].setAttribute('target', '_blank');
      links[i].setAttribute('rel', 'noopener');
    }
  }
})();

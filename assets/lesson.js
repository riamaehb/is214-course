
(function(){
  var slides = Array.prototype.slice.call(document.querySelectorAll('.slide'));
  var total = slides.length;
  var idx = 0;
  var prevBtn = document.getElementById('prevBtn');
  var nextBtn = document.getElementById('nextBtn');
  var curNum = document.getElementById('curNum');
  var totalNum = document.getElementById('totalNum');
  var progressFill = document.getElementById('progressFill');
  var endNote = document.getElementById('endNote');
  totalNum.textContent = total;

  function render(){
    slides.forEach(function(s, i){ s.classList.toggle('active', i === idx); });
    curNum.textContent = idx + 1;
    progressFill.style.width = ((idx + 1) / total * 100) + '%';
    prevBtn.disabled = (idx === 0);
    nextBtn.textContent = (idx === total - 1) ? 'Finish' : 'Next →';
    endNote.style.display = 'none';
    document.querySelector('.wrap').scrollTop = 0;
  }
  prevBtn.addEventListener('click', function(){
    if(idx > 0){ idx--; render(); }
  });
  nextBtn.addEventListener('click', function(){
    if(idx < total - 1){ idx++; render(); }
    else { endNote.style.display = 'block'; endNote.scrollIntoView({behavior:'smooth'}); }
  });
  document.addEventListener('keydown', function(e){
    if(e.key === 'ArrowRight') nextBtn.click();
    if(e.key === 'ArrowLeft') prevBtn.click();
  });
  render();
})();

document.querySelectorAll('.check:not(.open)').forEach(function(check){
  var correctIdx = parseInt(check.dataset.answer, 10);
  var rows = check.querySelectorAll('.opt-row');
  var fb = check.querySelector('.fb');
  rows.forEach(function(row, idx){
    var btn = row.querySelector('.opt');
    var explanation = row.querySelector('.opt-fb');
    btn.addEventListener('click', function(){
      rows.forEach(function(r){ r.querySelector('.opt').classList.remove('correct','wrong'); });
      if(idx === correctIdx){
        btn.classList.add('correct');
      } else {
        btn.classList.add('wrong');
        rows[correctIdx].querySelector('.opt').classList.add('correct');
      }
      fb.innerHTML = explanation ? explanation.innerHTML : '';
    });
  });
});
document.querySelectorAll('.reveal-btn').forEach(function(btn){
  btn.addEventListener('click', function(){
    var content = btn.nextElementSibling;
    content.classList.toggle('show');
    btn.textContent = content.classList.contains('show') ? 'Hide answer' : btn.textContent.replace('Hide','Reveal');
  });
});

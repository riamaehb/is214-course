"use strict";
const $ = id => document.getElementById(id);
const ids = ["languageName","printKeyword","addKeyword","subKeyword","mulKeyword","divKeyword","startKeyword","endKeyword","reflection"];
const getRadio = name => document.querySelector(`input[name="${name}"]:checked`)?.value ?? null;
const get = () => ({
  schema_version:"1.0", language_name:$("languageName").value.trim(), notation:getRadio("notation"),
  keywords:{print:$("printKeyword").value.trim(),add:$("addKeyword").value.trim(),sub:$("subKeyword").value.trim(),mul:$("mulKeyword").value.trim(),div:$("divKeyword").value.trim()},
  statement_terminator:getRadio("terminator"),case_sensitive:getRadio("caseChoice")==="yes"?true:getRadio("caseChoice")==="no"?false:null,
  program_boundaries:getRadio("boundariesChoice")==="yes"?{enabled:true,start:$("startKeyword").value.trim(),end:$("endKeyword").value.trim()}:getRadio("boundariesChoice")==="no"?{enabled:false}:null,
  design_reflection:$("reflection").value.trim()
});
function validate(s){
  const errors=[];
  if(!/^[A-Za-z][A-Za-z0-9_]{0,39}$/.test(s.language_name))errors.push("Language name must start with an ASCII letter, contain only letters, digits, or underscores, and be at most 40 characters.");
  if(!s.notation)errors.push("Choose an expression notation.");
  if(!s.statement_terminator)errors.push("Choose a statement terminator.");
  if(s.case_sensitive===null)errors.push("Choose whether keywords are case-sensitive.");
  if(s.program_boundaries===null)errors.push("Choose whether your language requires program boundaries.");
  const words={...s.keywords};
  if(s.program_boundaries?.enabled){words.start=s.program_boundaries.start;words.end=s.program_boundaries.end;}
  for(const [kind,word] of Object.entries(words))if(!/^[A-Za-z][A-Za-z0-9_]*$/.test(word))errors.push(`${kind.toUpperCase()} keyword must start with a letter and contain only ASCII letters, digits, or underscores.`);
  const normalized=Object.values(words).map(w=>w.toUpperCase());
  if(new Set(normalized).size!==normalized.length)errors.push("Every keyword must be different, even when the letter case differs.");
  if(s.design_reflection.length<20)errors.push("Write a reflection of at least 20 characters.");
  return errors;
}
function makeProgram(s){
  const k=s.keywords,fn=s.notation==="function";
  const sum=fn?`${k.add}(2, 3)`:`(${k.add} 2 3)`;
  const product=fn?`${k.mul}(${k.add}(2, 3), 4)`:`(${k.mul} (${k.add} 2 3) 4)`;
  const end=s.statement_terminator==="semicolon"?";":"";
  const statements=[`${k.print} ${sum}${end}`,`${k.print} ${product}${end}`];
  return [ ...(s.program_boundaries?.enabled?[s.program_boundaries.start]:[]),...statements,...(s.program_boundaries?.enabled?[s.program_boundaries.end]:[])].join("\n");
}
function render(){
  $("boundaryFields").classList.toggle("hidden",getRadio("boundariesChoice")!=="yes");
  const spec=get(),errors=validate(spec);
  $("previewName").textContent=spec.language_name||"Your language";
  const previewReady=Boolean(spec.language_name && spec.notation && spec.statement_terminator && spec.case_sensitive!==null && spec.program_boundaries!==null && Object.values(spec.keywords).every(Boolean) && (!spec.program_boundaries?.enabled || (spec.program_boundaries.start && spec.program_boundaries.end)));
  $("programPreview").textContent=previewReady?makeProgram(spec):"Make all your choices to see a sample program.";
  $("sampleNote").textContent=previewReady?"This program produces 5 and then 20.":"";
  $("jsonPreview").textContent=JSON.stringify(spec,null,2);
  $("previewState").textContent=errors.length?"Incomplete":"Valid";
  $("previewState").classList.toggle("invalid",!!errors.length);
  $("validation").className=`validation ${errors.length?"bad":"ok"}`;
  if(errors.length){
    const heading=document.createElement("strong");heading.textContent="To finish:";
    const ul=document.createElement("ul");for(const err of errors){const li=document.createElement("li");li.textContent=err;ul.append(li);}
    $("validation").replaceChildren(heading,ul);
  }else{$("validation").textContent="All choices are valid. You can download your file.";}
  $("download").disabled=!!errors.length;
  $("actionStatus").textContent="";
}
function json(){return JSON.stringify(get(),null,2)+"\n";}
$("download").addEventListener("click",()=>{
  if(validate(get()).length)return;
  const url=URL.createObjectURL(new Blob([json()],{type:"application/json"}));
  const link=document.createElement("a");link.href=url;link.download="language.json";document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
  $("actionStatus").textContent="language.json downloaded. Rename it as described under Submission, and keep a copy named language.json.";
});
for(const id of ids){$(id).addEventListener("input",render);$(id).addEventListener("change",render);}
for(const el of document.querySelectorAll('input[type="radio"]'))el.addEventListener("change",render);
render();

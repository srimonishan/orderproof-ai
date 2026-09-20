(() => {
'use strict';
const script=document.currentScript,site=script?.dataset.site;
if(!script||!site||!(/^[a-f0-9]{24}$/.test(site)||site==='demo')||window.OrderProof)return;
const origin=new URL(script.src).origin,host=document.createElement('div');host.id='orderproof-widget';document.body.appendChild(host);
const shadow=host.attachShadow({mode:'closed'}),style=document.createElement('link');style.rel='stylesheet';style.href=origin+'/embed.css';
const button=document.createElement('button');button.type='button';button.textContent='Chat with us';button.setAttribute('aria-expanded','false');button.setAttribute('aria-controls','support-frame');
const frame=document.createElement('iframe');frame.id='support-frame';frame.title='Customer support conversation';frame.hidden=true;frame.referrerPolicy='strict-origin-when-cross-origin';
frame.setAttribute('sandbox','allow-scripts allow-same-origin allow-downloads allow-popups allow-popups-to-escape-sandbox');
const setOpen=open=>{if(open&&!frame.src)frame.src=origin+(site==='demo'?'/widget-demo':'/widget/'+site);frame.hidden=!open;button.textContent=open?'Close chat':'Chat with us';button.setAttribute('aria-expanded',String(open));if(open)frame.focus();else button.focus()};
button.addEventListener('click',()=>setOpen(frame.hidden));shadow.append(style,frame,button);
window.OrderProof={open:()=>setOpen(true),close:()=>setOpen(false),destroy:()=>{host.remove();delete window.OrderProof}};
})();

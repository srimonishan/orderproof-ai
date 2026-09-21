const {chromium}=require('playwright');
const AxeBuilder=require('@axe-core/playwright').default;
const assert=require('node:assert/strict');
(async()=>{
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
try {
const page=await browser.newPage({viewport:{width:390,height:844}});
const base=process.env.ORDERPROOF_URL||'http://127.0.0.1:8080';
const cid='a'.repeat(24), site='b'.repeat(24); let feedback=null, attempts=0;
await page.route('**/public/support/**',async route=>{
 const url=route.request().url(); let body;
 if(url.endsWith('/feedback')) {attempts++;body=route.request().postDataJSON();assert.deepEqual(body,{resolution:'partly',rating:3,comment:'A person helped.'});if(attempts===1)return route.fulfill({status:503,json:{error:'Please retry.'}});feedback=body;}
 else if(url.includes('/sites/'))body={name:'Test business',greeting:'Hello',color:'#245e4c'};
 else body={id:cid,status:'closed',mode:'human',seq:1,messages:[{role:'system',content:'Closed',at:new Date().toISOString()}],feedback};
 await route.fulfill({json:body});
});
await page.route('**/widget/'+site,async route=>{const response=await page.request.get(base+'/widget-demo');await route.fulfill({response});});
await page.addInitScript(({cid,site})=>sessionStorage.setItem('orderproof:'+site,JSON.stringify({id:cid,token:'test-token'})),{cid,site});
await page.goto(base+'/widget/'+site);
await page.getByLabel('Was your issue resolved?').selectOption('partly');
await page.getByLabel('How helpful was this support?').selectOption('3');
await page.getByLabel('Comment (optional)').fill('A person helped.');
assert.equal((await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa']).analyze()).violations.length,0);
await page.getByRole('button',{name:'Send feedback'}).click();
await page.getByRole('alert').waitFor();
assert.equal(await page.getByLabel('Comment (optional)').inputValue(),'A person helped.');
await page.getByRole('button',{name:'Send feedback'}).click();
await page.getByRole('heading',{name:'Thank you for your feedback'}).waitFor();
await page.reload();await page.getByRole('heading',{name:'Thank you for your feedback'}).waitFor();
assert.equal(await page.getByRole('button',{name:'Download record'}).count(),1);
await page.getByRole('button',{name:'Start a new conversation'}).click();
await page.getByRole('heading',{name:'How can we help?'}).waitFor();
console.log('Feedback mobile accessibility, retry, persistence, and optional flow passed (mock API).');
} finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});

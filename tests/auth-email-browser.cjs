const {chromium}=require('playwright');
const AxeBuilder=require('@axe-core/playwright').default;
const assert=require('node:assert/strict');
(async()=>{
const browser=await chromium.launch({executablePath:process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE||(require('node:fs').existsSync('/usr/bin/chromium')?'/usr/bin/chromium':undefined),headless:true,args:['--no-sandbox']});
const context=await browser.newContext({viewport:{width:1280,height:900}});const page=await context.newPage();page.setDefaultTimeout(20000);page.setDefaultNavigationTimeout(30000);const errors=[];page.on('pageerror',e=>errors.push(e.message));
const base=process.env.ORDERPROOF_URL||'http://127.0.0.1:8080';
await page.route('**/config',r=>r.fulfill({json:{region:'us-east-1',clientId:'mock-client',poolId:'mock-pool',emailConfigured:false}}));
let failCode=true,confirmed=false;
await page.route('https://cognito-idp.us-east-1.amazonaws.com/**',async r=>{const action=r.request().headers()['x-amz-target'].split('.').pop();let body={};let status=200;
if(action==='SignUp'||action==='ResendConfirmationCode'||action==='ForgotPassword')body={UserConfirmed:false,CodeDeliveryDetails:{Destination:'v***@e***',DeliveryMedium:'EMAIL'}};
if(action==='ConfirmSignUp'&&failCode){status=400;body={__type:'CodeMismatchException',message:'The verification code is incorrect. Please use the newest code.'};failCode=false}else if(action==='ConfirmSignUp')confirmed=true;
await r.fulfill({status,json:body});});
async function axe(label){console.log("Checking "+label);const result=await new AxeBuilder({page}).exclude('iframe').withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();assert.deepEqual(result.violations.map(x=>({id:x.id,nodes:x.nodes.map(n=>n.target)})),[],label)}
await page.goto(base);await page.locator('nav [data-action="register"]').click();await page.getByLabel('Email address').fill('visitor@example.invalid');await page.getByLabel('Password',{exact:true}).fill('Fictional123!Password');await page.getByRole('button',{name:'Create your account'}).click();await page.getByRole('heading',{name:'Check your inbox.'}).waitFor();await page.getByText('AWS accepted a code request for v***@e***.',{exact:false}).waitFor();await axe('verification screen');await page.reload();await page.getByRole('heading',{name:'Check your inbox.'}).waitFor();assert.equal(await page.getByLabel('Email address').inputValue(),'visitor@example.invalid');await page.getByLabel('Verification code').fill('123456');await page.getByRole('button',{name:'Verify email'}).click();await page.getByRole('alert').filter({hasText:'incorrect'}).waitFor();await page.getByRole('button',{name:'Verify email'}).click();await page.getByRole('heading',{name:'Welcome back.'}).waitFor();assert(confirmed);assert.equal(await page.evaluate(()=>sessionStorage.getItem('orderproof-pending-auth')),null);
await page.getByRole('button',{name:'Forgot password?'}).click();await page.getByRole('button',{name:'Send reset code'}).click();await page.getByRole('heading',{name:'Choose a new password.'}).waitFor();await axe('password reset');
await page.goto(base+'/email-preview');await page.getByRole('heading',{name:'Thoughtful emails. A familiar experience.'}).waitFor();await axe('email gallery');await page.screenshot({path:'/tmp/orderproof-email-gallery.png',fullPage:true});
for(const kind of ['verification','welcome','handoff','closed']){await page.goto(base+'/email-'+kind+'.html');await axe('email '+kind);await page.setViewportSize({width:390,height:844});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'email mobile overflow: '+kind);await page.screenshot({path:'/tmp/orderproof-email-'+kind+'.png',fullPage:true});await page.setViewportSize({width:1280,height:900});}
assert.deepEqual(errors,[]);await browser.close();console.log('Mocked signup/reset flows, pending-code recovery, email previews, and accessibility passed. No email sent by browser tests.');
})().catch(e=>{console.error(e);process.exit(1)});

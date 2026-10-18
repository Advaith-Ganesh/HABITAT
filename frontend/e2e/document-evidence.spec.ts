import { test, expect } from "@playwright/test";
import { fileURLToPath } from "node:url";
const fixture=(name:string)=>fileURLToPath(new URL(`../../evidence_benchmark/${name}`,import.meta.url));
async function evidenceStep(page:any){
  await page.goto('/#applicant/Apply%20for%20Housing');
  await page.getByRole('button',{name:'Continue',exact:true}).click();
  await page.getByRole('combobox',{name:'Do you have somewhere safe to stay tonight?',exact:true}).selectOption('no');
  await expect(page.getByText(/Contact your local council/)).toBeVisible();
  await page.getByRole('button',{name:'Continue',exact:true}).click();
  await page.getByRole('combobox',{name:'Income evidence available',exact:true}).selectOption('help');
  await page.getByRole('combobox',{name:'Identity evidence available',exact:true}).selectOption('missing');
  await page.getByRole('checkbox',{name:'I confirm these PDFs contain only synthetic information.',exact:true}).check();
}
async function submit(page:any){
  await page.getByRole('button',{name:'Continue',exact:true}).click();
  await page.getByRole('button',{name:'Continue',exact:true}).click();
  await page.getByRole('checkbox',{name:'I confirm all values are synthetic.',exact:true}).check();
  await page.getByRole('button',{name:'Submit application',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Your application',exact:true})).toBeVisible();
  return await page.locator('.reference').innerText();
}

test('Real PDF upload, grounded findings, five evidence actions and applicant tracking',async({page,request})=>{
  await evidenceStep(page);
  await page.getByLabel('Synthetic PDF file',{exact:true}).setInputFiles(fixture('dev/dev-income.pdf'));
  await page.getByRole('button',{name:'Analyse uploaded PDF',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Extracted; awaiting human verification',exact:true})).toBeVisible();
  await expect(page.getByText('Employer: SIM-ORG-1',{exact:true})).toBeVisible();
  await page.screenshot({path:'../docs/screenshots/responsible-pdf-upload.png',fullPage:true});
  const id=await submit(page);
  let row=await(await request.get('/api/applications/'+id)).json();
  expect(row.payload.evidence_ids).toHaveLength(1);
  expect(row.payload.income_document_available).toBe(0); // upload never changes declarations
  expect(row.payload.evidence_help_needed).toEqual(['income']);
  await page.getByRole('button',{name:'Switch to administrator',exact:true}).click();
  await page.getByRole('textbox',{name:'Search cases',exact:true}).fill(id);
  await page.getByRole('button',{name:`Open ${id}`,exact:true}).click();
  await page.getByRole('button',{name:'Open AI assessment',exact:true}).click();
  await page.getByRole('button',{name:'Run AI Assessment',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Assessment unavailable',exact:true})).toBeVisible();
  for(const action of ['confirm','correct','insufficient','request_clarification','escalate']){
    await page.getByRole('combobox',{name:'Evidence review action',exact:true}).selectOption(action);
    if(action==='correct')await page.getByRole('textbox',{name:'Corrected observation',exact:true}).fill('SIM-ORG-CORRECTION');
    await page.getByRole('textbox',{name:'Evidence review reason',exact:true}).fill('Synthetic source reviewed; this confirms an observation only, not document authenticity.');
    const savedResponse=page.waitForResponse(r=>r.url().endsWith('/review') && r.request().method()==='POST');
    await page.getByRole('button',{name:'Save evidence review',exact:true}).click();
    expect((await savedResponse).status()).toBe(200);
    await expect(page.getByText('Recorded evidence reviews',{exact:true})).toBeVisible();
    const saved=await(await request.get(`/api/applications/${id}/evidence`)).json();
    expect(saved[0].reviews.at(-1).action).toBe(action);
  }
  await page.screenshot({path:'../docs/screenshots/responsible-evidence-review.png',fullPage:true});
  await page.getByRole('button',{name:'Continue to human review',exact:true}).click();
  await page.getByRole('combobox',{name:'Review action',exact:true}).selectOption('request_evidence');
  await page.getByRole('textbox',{name:'Reviewer notes & mandatory reason',exact:true}).fill('Offer document assistance and clarify the immediate housing-support concern; no housing decision.');
  await page.getByRole('button',{name:'Record review action',exact:true}).click();
  await page.getByRole('button',{name:'Confirm review action',exact:true}).click();
  await page.getByRole('button',{name:'Switch to applicant',exact:true}).click();
  await page.reload();
  await expect(page.getByText('A caseworker has requested more information',{exact:true})).toBeVisible();
  await expect(page.getByText('Recorded evidence reviews',{exact:true})).toBeVisible();
  row=await(await request.get('/api/applications/'+id)).json();
  expect(row.history).toHaveLength(8);
  expect(row.assessment.score).toBeNull();
});

test('Unreadable PDF and injected instructions abstain honestly',async({page})=>{
  await evidenceStep(page);
  await page.getByLabel('Synthetic PDF file',{exact:true}).setInputFiles(fixture('dev/dev-blank.pdf'));
  await page.getByRole('button',{name:'Analyse uploaded PDF',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Insufficient readable evidence',exact:true})).toBeVisible();
  await page.getByLabel('Synthetic PDF file',{exact:true}).setInputFiles(fixture('dev/dev-injection.pdf'));
  await page.getByRole('button',{name:'Analyse uploaded PDF',exact:true}).click();
  await expect(page.getByText(/Requires human handling: prompt injection/)).toBeVisible();
  await page.screenshot({path:'../docs/screenshots/responsible-document-handoff.png',fullPage:true});
  await submit(page);
});

test('Rejected PDF does not block an application without evidence',async({page})=>{
  await evidenceStep(page);
  await page.getByLabel('Synthetic PDF file',{exact:true}).setInputFiles(fixture('security/encrypted.pdf'));
  await page.getByRole('button',{name:'Analyse uploaded PDF',exact:true}).click();
  await expect(page.getByRole('alert')).toContainText('PDF rejected');
  await submit(page);
});

import { useEffect, useState } from "react";
import { api, analysePdf } from "../lib/api";
import { type Json, humanize } from "../lib/types";

function Findings({ document }: {document: Json}) {
  const a=document.analysis;
  return <div className="documents">
    <h3>{a.status}</h3>
    <p className="field-hint">Document {document.id} · {a.mode} · {a.processing_ms.toFixed(1)} ms</p>
    <p>Claimed: {a.claimed_category}. Detected: {a.detected_category}. Readable: {a.readable ? "Yes" : "No"}. Automated conclusion withheld: {a.abstained ? "Yes" : "No issues detected by these limited rules"}.</p>
    <p>Human verification: {document.reviews.length ? "See recorded, scoped review actions below" : "Not reviewed"}. Authenticity and identity are not established.</p>
    {a.issues.length > 0 && <p className="warning">Requires human handling: {a.issues.map(humanize).join(", ")}. {a.missing_fields.length > 0 && `Missing fields: ${a.missing_fields.map(humanize).join(", ")}.`}</p>}
    {a.observations.map((o: Json)=><div className="callout" key={o.id}><b>{humanize(o.field)}: {o.value}</b><p>Page {o.page}: <q>{o.excerpt}</q></p><small>{o.status}</small></div>)}
    <details><summary>Actual extracted text by page</summary>{a.pages.map((p: Json)=><div key={p.page}><h4>Page {p.page}</h4><p style={{whiteSpace:"pre-wrap",overflowWrap:"anywhere"}}>{p.text || "No readable text extracted. OCR is not implemented."}</p></div>)}</details>
    {!!document.reviews.length && <details open><summary>Recorded evidence reviews</summary>{document.reviews.map((r: Json)=><p key={r.timestamp}><b>{humanize(r.action)}</b>{r.observation_id && ` · ${r.observation_id}`}{r.corrected_value && ` → ${r.corrected_value}`} · {r.reason}<br/><small>{r.timestamp} · {r.scope}</small></p>)}</details>}
  </div>;
}

export function EvidenceUpload({ids,onChange}:{ids:string[];onChange:(ids:string[])=>void}) {
  const [category,setCategory]=useState("income"),[synthetic,setSynthetic]=useState(false),[file,setFile]=useState<File>(),[busy,setBusy]=useState(false),[error,setError]=useState(""),[documents,setDocuments]=useState<Json[]>([]);
  const key=JSON.stringify(ids);
  useEffect(()=>{let ignore=false;Promise.all((JSON.parse(key) as string[]).map(id=>api(`/api/evidence/${id}`))).then(rows=>{if(!ignore)setDocuments(rows);}).catch(e=>{if(!ignore)setError(String(e));});return()=>{ignore=true;};},[key]);
  async function analyse(example=false) {
    if(!synthetic || busy || ids.length>=3 || (!file && !example)) return;
    setBusy(true);setError("");
    try {
      let data:Blob;
      if(example){const response=await fetch(`/api/evidence-fixtures/dev-${category}`);if(!response.ok)throw new Error("Synthetic fixture unavailable");data=await response.blob();}
      else data=file!;
      if(data.size>2*1024*1024)throw new Error("PDF exceeds 2 MiB limit");
      const result=await analysePdf(data,category);setDocuments(previous=>[...previous,result]);onChange([...ids,result.id]);
    } catch(e){setError(String(e));} finally{setBusy(false);}
  }
  return <section aria-label="Optional synthetic PDF evidence">
    <h3>Optional synthetic PDF evidence</h3>
    <p>Use only project-marked synthetic documents. Never upload real ID, bank statements, tenancy documents or payslips. You can submit without a PDF. Uploads do not change your evidence declarations or the Random Forest inputs.</p>
    <p className="field-hint">Local analysis only; no API key, cloud inference, OCR or authenticity check. Maximum 3 PDFs, 2 MiB and 5 pages each. Raw files are discarded after processing; extracted text remains in local SQLite for review.</p>
    <label className="checkbox"><input type="checkbox" checked={synthetic} onChange={e=>setSynthetic(e.target.checked)}/>I confirm these PDFs contain only synthetic information.</label>
    <label>Claimed PDF evidence category<select aria-label="Claimed PDF evidence category" value={category} onChange={e=>setCategory(e.target.value)}>{["income","identity","housing"].map(c=><option key={c}>{c}</option>)}</select></label>
    <label>Synthetic PDF file<input aria-label="Synthetic PDF file" type="file" accept="application/pdf,.pdf" onChange={e=>setFile(e.target.files?.[0])}/></label>
    <button type="button" className="secondary" disabled={!synthetic || !file || busy || ids.length>=3} onClick={()=>void analyse()}>{busy ? "Processing actual PDF…" : "Analyse uploaded PDF"}</button>{" "}
    <button type="button" className="secondary" disabled={!synthetic || busy || ids.length>=3} onClick={()=>void analyse(true)}>Analyse bundled synthetic example</button>
    <p><a href={`/api/evidence-fixtures/dev-${category}`} download>Download marked synthetic {category} PDF</a></p>
    {error && <p className="warning" role="alert">{error} Missing documents never block submission.</p>}
    {documents.map(d=><Findings key={d.id} document={d}/>)}
  </section>;
}

function ReviewDocument({document,onSaved}:{document:Json;onSaved:()=>void}) {
  const [action,setAction]=useState("confirm"),[observation,setObservation]=useState(document.analysis.observations[0]?.id ?? ""),[correction,setCorrection]=useState(""),[reason,setReason]=useState(""),[busy,setBusy]=useState(false),[error,setError]=useState("");
  async function save(){setBusy(true);setError("");try{await api(`/api/evidence/${document.id}/review`,{action,observation_id:["confirm","correct"].includes(action) ? observation : null,corrected_value:action==="correct" ? correction : null,reason});setReason("");onSaved();}catch(e){setError(String(e));}finally{setBusy(false);}}
  return <div className="callout">
    <h4>Human evidence review</h4><p>Confirm text observations only. This does not authenticate a document, verify identity or decide housing entitlement. Use synthetic notes only.</p>
    <label>Evidence review action<select aria-label="Evidence review action" value={action} onChange={e=>setAction(e.target.value)}>{["confirm","correct","insufficient","request_clarification","escalate"].map(a=><option key={a} value={a}>{humanize(a)}</option>)}</select></label>
    {["confirm","correct"].includes(action) && <label>Specific observation<select aria-label="Specific observation" value={observation} onChange={e=>setObservation(e.target.value)}><option value="">Choose an observation</option>{document.analysis.observations.map((o:Json)=><option key={o.id} value={o.id}>{humanize(o.field)} · page {o.page}: {o.value}</option>)}</select></label>}
    {action==="correct" && <label>Corrected observation<input aria-label="Corrected observation" value={correction} maxLength={300} onChange={e=>setCorrection(e.target.value)}/></label>}
    <label>Evidence review reason<textarea aria-label="Evidence review reason" value={reason} maxLength={1000} onChange={e=>setReason(e.target.value)}/></label>
    <button type="button" className="primary" disabled={busy || reason.trim().length<8 || (["confirm","correct"].includes(action) && !observation) || (action==="correct" && !correction.trim())} onClick={()=>void save()}>{busy ? "Saving evidence review…" : "Save evidence review"}</button>
    {error && <p role="alert" className="warning">{error}</p>}
  </div>;
}

export function EvidenceWorkspace({applicationId,allowReview=false}:{applicationId:string;allowReview?:boolean}) {
  const [result,setResult]=useState<{key:string;documents:Json[];error:string}>(),[version,setVersion]=useState(0);
  const key=`${applicationId}:${version}`;
  useEffect(()=>{let ignore=false;api(`/api/applications/${applicationId}/evidence`).then(rows=>{if(!ignore)setResult({key,documents:rows,error:""});}).catch(e=>{if(!ignore)setResult({key,documents:[],error:String(e)});});return()=>{ignore=true;};},[applicationId,key]);
  return <section aria-label="Evidence inspection"><h3>Evidence inspection</h3>{result?.key !== key ? <p role="status">Loading saved evidence…</p> : result.error ? <p role="alert" className="warning">{result.error}</p> : result.documents.length ? result.documents.map(d=><div key={d.id}><Findings document={d}/>{allowReview && <ReviewDocument document={d} onSaved={()=>setVersion(v=>v+1)}/>}</div>) : <p>No PDF evidence attached. Self-declarations remain valid for submission; a caseworker can offer assistance.</p>}</section>;
}

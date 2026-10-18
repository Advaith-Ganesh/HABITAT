"""Evaluate two frozen local methods on the same separate held-out PDF fixtures."""
import hashlib
import json
import math
import statistics
from pathlib import Path
from backend.document_service import process_pdf

ROOT=Path(__file__).resolve().parents[1]


def wilson(correct,total):
    if not total:return None
    z=1.96;p=correct/total;den=1+z*z/total
    centre=(p+z*z/(2*total))/den
    margin=z*math.sqrt(p*(1-p)/total+z*z/(4*total*total))/den
    return [centre-margin,centre+margin]


def evaluate(rows,baseline):
    outputs=[];correct=tp=fp=fn=unsupported=field_tp=field_fp=field_fn=0;times=[];abstentions=handoffs=0
    confusion={k:{v:0 for v in ['income','identity','housing','unknown']} for k in ['income','identity','housing','unknown']}
    for truth in rows:
        data=(ROOT/'evidence_benchmark'/truth['path']).read_bytes()
        result=process_pdf(data,truth['claimed_category'],baseline)
        times.append(result['processing_ms']);correct+=result['detected_category']==truth['expected_category']
        confusion[truth['expected_category']][result['detected_category']]+=1
        found=set(result['issues']);expected=set(truth['planted_issues']);tp+=len(found&expected);fp+=len(found-expected);fn+=len(expected-found)
        expected_fields={(field,v['value'],v['page']) for field,values in truth['expected_fields'].items() for v in values}
        actual_fields={(o['field'],o['value'],o['page']) for o in result['observations']}
        field_tp+=len(expected_fields&actual_fields);field_fp+=len(actual_fields-expected_fields);field_fn+=len(expected_fields-actual_fields)
        unsupported+=sum(o['excerpt'] not in result['pages'][o['page']-1]['text'] or o['value'] not in o['excerpt'] for o in result['observations'])
        abstentions+=result['abstained'];handoffs+=result['human_handoff']
        outputs.append({'document_id':truth['document_id'],'input_sha256':hashlib.sha256(data).hexdigest(),'result':result})
    per_class={}
    for cat,values in confusion.items():
        ctp=values[cat];cfp=sum(confusion[k][cat] for k in confusion if k!=cat);cfn=sum(v for k,v in values.items() if k!=cat)
        precision=ctp/(ctp+cfp) if ctp+cfp else 0;recall=ctp/(ctp+cfn) if ctp+cfn else 0
        per_class[cat]={'precision':precision,'recall':recall,'f1':2*precision*recall/(precision+recall) if precision+recall else 0}
    return {'n':len(rows),'correct_classifications':correct,'classification_accuracy':correct/len(rows),'accuracy_wilson_95':wilson(correct,len(rows)),
            'classification_macro':{metric:statistics.mean(v[metric] for v in per_class.values()) for metric in ['precision','recall','f1']},'classification_by_class':per_class,'confusion':confusion,
            'issue_precision':tp/(tp+fp) if tp+fp else 0,'issue_recall':tp/(tp+fn) if tp+fn else 0,'issue_f1':2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0,
            'planted_issues':tp+fn,'detected_planted_issues':tp,'issue_detection_wilson_95':wilson(tp,tp+fn),'false_alarm_count':fp,
            'field_exact_matches':field_tp,'field_false_extractions':field_fp,'field_missed_observations':field_fn,
            'unsupported_claim_count':unsupported,'abstention_count':abstentions,'abstention_rate':abstentions/len(rows),
            'human_handoff_count':handoffs,'human_handoff_rate':handoffs/len(rows),
            'processing_ms':{'mean':statistics.mean(times),'median':statistics.median(times),'max':max(times)},'documents':outputs}


def main():
    manifest=json.loads((ROOT/'evidence_benchmark/manifest.json').read_text());heldout=manifest['heldout']
    assert not {r['document_id'] for r in heldout}&{r['document_id'] for r in manifest['development']}
    report={'benchmark_version':'1','fixture_count':len(heldout),'development_count':len(manifest['development']),
            'provenance':manifest['provenance'],'methods':{'baseline':'Shared real PDF extraction; naive category keyword counts; first exact-label observation; missing-field/category/readability checklist.',
            'structured':'Shared real PDF extraction; title-based category with abstention; all labelled observations with page grounding; conflict, ambiguity and instruction-text checks. Deterministic, not a trained PDF model or LLM.'},
            'baseline':evaluate(heldout,True),'structured':evaluate(heldout,False),
            'limitations':['24 authored, template-oriented held-out synthetic PDFs are not an independently sampled real-world corpus. Estimates are unstable.',
            'Both methods and ground truth are authored by the same project; this is an internal assurance regression set, not external validation.',
            'Wilson intervals assume independent Bernoulli trials; shared templates violate that approximation. Issue intervals also ignore within-document dependence.',
            'Unsupported claim means ungrounded value/excerpt, not authenticity. Neither method authenticates evidence; both hand every document to a human.',
            'Processing times are measured local subprocess wall time, hardware dependent; no judge/customer time savings are measured. No LLM or OCR.']}
    (ROOT/'reports/document_assurance.json').write_text(json.dumps(report,indent=2)+'\n')
    for method in ['baseline','structured']:
        r=report[method];print(method, 'classification',r['correct_classifications'],'/',r['n'],'issue detection',r['detected_planted_issues'],'/',r['planted_issues'],'false alarms',r['false_alarm_count'],'mean ms',round(r['processing_ms']['mean'],1))
if __name__=='__main__':main()

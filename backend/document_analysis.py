"""Bounded local evidence checks. Not OCR, authentication, eligibility or ML features."""
from io import BytesIO
import re
from pypdf import PdfReader
from pydantic import BaseModel, ConfigDict, Field

MAX_BYTES = 2 * 1024 * 1024
MAX_PAGES = 5
MAX_TEXT = 30000
CATEGORIES = {
    'income': {'employer': 'Employer', 'pay_period': 'Pay period', 'gross_pay': 'Gross pay'},
    'identity': {'synthetic_subject': 'Synthetic subject', 'issued_on': 'Issued on', 'document_reference': 'Document reference'},
    'housing': {'accommodation_type': 'Accommodation type', 'period': 'Period', 'housing_cost': 'Housing cost'},
}
MARKER = 'HABITAT SYNTHETIC DOCUMENT'
INJECTION = re.compile(r'ignore (?:all |previous |prior )*instructions|system prompt|approve all|override instructions|assistant\s*:', re.I)

class Page(BaseModel):
    model_config = ConfigDict(extra='forbid')
    page: int
    text: str

class Observation(BaseModel):
    model_config = ConfigDict(extra='forbid')
    id: str
    field: str
    value: str
    page: int
    excerpt: str
    status: str = 'Observed in text; not verified'

class Analysis(BaseModel):
    model_config = ConfigDict(extra='forbid')
    mode: str = 'Local PDF text extraction + deterministic evidence checks (no LLM/OCR)'
    claimed_category: str
    detected_category: str
    readable: bool
    status: str
    pages: list[Page]
    observations: list[Observation]
    issues: list[str]
    missing_fields: list[str]
    abstained: bool
    human_handoff: bool = True
    human_verification: str = 'Not reviewed; extraction does not establish authenticity or identity'
    processing_ms: float = Field(default=0, ge=0)


def analyse(data: bytes, claimed: str, baseline=False):
    if claimed not in CATEGORIES:
        raise ValueError('Choose income, identity or housing evidence')
    if len(data) > MAX_BYTES:
        raise ValueError('PDF exceeds 2 MiB limit')
    if not data.startswith(b'%PDF-') or b'%%EOF' not in data[-1024:]:
        raise ValueError('Invalid PDF signature or incomplete file')
    reader = PdfReader(BytesIO(data), strict=True)
    if reader.is_encrypted:
        raise ValueError('Encrypted PDFs are not supported; use a synthetic unencrypted fixture')
    if not 1 <= len(reader.pages) <= MAX_PAGES:
        raise ValueError('PDF must contain 1 to 5 pages')
    if any(k in reader.root_object for k in ['/OpenAction', '/AA']):
        raise ValueError('Active PDF actions are not supported')
    names = reader.root_object.get('/Names', {})
    if any(k in names for k in ['/JavaScript', '/EmbeddedFiles']):
        raise ValueError('Scripts and embedded files are not supported')
    pages=[]
    for i, page in enumerate(reader.pages,1):
        text = page.extract_text() or ''
        if len(text) > MAX_TEXT or sum(len(p.text) for p in pages) + len(text) > MAX_TEXT:
            raise ValueError('Extracted text exceeds the sandbox limit')
        pages.append(Page(page=i,text=text))
    all_text='\n'.join(p.text for p in pages)
    readable=sum(c.isalnum() for c in all_text) >= 30
    # Acknowledgement alone cannot identify real PII. Readable files must also
    # carry our fixture marker. This is a bounded sandbox gate, not a PII detector.
    if readable and MARKER not in all_text:
        raise ValueError('Only marked HABITAT synthetic documents are accepted; never upload personal documents')
    issues=[];observations=[];missing=[]
    if not readable:
        return Analysis(claimed_category=claimed,detected_category='unknown',readable=False,
                        status='Insufficient readable evidence',pages=pages,observations=[],
                        issues=['unreadable'],missing_fields=list(CATEGORIES[claimed]),abstained=True)
    if baseline:
        counts={k:len(re.findall(k,all_text,re.I)) for k in CATEGORIES}
        category=max(counts,key=counts.get) if max(counts.values()) else 'unknown'
    else:
        titles=set(re.findall(r'^\s*(Income|Identity|Housing) evidence\s*$',all_text,re.I|re.M))
        titles={s.lower() for s in titles}
        category=next(iter(titles)) if len(titles)==1 else 'unknown'
    if category != claimed:issues.append('category_mismatch')
    if not baseline and INJECTION.search(all_text):issues.append('prompt_injection')
    fields=CATEGORIES.get(category,CATEGORIES[claimed])
    for key,label in fields.items():
        matches=[]
        for p in pages:
            for line in p.text.splitlines():
                m=re.match(r'^\s*'+re.escape(label)+r'\s*:\s*(.*?)\s*$',line,re.I)
                if m and m[1]: matches.append((p.page,line,m[1]))
        if not matches:
            missing.append(key);continue
        if not baseline and len({value for _,_,value in matches})>1:
            issues.append('conflicting_values')
        for page,line,value in (matches[:1] if baseline else matches):
            if not baseline and (re.search(r'\b(?:or|approximately|unknown)\b|\?',value,re.I) or (key in ['gross_pay','housing_cost'] and not re.fullmatch(r'(?:GBP|£)\s*\d+(?:\.\d{1,2})?',value))):
                issues.append('ambiguous_values')
            observations.append(Observation(id=f'p{page}-{key}-{len(observations)}',field=key,value=value,page=page,excerpt=line))
    if missing:issues.append('missing_fields')
    # Grounding is enforced before any result crosses the API boundary.
    for o in observations:
        if o.excerpt not in pages[o.page-1].text or o.value not in o.excerpt:
            raise ValueError('An observation failed source grounding')
    issues=sorted(set(issues))
    return Analysis(claimed_category=claimed,detected_category=category,readable=True,
                    status='Human review required' if issues else 'Extracted; awaiting human verification',
                    pages=pages,observations=observations,issues=issues,missing_fields=missing,abstained=bool(issues))

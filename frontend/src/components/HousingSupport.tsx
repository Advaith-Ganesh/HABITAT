/** Declarative guidance only: no model, network request or automatic referral. */
export function HousingSupport({ answer }: { answer?: string | null }) {
  const concern = answer === "no" || answer === "unsure";
  return (
    <div className={concern ? "warning" : "field-hint"} role={concern ? "status" : undefined}>
      <b>Safe place to stay tonight: {answer === "yes" ? "Yes" : answer === "no" ? "No" : answer === "unsure" ? "Unsure" : "Not answered"}</b>
      {concern && <>
        <p>Contact your local council’s homelessness service as soon as possible for urgent housing assistance. You do not need to wait for a HABITAT assessment.</p>
        <p>HABITAT does not contact the council or emergency services for you and cannot promise accommodation. This concern is separate from model scoring and does not determine eligibility or entitlement.</p>
      </>}
      <p><a href="https://www.gov.uk/if-youre-homeless-at-risk-of-homelessness" target="_blank" rel="noreferrer">Get homelessness help on GOV.UK</a></p>
    </div>
  );
}

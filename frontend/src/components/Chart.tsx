import { lazy, Suspense } from "react";
import { type Json } from "../lib/types";
const Visual = lazy(() => import("./Charts"));
export default function Chart({ kind, data }: { kind: string; data: any }) {
  return (
    <Suspense
      fallback={
        <div className="chart-loading" role="status">
          Loading measured chart…
        </div>
      }
    >
      <Visual kind={kind} data={data} />
    </Suspense>
  );
}
export function ExplanationChart({ explanation }: { explanation: Json }) {
  return <Chart kind="shap" data={explanation} />;
}

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  Cell,
  AreaChart,
  Area,
  PieChart,
  Pie,
} from "recharts";
import { type Json, pct } from "../lib/types";
export default function Charts({ kind, data }: { kind: string; data: any }) {
  const common = {
    tick: { fill: "var(--muted)", fontSize: 11 },
    axisLine: false,
    tickLine: false,
  };
  const tooltip = {
    contentStyle: {
      background: "var(--surface)",
      border: "1px solid var(--border)",
      borderRadius: 8,
      color: "var(--text)",
    },
    labelStyle: { color: "var(--text)" },
    itemStyle: { color: "var(--text)" },
  };
  if (kind === "shap")
    return (
      <div
        className="chart-frame"
        role="img"
        aria-label="Actual SHAP feature contributions; numeric values follow in the input summary"
      >
        <ResponsiveContainer width="100%" height={335}>
          <BarChart
            layout="vertical"
            data={data.attributions.map((a: Json) => ({
              ...a,
              label: a.feature.replaceAll("_", " "),
            }))}
            margin={{ left: 0, right: 24 }}
          >
            <CartesianGrid horizontal={false} stroke="var(--border)" />
            <XAxis
              {...common}
              type="number"
              tickFormatter={(v) => Number(v).toFixed(2)}
            />
            <YAxis {...common} type="category" dataKey="label" width={170} />
            <Tooltip {...tooltip} formatter={(v) => Number(v).toFixed(4)} />
            <Bar
              dataKey="attribution"
              name="SHAP contribution"
              isAnimationActive={false}
              radius={[0, 4, 4, 0]}
            >
              {data.attributions.map((a: Json) => (
                <Cell
                  key={a.feature}
                  fill={
                    a.attribution > 0
                      ? "var(--chart-positive)"
                      : "var(--chart-negative)"
                  }
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  if (kind === "workload")
    return (
      <ResponsiveContainer width="100%" height={220}>
        <BarChart
          layout="vertical"
          data={[
            {
              name: "Classification",
              additional: data.human_review_rate,
              routine: 1 - data.human_review_rate,
            },
            {
              name: "With uncertainty",
              additional: data.routing_review_rate,
              routine: 1 - data.routing_review_rate,
            },
          ]}
        >
          <CartesianGrid horizontal={false} stroke="var(--border)" />
          <XAxis
            {...common}
            type="number"
            domain={[0, 1]}
            tickFormatter={pct}
          />
          <YAxis {...common} dataKey="name" type="category" width={110} />
          <Tooltip {...tooltip} formatter={(v) => pct(Number(v))} />
          <Legend
            formatter={(value) => (
              <span style={{ color: "var(--muted)" }}>{value}</span>
            )}
          />
          <Bar
            name="Additional review"
            dataKey="additional"
            stackId="a"
            fill="var(--chart-positive)"
          />
          <Bar
            name="Routine workflow"
            dataKey="routine"
            stackId="a"
            fill="var(--chart-neutral)"
          />
        </BarChart>
      </ResponsiveContainer>
    );
  if (kind === "distribution")
    return (
      <div className="distribution-chart">
        <ResponsiveContainer width="100%" height={205}>
          <PieChart>
            <Pie
              data={data}
              dataKey="count"
              nameKey="name"
              innerRadius={58}
              outerRadius={82}
              paddingAngle={4}
              stroke="none"
            >
              {data.map((d: Json, i: number) => (
                <Cell
                  key={d.name}
                  fill={
                    [
                      "var(--chart-negative)",
                      "var(--chart-positive)",
                      "var(--chart-neutral)",
                    ][i]
                  }
                />
              ))}
            </Pie>
            <Tooltip {...tooltip} />
            <Legend
              formatter={(value) => (
                <span style={{ color: "var(--muted)" }}>{value}</span>
              )}
              iconType="circle"
              iconSize={7}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    );
  if (kind === "activity")
    return (
      <ResponsiveContainer width="100%" height={205}>
        <AreaChart data={data} margin={{ left: -20, right: 10, top: 10 }}>
          <CartesianGrid vertical={false} stroke="var(--border)" />
          <XAxis
            {...common}
            dataKey="date"
            tickFormatter={(v) => String(v).slice(5)}
          />
          <YAxis {...common} allowDecimals={false} />
          <Tooltip {...tooltip} />
          <Area
            name="Recorded events"
            type="monotone"
            dataKey="events"
            stroke="var(--chart-positive)"
            fill="var(--chart-positive)"
            fillOpacity={0.09}
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    );
  let chartData = data,
    bars = [
      {
        key: "count",
        name: "Synthetic records",
        color: "var(--chart-positive)",
      },
    ],
    name = "name",
    rate = false;
  if (kind === "fairness") {
    name = "group";
    rate = true;
    bars = [
      {
        key: "false_positive_rate",
        name: "False positive rate",
        color: "var(--chart-neutral)",
      },
      {
        key: "false_negative_rate",
        name: "False negative rate",
        color: "var(--chart-positive)",
      },
    ];
  }
  if (kind === "comparison") {
    name = "metric";
    rate = true;
    chartData = ["accuracy", "precision", "recall", "f1"].map((k) => ({
      metric: k,
      model: data.random_forest[k],
      checklist: data.checklist[k],
    }));
    bars = [
      { key: "model", name: "Random Forest", color: "var(--chart-positive)" },
      { key: "checklist", name: "Checklist", color: "var(--chart-negative)" },
    ];
  }
  return (
    <ResponsiveContainer width="100%" height={270}>
      <BarChart data={chartData} margin={{ left: 0, right: 4 }}>
        <CartesianGrid vertical={false} stroke="var(--border)" />
        <XAxis {...common} dataKey={name} />
        <YAxis
          {...common}
          domain={rate ? [0, 1] : undefined}
          tickFormatter={
            rate ? (v) => `${Math.round(Number(v) * 100)}%` : undefined
          }
          ticks={rate ? [0, 0.25, 0.5, 0.75, 1] : undefined}
          allowDecimals={rate}
          width={48}
          tickCount={5}
        />
        <Tooltip
          {...tooltip}
          formatter={(v) => (rate ? pct(Number(v)) : Number(v))}
        />
        {bars.length > 1 && (
          <Legend
            formatter={(value) => (
              <span style={{ color: "var(--muted)" }}>{value}</span>
            )}
            iconType="circle"
            iconSize={7}
          />
        )}{" "}
        {bars.map((b) => (
          <Bar
            key={b.key}
            dataKey={b.key}
            name={b.name}
            isAnimationActive={false}
            fill={b.color}
            radius={[4, 4, 0, 0]}
            maxBarSize={40}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}

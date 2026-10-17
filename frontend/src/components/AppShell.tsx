import { useEffect, useState, type ReactNode } from "react";
import {
  ClipboardPlus,
  Files,
  HelpCircle,
  LayoutDashboard,
  Moon,
  Scale,
  ScanLine,
  ShieldCheck,
  Sun,
  Users,
} from "lucide-react";
import { type Json } from "../lib/types";
export const adminPages = [
  "Overview",
  "Applications",
  "AI Assessment",
  "Fairness & Sandbox",
  "Human Review",
];
export const applicantPages = [
  "Apply for Housing",
  "My Applications",
  "Help & Transparency",
];
const icons = [LayoutDashboard, Files, ScanLine, Scale, Users];
const applicantIcons = [ClipboardPlus, Files, HelpCircle];
export function AppShell({
  portal,
  page,
  navigate,
  switchPortal,
  health,
  children,
}: {
  portal: string;
  page: string;
  navigate: (page: string) => void;
  switchPortal: () => void;
  health?: Json;
  children: ReactNode;
}) {
  const [dark, setDark] = useState(() => {
    try {
      return localStorage.getItem("habitat.v2.theme") === "dark";
    } catch {
      return false;
    }
  });
  useEffect(() => {
    document.documentElement.dataset.theme = dark ? "dark" : "light";
    try {
      localStorage.setItem("habitat.v2.theme", dark ? "dark" : "light");
    } catch {
      /* In-memory theme remains available. */
    }
  }, [dark]);
  useEffect(() => {
    document.getElementById("page-title")?.focus({ preventScroll: true });
    window.scrollTo({ top: 0, behavior: "instant" });
  }, [page, portal]);
  const admin = portal === "admin";
  return (
    <div className="app v4-app v5-app">
      <a
        className="skip-link"
        href="#main-content"
        onClick={(event) => {
          event.preventDefault();
          document.getElementById("main-content")?.focus();
        }}
      >
        Skip to main content
      </a>
      <aside
        className="sidebar"
        aria-label={`${admin ? "Administrator" : "Applicant"} navigation`}
      >
        <div className="brand">
          <img src="/habitat-logo.svg" alt="" width="44" height="44" />
          <span className="brand-word">
            HABITAT <span className="brand-ai">AI</span>
            <small>Fairer Housing. Clearer Decisions.</small>
          </span>
        </div>
        <div className="portal-caption">
          {admin ? "Administrator portal" : "Applicant portal"}
        </div>
        <nav
          className="main-nav"
          aria-label={`${admin ? "Administrator" : "Applicant"} tabs`}
        >
          {(admin ? adminPages : applicantPages).map((label, i) => {
            const Icon = (admin ? icons : applicantIcons)[i];
            return (
              <button
                key={label}
                className={page === label ? "nav-active" : ""}
                onClick={() => navigate(label)}
                aria-current={page === label ? "page" : undefined}
              >
                <Icon size={19} />
                <span className="nav-text">{label}</span>
              </button>
            );
          })}
        </nav>
        <div className="sidebar-bottom">
          <ShieldCheck size={20} />
          <span>
            <strong>Built around human review</strong>
            <small>Every housing decision stays with people.</small>
          </span>
        </div>
      </aside>
      <div className="shell">
        <header className="topbar">
          <span className="breadcrumbs">
            {admin ? "Administrator" : "Applicant"}{" "}
            <span aria-hidden="true">/</span> {page}
          </span>
          <div className="topbar-right">
            {admin && (
              <span className="muted health-label">
                {health?.model?.ready
                  ? `Model online · ${health.model.version}`
                  : health
                    ? "Model unavailable"
                    : "Checking model…"}
              </span>
            )}
            <button className="secondary portal-switch" onClick={switchPortal}>
              {admin ? "Switch to applicant" : "Switch to administrator"}
            </button>
            <button
              className="icon-button"
              aria-label={
                dark ? "Switch to light theme" : "Switch to dark theme"
              }
              onClick={() => setDark(!dark)}
            >
              {dark ? <Sun size={18} /> : <Moon size={18} />}
            </button>
          </div>
        </header>
        <div className="sandbox">
          <ShieldCheck size={14} />
          <b>Sandbox · Synthetic Data</b>
          <span>
            No real housing decisions. Portal switching is a demo, not access
            control.
          </span>
        </div>
        <main id="main-content" tabIndex={-1}>
          {children}
          <footer>
            HABITAT AI <span>Fairer Housing. Clearer Decisions.</span>
            <span>SotonShip 2026 · Synthetic demonstration</span>
          </footer>
        </main>
      </div>
    </div>
  );
}

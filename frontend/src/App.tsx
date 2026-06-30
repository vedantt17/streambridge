import { Activity, BarChart3, Cable, ClipboardCheck, Gauge, LayoutDashboard, ListChecks, ServerCog, Users } from "lucide-react";
import { NavLink, Route, Routes } from "react-router-dom";
import ApiTroubleshooting from "./pages/ApiTroubleshooting";
import Dashboard from "./pages/Dashboard";
import FeedSandbox from "./pages/FeedSandbox";
import IssueTriage from "./pages/IssueTriage";
import PartnerDetail from "./pages/PartnerDetail";
import Partners from "./pages/Partners";
import ProductFeedback from "./pages/ProductFeedback";
import ReadinessReport from "./pages/ReadinessReport";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/partners", label: "Partners", icon: Users },
  { to: "/sandbox", label: "Sandbox", icon: Cable },
  { to: "/triage", label: "Triage", icon: ListChecks },
  { to: "/api-troubleshooting", label: "API Checks", icon: ServerCog },
  { to: "/readiness", label: "Readiness", icon: ClipboardCheck },
  { to: "/product-feedback", label: "Product Feedback", icon: BarChart3 }
];

export default function App() {
  return (
    <div className="min-h-[100dvh] bg-ink text-slate-100">
      <aside className="fixed inset-y-0 left-0 z-20 hidden w-72 border-r border-line bg-[#0b1423]/95 px-4 py-5 lg:block">
        <div className="flex items-center gap-3 border-b border-line pb-5">
          <div className="grid h-11 w-11 place-items-center rounded-lg border border-cyan-300/35 bg-cyan-400/10 text-cyan-100">
            <Activity size={22} />
          </div>
          <div>
            <p className="text-lg font-semibold text-white">StreamBridge</p>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Partner Console</p>
          </div>
        </div>
        <nav className="mt-6 grid gap-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `flex h-11 items-center gap-3 rounded-lg px-3 text-sm font-medium transition ${
                  isActive
                    ? "bg-cyan-400/12 text-cyan-50 ring-1 ring-cyan-300/25"
                    : "text-slate-400 hover:bg-slate-800/70 hover:text-slate-100"
                }`
              }
            >
              <item.icon size={18} />
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <header className="sticky top-0 z-10 border-b border-line bg-[#0b1423]/95 px-4 py-3 backdrop-blur lg:hidden">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="font-semibold text-white">StreamBridge</p>
            <p className="text-xs text-slate-500">Partner Console</p>
          </div>
          <Gauge className="text-cyan-100" size={22} />
        </div>
        <nav className="dashboard-scrollbar mt-3 flex gap-2 overflow-x-auto pb-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `inline-flex h-10 shrink-0 items-center gap-2 rounded-lg border px-3 text-xs font-semibold ${
                  isActive
                    ? "border-cyan-300/35 bg-cyan-400/12 text-cyan-50"
                    : "border-line bg-slate-900/60 text-slate-400"
                }`
              }
            >
              <item.icon size={16} />
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>

      <main className="lg:pl-72">
        <div className="mx-auto min-h-[100dvh] w-full max-w-[1500px] px-4 py-5 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/partners" element={<Partners />} />
            <Route path="/partners/:partnerId" element={<PartnerDetail />} />
            <Route path="/sandbox" element={<FeedSandbox />} />
            <Route path="/triage" element={<IssueTriage />} />
            <Route path="/api-troubleshooting" element={<ApiTroubleshooting />} />
            <Route path="/readiness" element={<ReadinessReport />} />
            <Route path="/product-feedback" element={<ProductFeedback />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}


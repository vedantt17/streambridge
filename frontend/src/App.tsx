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
import { VantaWavesBackground } from "./components/VantaWavesBackground";

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
    <div className="relative min-h-[100dvh] overflow-hidden bg-ink text-slate-100">
      <VantaWavesBackground />
      <div className="pointer-events-none fixed inset-0 z-0 bg-[linear-gradient(90deg,rgba(4,9,18,0.66)_0%,rgba(4,9,18,0.16)_28%,rgba(4,9,18,0)_58%)]" />

      <aside className="fixed inset-y-0 left-0 z-20 hidden w-[17rem] border-r border-white/10 bg-[#07111f]/50 px-4 py-5 shadow-2xl shadow-black/20 backdrop-blur-xl lg:block">
        <div className="flex items-center gap-3 border-b border-white/10 pb-5">
          <div className="grid h-11 w-11 place-items-center rounded-lg border border-cyan-200/35 bg-cyan-300/10 text-cyan-100 shadow-lg shadow-cyan-950/30">
            <Activity size={22} />
          </div>
          <div>
            <p className="font-display text-2xl italic leading-none text-white">StreamBridge</p>
            <p className="mt-1 text-[0.66rem] uppercase tracking-[0.22em] text-cyan-100/70">Partner Console</p>
          </div>
        </div>
        <nav className="mt-7 grid gap-1.5">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `flex h-11 items-center gap-3 rounded-lg px-3 text-sm font-semibold transition duration-200 ${
                  isActive
                    ? "bg-white/10 text-white ring-1 ring-cyan-200/30"
                    : "text-slate-300/75 hover:bg-white/10 hover:text-white"
                }`
              }
            >
              <item.icon size={18} />
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <header className="sticky top-0 z-20 border-b border-white/10 bg-[#07111f]/55 px-4 py-3 backdrop-blur-xl lg:hidden">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="font-display text-2xl italic leading-none text-white">StreamBridge</p>
            <p className="text-xs uppercase tracking-[0.16em] text-cyan-100/70">Partner Console</p>
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
                `inline-flex h-10 shrink-0 items-center gap-2 rounded-lg border px-3 text-xs font-semibold backdrop-blur ${
                  isActive
                    ? "border-cyan-200/30 bg-white/10 text-cyan-50"
                    : "border-white/10 bg-slate-950/25 text-slate-300"
                }`
              }
            >
              <item.icon size={16} />
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>

      <main className="relative z-10 lg:pl-[17rem]">
        <div className="mx-auto min-h-[100dvh] w-full max-w-[1420px] px-4 py-6 sm:px-6 lg:px-8 xl:py-8">
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

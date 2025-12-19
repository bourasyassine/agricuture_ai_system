import { NavLink } from "react-router-dom";

const links = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/plots", label: "Plots" },
  { to: "/anomalies", label: "Alerts" },
];

export default function Sidebar() {
  return (
    <aside className="hidden w-72 flex-col bg-agri-900/90 text-slate-100 shadow-2xl shadow-black/40 backdrop-blur lg:flex">
      <div className="flex items-center gap-3 px-6 py-6 border-b border-white/5">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-agri-500/20 text-agri-500">
          <span className="text-lg font-semibold">Ag</span>
        </div>
        <div>
          <p className="text-sm text-slate-300">Farm Intelligence</p>
          <p className="text-lg font-semibold text-white">Agri AI</p>
        </div>
      </div>

      <nav className="flex-1 px-4 py-6 space-y-2">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              [
                "block rounded-xl px-4 py-3 text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-white/10 text-white shadow-inner shadow-agri-500/20 ring-1 ring-agri-500/40"
                  : "text-slate-300 hover:bg-white/5 hover:text-white",
              ].join(" ")
            }
          >
            {link.label}
          </NavLink>
        ))}
      </nav>

      <div className="px-6 py-5 border-t border-white/5">
        <div className="rounded-xl bg-white/5 px-4 py-3">
          <p className="text-xs uppercase tracking-wide text-slate-400">
            Status
          </p>
          <p className="text-sm font-semibold text-white">Connected</p>
          <p className="text-xs text-slate-400">Backend: 127.0.0.1:8000</p>
        </div>
      </div>
    </aside>
  );
}

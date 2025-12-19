import { Link } from "react-router-dom";
import StatusBadge from "./StatusBadge";
import type { PlotStatus } from "../services/plots";

export default function PlotCard({ plot }: { plot: PlotStatus }) {
  return (
    <Link
      to={`/plots/${plot.id}`}
      className="block focus:outline-none focus-visible:ring-2 focus-visible:ring-agri-500 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 rounded-2xl"
    >
      <div className="glass-card rounded-2xl p-6 text-white transition duration-300 hover:-translate-y-1 hover:shadow-2xl">
        <div className="mb-4 flex items-start justify-between">
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-300">Plot</p>
            <h3 className="text-xl font-semibold text-white">{plot.name}</h3>
          </div>
          <StatusBadge status={plot.status} />
        </div>

        <div className="flex items-center justify-between text-sm text-slate-200">
          <p className="font-medium">
            Size: <span className="text-white">{plot.size_hectares} ha</span>
          </p>
          <span className="rounded-full bg-white/10 px-3 py-1 text-xs">
            ID #{plot.id}
          </span>
        </div>
      </div>
    </Link>
  );
}

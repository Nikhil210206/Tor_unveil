import { NavLink } from "@/components/NavLink";
import { Badge } from "@/components/ui/badge";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Shield } from "lucide-react";

export function Header() {
  const { data: stats } = useQuery({
    queryKey: ["stats"],
    queryFn: api.getStats,
    refetchInterval: 5000,
  });

  return (
    <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Shield className="h-8 w-8 text-primary" />
            <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              TOR Unveil
            </h1>
          </div>

          <nav className="hidden md:flex items-center gap-1">
            <NavLink
              to="/"
              end
              className="px-4 py-2 rounded-md text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent/50 transition-colors"
              activeClassName="text-foreground bg-accent"
            >
              Dashboard
            </NavLink>
            <NavLink
              to="/upload"
              className="px-4 py-2 rounded-md text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent/50 transition-colors"
              activeClassName="text-foreground bg-accent"
            >
              Upload
            </NavLink>
            <NavLink
              to="/flows"
              className="px-4 py-2 rounded-md text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent/50 transition-colors"
              activeClassName="text-foreground bg-accent"
            >
              Flows
            </NavLink>
            <NavLink
              to="/graph"
              className="px-4 py-2 rounded-md text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent/50 transition-colors"
              activeClassName="text-foreground bg-accent"
            >
              Graph
            </NavLink>
            <NavLink
              to="/timeline"
              className="px-4 py-2 rounded-md text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent/50 transition-colors"
              activeClassName="text-foreground bg-accent"
            >
              Timeline
            </NavLink>
            <NavLink
              to="/reports"
              className="px-4 py-2 rounded-md text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent/50 transition-colors"
              activeClassName="text-foreground bg-accent"
            >
              Reports
            </NavLink>
          </nav>

          {stats && stats.critical_flows > 0 && (
            <Badge
              variant="destructive"
              className="animate-pulse-slow font-semibold"
            >
              {stats.critical_flows} Critical Alerts
            </Badge>
          )}
        </div>
      </div>
    </header>
  );
}

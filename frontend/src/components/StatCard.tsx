import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";
import { useEffect, useState } from "react";

interface StatCardProps {
  title: string;
  value: number;
  icon: LucideIcon;
  color: "blue" | "yellow" | "orange" | "red";
  pulse?: boolean;
}

export function StatCard({ title, value, icon: Icon, color, pulse }: StatCardProps) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    const duration = 1000;
    const steps = 20;
    const increment = value / steps;
    let current = 0;
    
    const timer = setInterval(() => {
      current += increment;
      if (current >= value) {
        setDisplayValue(value);
        clearInterval(timer);
      } else {
        setDisplayValue(Math.floor(current));
      }
    }, duration / steps);

    return () => clearInterval(timer);
  }, [value]);

  const colorClasses = {
    blue: "border-l-primary text-primary",
    yellow: "border-l-warning text-warning",
    orange: "border-l-high text-high",
    red: "border-l-critical text-critical",
  };

  const bgClasses = {
    blue: "bg-primary/10",
    yellow: "bg-warning/10",
    orange: "bg-high/10",
    red: "bg-critical/10",
  };

  return (
    <Card
      className={cn(
        "p-6 border-l-4 hover:shadow-lg transition-all duration-300",
        colorClasses[color],
        pulse && "animate-pulse-slow"
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-muted-foreground mb-2">{title}</p>
          <p className="text-3xl font-bold animate-counter">{displayValue.toLocaleString()}</p>
        </div>
        <div className={cn("p-3 rounded-lg", bgClasses[color])}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
    </Card>
  );
}

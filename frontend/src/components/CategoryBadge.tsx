import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface CategoryBadgeProps {
  category: "Low" | "Medium" | "High" | "Critical";
  className?: string;
}

export function CategoryBadge({ category, className }: CategoryBadgeProps) {
  const variants = {
    Low: "bg-success/20 text-success border-success/30",
    Medium: "bg-warning/20 text-warning border-warning/30",
    High: "bg-high/20 text-high border-high/30",
    Critical: "bg-critical/20 text-critical border-critical/30 animate-pulse-slow",
  };

  return (
    <Badge
      variant="outline"
      className={cn("font-semibold", variants[category], className)}
    >
      {category}
    </Badge>
  );
}

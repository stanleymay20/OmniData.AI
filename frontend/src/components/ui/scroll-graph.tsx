import * as React from "react"
import { cn } from "@/lib/utils"

interface ScrollGraphProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
  title?: string
  description?: string
  data?: any
}

const ScrollGraph = React.forwardRef<HTMLDivElement, ScrollGraphProps>(
  ({ className, children, title, description, data, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "bg-gradient-to-r from-purple-400 via-purple-500 to-purple-600 text-white p-6 rounded-lg shadow-lg",
          className
        )}
        {...props}
      >
        {title && <h2 className="text-2xl font-bold mb-2">{title}</h2>}
        {description && <p className="text-sm opacity-90 mb-4">{description}</p>}
        <div className="bg-white/10 rounded-lg p-4">
          {children}
        </div>
      </div>
    )
  }
)
ScrollGraph.displayName = "ScrollGraph"

export { ScrollGraph } 
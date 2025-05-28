import * as React from "react"
import { cn } from "@/lib/utils"

interface ToastProps extends React.HTMLAttributes<HTMLDivElement> {
  type?: "success" | "error" | "info"
  message: string
  onClose?: () => void
}

const Toast = React.forwardRef<HTMLDivElement, ToastProps>(
  ({ className, type = "info", message, onClose, ...props }, ref) => {
    const typeClasses = {
      success: "bg-green-100 border-green-400 text-green-700",
      error: "bg-red-100 border-red-400 text-red-700",
      info: "bg-blue-100 border-blue-400 text-blue-700"
    }

    return (
      <div
        ref={ref}
        className={cn(
          "fixed bottom-4 right-4 px-4 py-3 rounded shadow-lg border",
          typeClasses[type],
          className
        )}
        role="alert"
        {...props}
      >
        <div className="flex items-center">
          <span className="block sm:inline">{message}</span>
          {onClose && (
            <button
              className="ml-4 text-current hover:opacity-75"
              onClick={onClose}
            >
              ×
            </button>
          )}
        </div>
      </div>
    )
  }
)
Toast.displayName = "Toast"

export { Toast } 
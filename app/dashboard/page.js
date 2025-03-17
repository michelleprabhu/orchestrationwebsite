import { DashboardContent } from "@/components/dashboard-content"
import { DashboardSidebar } from "@/components/dashboard-sidebar"

export default function DashboardPage() {
  return (
    <div className="flex min-h-screen">
      <DashboardSidebar />
      <DashboardContent />
    </div>
  )
}


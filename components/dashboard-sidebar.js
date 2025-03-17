"use client"

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Home, MessageSquare, Settings, BarChart2, LogOut, Menu, X } from "lucide-react"
import Image from "next/image"

export function DashboardSidebar() {
  const [isOpen, setIsOpen] = useState(false)

  const toggleSidebar = () => {
    setIsOpen(!isOpen)
  }

  return (
    <>
      <Button variant="ghost" size="icon" className="absolute left-4 top-4 z-50 md:hidden" onClick={toggleSidebar}>
        {isOpen ? <X /> : <Menu />}
      </Button>

      <div
        className={`fixed inset-y-0 left-0 z-40 w-64 transform bg-black/80 p-4 backdrop-blur-sm transition-transform duration-200 ease-in-out md:relative md:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex h-full flex-col">
          <div className="mb-8 flex items-center justify-center py-4">
            <Image src="/moolai-logo.png" alt="MoolAI Logo" width={120} height={40} />
          </div>

          <nav className="flex-1 space-y-2">
            <Button variant="ghost" className="w-full justify-start" asChild>
              <Link href="/chat">
                <MessageSquare className="mr-2 h-5 w-5" />
                Chat
              </Link>
            </Button>

            <Button variant="ghost" className="w-full justify-start" asChild>
              <Link href="/dashboard">
                <Home className="mr-2 h-5 w-5" />
                Dashboard
              </Link>
            </Button>
            
            <Button variant="ghost" className="w-full justify-start" asChild>
              <Link href="/dashboard/settings">
                <Settings className="mr-2 h-5 w-5" />
                Settings
              </Link>
            </Button>
          </nav>

          <div className="border-t border-gray-800 pt-4">
            <Button variant="ghost" className="w-full justify-start text-red-500 hover:text-red-400" asChild>
              <Link href="/">
                <LogOut className="mr-2 h-5 w-5" />
                Logout
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </>
  )
}


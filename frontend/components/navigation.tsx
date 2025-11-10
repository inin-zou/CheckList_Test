"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { FrostedCard } from "./frosted-card"
import { ThemeToggle } from "./theme-toggle"
import { Home, FileText, CheckSquare, BarChart3, MessageSquare, Settings, ChevronDown } from "lucide-react"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Button } from "@/components/ui/button"

const navItems = [
  { href: "/", label: "Dashboard", icon: Home },
  {
    label: "Documents",
    icon: FileText,
    children: [
      { href: "/documents/checklist", label: "Checklist Templates" },
      { href: "/documents/user", label: "User Documents" },
    ],
  },
  {
    label: "Checklist",
    icon: CheckSquare,
    children: [
      { href: "/checklist/questions", label: "Questions" },
      { href: "/checklist/conditions", label: "Conditions" },
      { href: "/checklist/templates", label: "Templates" },
      { href: "/checklist/run", label: "Run Checklist" },
    ],
  },
  { href: "/results", label: "Results", icon: BarChart3 },
  { href: "/rag", label: "RAG", icon: MessageSquare },
  { href: "/settings", label: "Settings", icon: Settings },
]

export function Navigation() {
  const pathname = usePathname()

  return (
    <FrostedCard className="sticky top-4 mx-4 mb-8 z-50">
      <nav className="px-6 py-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-400" />
            <span className="font-bold text-lg">DocCheck</span>
          </Link>

          <div className="flex items-center gap-2">
            {navItems.map((item) => {
              if (item.children) {
                return (
                  <DropdownMenu key={item.label}>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" className="gap-2">
                        <item.icon className="h-4 w-4" />
                        {item.label}
                        <ChevronDown className="h-3 w-3" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="backdrop-blur-xl bg-white/80 dark:bg-gray-900/80">
                      {item.children.map((child) => (
                        <DropdownMenuItem key={child.href} asChild>
                          <Link href={child.href} className={pathname === child.href ? "bg-accent" : ""}>
                            {child.label}
                          </Link>
                        </DropdownMenuItem>
                      ))}
                    </DropdownMenuContent>
                  </DropdownMenu>
                )
              }

              const Icon = item.icon
              const isActive = pathname === item.href

              return (
                <Link key={item.href} href={item.href}>
                  <Button variant={isActive ? "secondary" : "ghost"} className="gap-2">
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </Button>
                </Link>
              )
            })}

            <ThemeToggle />
          </div>
        </div>
      </nav>
    </FrostedCard>
  )
}

"use client"

import * as React from "react"
import Image from "next/image"
import { usePathname } from "next/navigation"
import {
  IconDashboard,
  IconHelp,
  IconListDetails,
  IconReport,
  IconSearch,
  IconSettings,
} from "@tabler/icons-react"

import { NavMain } from "@/components/nav-main"
import { NavSecondary } from "@/components/nav-secondary"
import { NavUser } from "@/components/nav-user"
import { PipelineStatus } from "@/components/pipeline-status"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"

const data = {
  user: {
    name: "Mr Chong Quey Lim",
    email: "cql@tsaofoundation.org",
    avatar: "/avatars/shadcn.jpg",
  },
  navMain: [
    {
      title: "Dashboard",
      url: "/",
      icon: IconDashboard,
    },
    {
      title: "Organisation Configuration",
      url: "/configure",
      icon: IconSettings,
    },
    {
      title: "Initiatives",
      url: "/initiatives",
      icon: IconListDetails,
    },
    {
      title: "Grants",
      url: "/grants",
      icon: IconReport,
    },
  ],
  navSecondary: [
    {
      title: "Settings",
      url: "",
      icon: IconSettings,
    },
    {
      title: "Get Help",
      url: "",
      icon: IconHelp,
    },
    {
      title: "Search",
      url: "",
      icon: IconSearch,
    },
  ],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const pathname = usePathname()

  return (
    <Sidebar collapsible="offcanvas" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              asChild
              className="h-20 data-[slot=sidebar-menu-button]:p-1.5!"
            >
              <Image
                src="/long.png"
                width={664}
                height={314}
                alt="Tsao Foundation Tagline"
                className="object-contain"
              />
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} currentPath={pathname} />
        <NavSecondary
          items={data.navSecondary}
          currentPath={pathname}
          className="mt-auto"
        />
        <PipelineStatus />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user} />
      </SidebarFooter>
    </Sidebar>
  )
}

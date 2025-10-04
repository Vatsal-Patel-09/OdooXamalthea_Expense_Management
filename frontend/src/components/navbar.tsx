'use client';

import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { ThemeToggle } from '@/components/theme-toggle';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { 
  LayoutDashboard, 
  Receipt, 
  PlusCircle, 
  Settings, 
  LogOut,
  Menu,
  Wallet
} from 'lucide-react';
import Link from 'next/link';

export function Navbar() {
  const router = useRouter();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const navItems = [
    { 
      name: 'Dashboard', 
      path: '/dashboard', 
      icon: LayoutDashboard 
    },
    { 
      name: 'My Expenses', 
      path: '/expenses', 
      icon: Receipt 
    },
    { 
      name: 'New Expense', 
      path: '/expenses/new', 
      icon: PlusCircle 
    },
    ...(user?.role === 'admin' ? [{ 
      name: 'Categories', 
      path: '/admin/categories', 
      icon: Settings 
    }] : []),
  ];

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <Wallet className="h-6 w-6" />
            </div>
            <div className="hidden sm:block">
              <h1 className="text-xl font-bold bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
                Expense Tracker
              </h1>
            </div>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex md:items-center md:space-x-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link key={item.path} href={item.path}>
                  <Button 
                    variant="ghost" 
                    className="flex items-center space-x-2"
                  >
                    <Icon className="h-4 w-4" />
                    <span>{item.name}</span>
                  </Button>
                </Link>
              );
            })}
          </div>

          {/* Right side actions */}
          <div className="flex items-center space-x-3">
            <div className="hidden sm:flex items-center space-x-2 text-sm text-muted-foreground">
              <div className="text-right">
                <p className="font-medium text-foreground">{user?.name}</p>
                <p className="text-xs capitalize">{user?.role}</p>
              </div>
            </div>
            
            <ThemeToggle />
            
            <Button
              variant="outline"
              size="icon"
              onClick={handleLogout}
              className="hidden md:flex"
              title="Logout"
            >
              <LogOut className="h-4 w-4" />
            </Button>

            {/* Mobile menu dropdown */}
            <div className="md:hidden">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="icon">
                    <Menu className="h-5 w-5" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <div className="px-2 py-1.5 text-sm font-medium">
                    <p className="text-foreground">{user?.name}</p>
                    <p className="text-xs text-muted-foreground capitalize">{user?.role}</p>
                  </div>
                  <DropdownMenuSeparator />
                  {navItems.map((item) => {
                    const Icon = item.icon;
                    return (
                      <DropdownMenuItem key={item.path} onClick={() => router.push(item.path)}>
                        <Icon className="h-4 w-4 mr-2" />
                        {item.name}
                      </DropdownMenuItem>
                    );
                  })}
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout}>
                    <LogOut className="h-4 w-4 mr-2" />
                    Logout
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}

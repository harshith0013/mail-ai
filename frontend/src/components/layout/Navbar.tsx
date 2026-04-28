import { Sun, Moon, Menu } from "lucide-react";
import { useThemeStore } from "@/stores/theme-store";
import { Button } from "../ui/Button";

interface NavbarProps {
  onMenuClick: () => void;
}

export function Navbar({ onMenuClick }: NavbarProps) {
  const { theme, toggleTheme } = useThemeStore();

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-16 items-center px-4 gap-4 sm:px-8">
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden"
          onClick={onMenuClick}
        >
          <Menu className="h-5 w-5" />
        </Button>
        <div className="flex flex-1 items-center gap-2 font-bold tracking-tight text-xl">
          <div className="bg-gradient-to-br from-primary to-primary/60 text-transparent bg-clip-text">
            Mail AI
          </div>
        </div>
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            className="rounded-full"
          >
            {theme === "light" ? (
              <Sun className="h-5 w-5" />
            ) : (
              <Moon className="h-5 w-5" />
            )}
            <span className="sr-only">Toggle theme</span>
          </Button>
          <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 border shadow-sm shrink-0 overflow-hidden" />
        </div>
      </div>
    </header>
  );
}

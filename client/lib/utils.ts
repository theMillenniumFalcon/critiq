import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format a date string to a human-readable format
 */
export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Convert a GitHub repository URL to owner/repo format
 */
export function getRepoFromUrl(url: string): string | null {
  try {
    const parsedUrl = new URL(url);
    const path = parsedUrl.pathname.slice(1); // Remove leading slash
    if (parsedUrl.hostname === 'github.com' && path.split('/').length >= 2) {
      return path.split('/').slice(0, 2).join('/');
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * Get PR number from GitHub URL if present
 */
export function getPrNumberFromUrl(url: string): number | null {
  try {
    const parsedUrl = new URL(url);
    const path = parsedUrl.pathname;
    const match = path.match(/\/pull\/(\d+)$/);
    if (match) {
      return parseInt(match[1], 10);
    }
    return null;
  } catch {
    return null;
  }
}

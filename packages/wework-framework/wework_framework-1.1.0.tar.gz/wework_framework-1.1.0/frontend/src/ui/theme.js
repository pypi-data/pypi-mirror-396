// Design Tokens & Theme System
export const theme = {
  colors: {
    // Backgrounds
    bg: {
      primary: '#0f172a',
      secondary: '#1e293b',
      tertiary: '#334155',
      hover: '#475569',
    },
    // Text
    text: {
      primary: '#f1f5f9',
      secondary: '#e2e8f0',
      tertiary: '#cbd5e1',
      muted: '#94a3b8',
    },
    // Borders
    border: {
      default: '#334155',
      light: '#475569',
      dark: '#1e293b',
    },
    // Semantic colors
    success: {
      main: '#4caf50',
      light: '#86efac',
      dark: '#45a049',
      bg: 'rgba(34, 197, 94, 0.15)',
      border: 'rgba(34, 197, 94, 0.3)',
    },
    error: {
      main: '#ef4444',
      light: '#fca5a5',
      dark: '#dc2626',
      bg: 'rgba(239, 68, 68, 0.15)',
      border: 'rgba(239, 68, 68, 0.3)',
    },
    warning: {
      main: '#ff9800',
      light: '#ffb74d',
      dark: '#f57c00',
      bg: 'rgba(255, 152, 0, 0.15)',
      border: 'rgba(255, 152, 0, 0.3)',
    },
    info: {
      main: '#3b82f6',
      light: '#93c5fd',
      dark: '#2563eb',
      bg: 'rgba(59, 130, 246, 0.15)',
      border: 'rgba(59, 130, 246, 0.3)',
    },
  },
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
    '2xl': '48px',
  },
  borderRadius: {
    sm: '4px',
    md: '8px',
    lg: '12px',
    xl: '16px',
    full: '9999px',
  },
  shadows: {
    sm: '0 1px 2px rgba(0, 0, 0, 0.3)',
    md: '0 4px 8px rgba(0, 0, 0, 0.4)',
    lg: '0 8px 32px rgba(0, 0, 0, 0.5)',
  },
  transitions: {
    fast: '0.15s ease-out',
    normal: '0.2s ease-out',
    slow: '0.3s ease-out',
  },
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '960px',
    xl: '1280px',
  },
  zIndex: {
    dropdown: 100,
    modal: 1000,
    toast: 2000,
  },
}

export const getColor = (path) => {
  const keys = path.split('.')
  let value = theme.colors
  for (const key of keys) {
    value = value?.[key]
    if (!value) return path
  }
  return value
}


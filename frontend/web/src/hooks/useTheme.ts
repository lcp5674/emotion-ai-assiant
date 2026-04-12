import { useState, useEffect } from 'react'

type Theme = 'light' | 'dark'
type ThemeColor = 'purple' | 'blue' | 'green' | 'red' | 'orange'

const themeColors = {
  purple: '#722ed1',
  blue: '#1890ff',
  green: '#52c41a',
  red: '#f5222d',
  orange: '#fa8c16',
}

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(() => {
    if (typeof window === 'undefined') return 'light'
    return (localStorage.getItem('theme') as Theme) || 'light'
  })

  const [themeColor, setThemeColor] = useState<ThemeColor>(() => {
    if (typeof window === 'undefined') return 'purple'
    return (localStorage.getItem('themeColor') as ThemeColor) || 'purple'
  })

  useEffect(() => {
    localStorage.setItem('theme', theme)
  }, [theme])

  useEffect(() => {
    localStorage.setItem('themeColor', themeColor)
  }, [themeColor])

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light')
  }

  const changeThemeColor = (color: ThemeColor) => {
    setThemeColor(color)
  }

  const getThemeColor = () => {
    return themeColors[themeColor]
  }

  return { theme, toggleTheme, themeColor, changeThemeColor, getThemeColor, themeColors }
}

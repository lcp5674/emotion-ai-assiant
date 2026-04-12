import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ConfigProvider, theme } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import enUS from 'antd/locale/en_US'
import App from './App'
import { useTheme } from './hooks/useTheme'
import i18n from './i18n'
import './index.css'

function ThemedApp() {
  const { theme: currentTheme, getThemeColor } = useTheme()
  const locale = i18n.language === 'zh-CN' ? zhCN : enUS
  return (
    <ConfigProvider
      locale={locale}
      theme={{
        algorithm: currentTheme === 'dark' ? theme.darkAlgorithm : theme.defaultAlgorithm,
        token: {
          colorPrimary: getThemeColor(),
        },
      }}
    >
      <App />
    </ConfigProvider>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <ThemedApp />
    </BrowserRouter>
  </React.StrictMode>,
)

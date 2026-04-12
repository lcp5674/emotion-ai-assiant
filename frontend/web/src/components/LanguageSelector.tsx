import { useState } from 'react'
import { Select, ConfigProvider } from 'antd'
import { useTranslation } from 'react-i18next'
import zhCN from 'antd/locale/zh_CN'
import enUS from 'antd/locale/en_US'
import i18n from '../i18n'

const LanguageSelector = () => {
  const { t } = useTranslation()
  const [language, setLanguage] = useState(i18n.language)

  const handleLanguageChange = (value: string) => {
    setLanguage(value)
    i18n.changeLanguage(value)
  }

  const locale = language === 'zh-CN' ? zhCN : enUS

  return (
    <ConfigProvider locale={locale}>
      <Select
        value={language}
        onChange={handleLanguageChange}
        style={{ width: 120 }}
        options={[
          {
            value: 'zh-CN',
            label: '中文'
          },
          {
            value: 'en-US',
            label: 'English'
          }
        ]}
      />
    </ConfigProvider>
  )
}

export default LanguageSelector

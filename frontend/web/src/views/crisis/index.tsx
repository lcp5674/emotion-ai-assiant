/**
 * 危机干预求助页面
 * 提供紧急求助资源和一键拨打功能
 */
import { useEffect, useState } from 'react'
import { Card, List, Button, Tag, Typography, Space, Alert, Divider } from 'antd'
import { PhoneOutlined, GlobalOutlined, WarningOutlined, HeartOutlined } from '@ant-design/icons'
import { apiClient } from '../../utils/api'
import './index.css'

const { Title, Text, Paragraph } = Typography

export default function CrisisPage() {
  const [resources, setResources] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchResources()
  }, [])

  const fetchResources = async () => {
    try {
      const res = await apiClient.get('/auth/crisis-resources')
      setResources(res.data)
    } catch (error) {
      console.error('获取危机资源失败', error)
    } finally {
      setLoading(false)
    }
  }

  const callHotline = (number: string) => {
    window.location.href = `tel:${number.replace(/[^\d]/g, '')}`
  }

  const openUrl = (url: string) => {
    if (url) {
      window.open(url, '_blank')
    }
  }

  return (
    <div className="crisis-container">
      <Card loading={loading} className="crisis-card">
        {resources && (
          <>
            <div className="crisis-header">
              <Alert
                message="如果你或你身边的人正面临立即的生命危险，请立即拨打120或110求助。"
                type="error"
                showIcon
                icon={<WarningOutlined />}
              />
              <Title level={2} style={{ marginTop: 24 }}>
                <HeartOutlined /> {resources.title}
              </Title>
              <Text type="secondary">{resources.description}</Text>
            </div>

            <Divider />

            <div className="crisis-section">
              <Title level={4}>📞 危机干预热线</Title>
              <List
                dataSource={resources.hotlines}
                renderItem={(item: any) => (
                  <List.Item>
                    <div className="hotline-item">
                      <div className="hotline-info">
                        <Text strong>{item.name}</Text>
                        <br />
                        <Text type="secondary">{item.description}</Text>
                      </div>
                      <Button
                        type="primary"
                        icon={<PhoneOutlined />}
                        onClick={() => callHotline(item.number)}
                        danger
                      >
                        立即拨打
                      </Button>
                    </div>
                  </List.Item>
                )}
              />
            </div>

            <Divider />

            <div className="crisis-section">
              <Title level={4}>🌐 在线资源</Title>
              <List
                dataSource={resources.online_resources}
                renderItem={(item: any) => (
                  <List.Item>
                    <div className="online-item">
                      <div className="online-info">
                        <Text strong>{item.name}</Text>
                      </div>
                      {item.url && (
                        <Button
                          icon={<GlobalOutlined />}
                          onClick={() => openUrl(item.url)}
                        >
                          访问网站
                        </Button>
                      )}
                    </div>
                  </List.Item>
                )}
              />
          </div>

          <Divider />

          <div className="crisis-section">
            <Title level={4}>💡 自助建议</Title>
            <List
              dataSource={resources.self_help_tips}
              renderItem={(tip: string) => (
                <List.Item>
                  <div className="tip-item">
                    <Text>{tip}</Text>
                  </div>
                </List.Item>
              )}
            />
          </div>

          <Divider />

          <div className="crisis-footer">
            <Text type="secondary">
              记住：你不需要独自承受。寻求帮助不是软弱，而是勇敢的表现。很多人都经历过困难时期，专业的帮助能让你更快走出来。
            </Text>
          </div>
        </>
      )}
    </Card>
  </div>
)
}

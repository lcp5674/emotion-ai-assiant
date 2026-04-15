/**
 * 数据隐私说明页面
 * 明确告知用户数据隐私政策，增强信任
 */
import { useEffect, useState } from 'react'
import { Card, Typography, Divider, List, Tag, Space, Button } from 'antd'
import { Link } from 'react-router-dom'
import { ArrowLeftOutlined } from '@ant-design/icons'
import { apiClient } from '../../api/request'
import './index.css'

const { Title, Paragraph, Text } = Typography

export default function PrivacyPage() {
  const [privacy, setPrivacy] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchPrivacy()
  }, [])

  const fetchPrivacy = async () => {
    try {
      const res = await apiClient.get('/diary/privacy-policy')
      setPrivacy(res.data)
    } catch (error) {
      console.error('获取隐私政策失败', error)
    } finally {
      setLoading(false)
    }
  }

  const dataControls = [
    {
      action: 'export',
      title: '导出所有数据',
      description: '下载您存储在我们这里的所有个人数据，包括日记、对话等',
    },
    {
      action: 'delete_account',
      title: '删除账户',
      description: '永久删除您的账户和所有相关数据，操作不可逆',
    },
  ]

  return (
    <div className="privacy-container">
      <div style={{ marginBottom: 16 }}>
        <Link to="/">
          <Button icon={<ArrowLeftOutlined />}>返回首页</Button>
        </Link>
      </div>
      <Card className="privacy-card" loading={loading}>
        {privacy && (
          <>
            <div className="privacy-header">
              <Title level={2}>{privacy.title}</Title>
              <div className="privacy-meta">
                <Tag color="blue">版本 {privacy.version}</Tag>
                <Text type="secondary">最后更新：{privacy.last_updated}</Text>
              </div>
            </div>

            <div
              className="privacy-content"
              dangerouslySetInnerHTML={{ __html: privacy.content }}
            />

            <Divider />

            <div className="privacy-data-controls">
              <Title level={4}>您的数据控制权</Title>
              <Paragraph>
                您完全拥有您的数据，我们提供以下数据控制功能：
              </Paragraph>
              <List
                dataSource={dataControls}
                renderItem={(item) => (
                  <List.Item>
                    <div className="control-item">
                      <div className="control-info">
                        <Text strong>{item.title}</Text>
                        <br />
                        <Text type="secondary">{item.description}</Text>
                      </div>
                      <Tag color={item.action === 'delete_account' ? 'red' : 'green'}>
                        {item.action === 'export' ? '导出' : '删除'}
                      </Tag>
                    </div>
                  </List.Item>
                )}
              />
              <Paragraph type="secondary" style={{ marginTop: 16 }}>
                这些功能可以在个人设置页面找到
              </Paragraph>
            </div>

            <Divider />

            <div className="privacy-contact">
              <Text type="secondary">
                如果您对数据隐私有任何疑问，可以通过客服联系我们
              </Text>
            </div>
          </>
        )}
      </Card>
    </div>
  )
}

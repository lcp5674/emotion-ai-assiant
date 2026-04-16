import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Card, Row, Col, Tag, Spin, Empty, Button, message, Pagination } from 'antd'
import { ArrowLeftOutlined, HeartOutlined, EyeOutlined } from '@ant-design/icons'
import { api } from '../../api/request'

interface Article {
  id: number
  title: string
  summary?: string
  category: string
  tags?: string
  cover_image?: string
  author?: string
  view_count: number
  like_count: number
  created_at: string
}

export default function KnowledgeCollections() {
  const navigate = useNavigate()
  const [articles, setArticles] = useState<Article[]>([])
  const [loading, setLoading] = useState(true)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(12)

  useEffect(() => {
    loadCollections()
  }, [page])

  const loadCollections = async () => {
    setLoading(true)
    try {
      const res = await api.knowledge.collections({
        page,
        page_size: pageSize,
      })
      setArticles(res.list || [])
      setTotal(res.total || 0)
    } catch (error: any) {
      console.error(error)
      message.error(error.response?.data?.detail || '加载收藏失败')
    } finally {
      setLoading(false)
    }
  }

  const getCategoryColor = (cat: string) => {
    const colors: Record<string, string> = {
      emotion: 'red',
      relationship: 'orange',
      self_growth: 'green',
      psychology: 'blue',
      love: 'pink',
      family: 'purple',
    }
    return colors[cat] || 'default'
  }

  const categories = [
    { key: 'emotion', name: '情绪管理' },
    { key: 'relationship', name: '人际关系' },
    { key: 'self_growth', name: '个人成长' },
    { key: 'psychology', name: '心理知识' },
    { key: 'love', name: '恋爱心理' },
    { key: 'family', name: '家庭关系' },
  ]

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      {/* Header */}
      <header style={{
        background: 'linear-gradient(135deg, #722ed1 0%, #b37feb 100%)',
        padding: '40px 0',
        textAlign: 'center',
        color: '#fff',
      }}>
        <div className="container">
          <h1 style={{ fontSize: 36, marginBottom: 8 }}>我的收藏</h1>
          <p style={{ fontSize: 18, opacity: 0.9 }}>
            我收藏的心理知识文章
          </p>
        </div>
      </header>

      <div className="container" style={{ padding: '24px 16px' }}>
        {/* Back */}
        <div style={{ marginBottom: 16 }}>
          <Link to="/">
            <Button icon={<ArrowLeftOutlined />} type="text">
              返回首页
            </Button>
          </Link>
        </div>

        {/* Collections */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: 60 }}>
            <Spin size="large" />
          </div>
        ) : (
          <>
            <Row gutter={[24, 24]}>
              {articles.map((article) => (
                <Col xs={24} sm={12} lg={8} xl={6} key={article.id}>
                  <Card
                    hoverable
                    onClick={() => navigate(`/knowledge/${article.id}`)}
                    cover={
                      article.cover_image ? (
                        <div style={{
                          height: 160,
                          backgroundImage: `url(${article.cover_image})`,
                          backgroundSize: 'cover',
                          backgroundPosition: 'center',
                        }} />
                      ) : (
                        <div style={{
                          height: 160,
                          background: 'linear-gradient(135deg, #f0f5ff 0%, #e6f7ff 100%)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                        }}>
                          <span style={{ fontSize: 48, color: '#722ed1' }}>📖</span>
                        </div>
                      )
                    }
                  >
                    <Tag color={getCategoryColor(article.category)} style={{ marginBottom: 8 }}>
                      {categories.find(c => c.key === article.category)?.name || article.category}
                    </Tag>
                    <Card.Meta
                      title={<div style={{ fontSize: 16 }}>{article.title}</div>}
                      description={
                        <div>
                          <p style={{
                            color: '#8c8c8c',
                            fontSize: 13,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}>
                            {article.summary || article.title}
                          </p>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8, color: '#8c8c8c', fontSize: 12 }}>
                            <span><EyeOutlined /> {article.view_count}</span>
                            <span><HeartOutlined /> {article.like_count}</span>
                          </div>
                        </div>
                      }
                    />
                  </Card>
                </Col>
              ))}
            </Row>

            {articles.length === 0 && (
              <Empty
                description="暂无收藏"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              >
                <Link to="/knowledge">
                  <Button type="primary" style={{ background: '#722ed1' }}>
                    去知识库看看
                  </Button>
                </Link>
              </Empty>
            )}

            {total > pageSize && (
              <div style={{ textAlign: 'center', marginTop: 24 }}>
                <Pagination
                  current={page}
                  pageSize={pageSize}
                  total={total}
                  onChange={setPage}
                />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Card, Row, Col, Tag, Input, Spin, Pagination, Empty, Button } from 'antd'
import { SearchOutlined, EyeOutlined, LikeOutlined, ArrowLeftOutlined, BookOutlined } from '@ant-design/icons'
import { api } from '../../api/request'
import { useTheme } from '../../hooks/useTheme'

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

const categories = [
  { key: 'all', name: '全部' },
  { key: 'emotion', name: '情绪管理', gradient: ['#ef4444', '#f87171'] },
  { key: 'relationship', name: '人际关系', gradient: ['#f97316', '#fb923c'] },
  { key: 'self_growth', name: '个人成长', gradient: ['#10b981', '#34d399'] },
  { key: 'psychology', name: '心理知识', gradient: ['#3b82f6', '#60a5fa'] },
  { key: 'love', name: '恋爱心理', gradient: ['#ec4899', '#f472b6'] },
  { key: 'family', name: '家庭关系', gradient: ['#8b5cf6', '#a78bfa'] },
]

export default function Knowledge() {
  const navigate = useNavigate()
  const { themeColors, themeColor } = useTheme()
  const [articles, setArticles] = useState<Article[]>([])
  const [loading, setLoading] = useState(true)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(12)
  const [category, setCategory] = useState('all')
  const [searchKeyword, setSearchKeyword] = useState('')

  const themeGradient = themeColors[themeColor]

  useEffect(() => {
    loadArticles()
  }, [page, category])

  const loadArticles = async () => {
    setLoading(true)
    try {
      const res = await api.knowledge.articles({
        category: category === 'all' ? undefined : category,
        page,
        page_size: pageSize,
      })
      setArticles(res.list || [])
      setTotal(res.total || 0)
    } catch (error) {
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const getCategoryColor = (cat: string) => {
    const catInfo = categories.find(c => c.key === cat)
    return catInfo?.gradient || [themeGradient, themeGradient]
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f8fafc' }}>
      {/* Header */}
      <header style={{
        background: `linear-gradient(135deg, ${themeGradient} 0%, ${themeGradient}cc 100%)`,
        padding: '60px 24px',
        textAlign: 'center',
        color: '#fff',
        position: 'relative',
        overflow: 'hidden',
      }}>
        <div style={{
          position: 'absolute',
          top: '-30%',
          right: '-10%',
          width: '50%',
          height: '150%',
          background: 'radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%)',
          borderRadius: '50%',
        }} />
        <div style={{ position: 'relative', zIndex: 1 }}>
          <div style={{
            width: 80,
            height: 80,
            borderRadius: '24px',
            background: 'rgba(255,255,255,0.2)',
            backdropFilter: 'blur(10px)',
            margin: '0 auto 20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '2px solid rgba(255,255,255,0.3)',
          }}>
            <BookOutlined style={{ fontSize: 36, color: '#fff' }} />
          </div>
          <h1 style={{ fontSize: 36, marginBottom: 12, fontWeight: 700 }}>
            心理知识库
          </h1>
          <p style={{ fontSize: 18, opacity: 0.9, margin: 0 }}>
            丰富心理学知识，助你自我成长
          </p>
        </div>
      </header>

      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '24px 16px 60px' }}>
        {/* Back */}
        <Link to="/">
          <Button icon={<ArrowLeftOutlined />} style={{ borderRadius: 12, marginBottom: 20 }}>返回首页</Button>
        </Link>

        {/* Search */}
        <Card
          style={{
            marginBottom: 20,
            border: 'none',
            borderRadius: 20,
            boxShadow: '0 8px 30px rgba(0,0,0,0.08)',
          }}
          bodyStyle={{ padding: 20 }}
        >
          <Input
            placeholder="搜索文章..."
            prefix={<SearchOutlined style={{ color: themeGradient }} />}
            value={searchKeyword}
            onChange={(e) => setSearchKeyword(e.target.value)}
            allowClear
            size="large"
            style={{ borderRadius: 14 }}
          />
        </Card>

        {/* Category Tabs */}
        <div style={{
          display: 'flex',
          gap: 10,
          flexWrap: 'wrap',
          marginBottom: 24,
        }}>
          {categories.map((cat) => {
            const isActive = category === cat.key
            const colors = cat.gradient || [themeGradient, themeGradient]
            return (
              <Tag
                key={cat.key}
                onClick={() => setCategory(cat.key)}
                style={{
                  cursor: 'pointer',
                  borderRadius: 20,
                  padding: '8px 20px',
                  fontSize: 14,
                  border: isActive ? 'none' : '1px solid #e5e7eb',
                  background: isActive
                    ? `linear-gradient(135deg, ${colors[0]} 0%, ${colors[1]} 100%)`
                    : '#fff',
                  color: isActive ? '#fff' : '#6b7280',
                  fontWeight: isActive ? 600 : 400,
                  transition: 'all 0.2s ease',
                  boxShadow: isActive ? `0 4px 15px ${colors[0]}40` : 'none',
                }}
              >
                {cat.name}
              </Tag>
            )
          })}
        </div>

        {/* Articles Grid */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: 80 }}>
            <Spin size="large" />
          </div>
        ) : articles.length > 0 ? (
          <>
            <Row gutter={[20, 20]}>
              {articles.map((article) => {
                const colors = getCategoryColor(article.category)
                return (
                  <Col xs={24} sm={12} lg={8} xl={6} key={article.id}>
                    <Card
                      hoverable
                      onClick={() => navigate(`/knowledge/${article.id}`)}
                      style={{
                        border: 'none',
                        borderRadius: 20,
                        overflow: 'hidden',
                        boxShadow: '0 8px 30px rgba(0,0,0,0.08)',
                        transition: 'all 0.3s ease',
                      }}
                      bodyStyle={{ padding: 0 }}
                      onMouseEnter={(e) => {
                        (e.currentTarget as HTMLElement).style.transform = 'translateY(-8px)'
                        ;(e.currentTarget as HTMLElement).style.boxShadow = `0 20px 50px ${colors[0]}25`
                      }}
                      onMouseLeave={(e) => {
                        (e.currentTarget as HTMLElement).style.transform = 'translateY(0)'
                        ;(e.currentTarget as HTMLElement).style.boxShadow = '0 8px 30px rgba(0,0,0,0.08)'
                      }}
                    >
                      {/* Cover */}
                      <div style={{
                        height: 140,
                        background: article.cover_image
                          ? `url(${article.cover_image}) center/cover`
                          : `linear-gradient(135deg, ${colors[0]} 0%, ${colors[1]} 100%)`,
                        position: 'relative',
                      }}>
                        {!article.cover_image && (
                          <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            height: '100%',
                            fontSize: 48,
                          }}>
                            <BookOutlined style={{ color: 'rgba(255,255,255,0.8)' }} />
                          </div>
                        )}
                        <Tag
                          style={{
                            position: 'absolute',
                            top: 12,
                            right: 12,
                            background: 'rgba(255,255,255,0.95)',
                            color: colors[0],
                            borderRadius: 8,
                            fontSize: 11,
                            fontWeight: 600,
                            border: 'none',
                          }}
                        >
                          {categories.find(c => c.key === article.category)?.name || article.category}
                        </Tag>
                      </div>

                      {/* Content */}
                      <div style={{ padding: '16px 20px 20px' }}>
                        <h3 style={{
                          fontSize: 16,
                          fontWeight: 600,
                          marginBottom: 8,
                          color: '#1f2937',
                          lineHeight: 1.4,
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden',
                        }}>
                          {article.title}
                        </h3>
                        {article.summary && (
                          <p style={{
                            fontSize: 13,
                            color: '#6b7280',
                            lineHeight: 1.6,
                            marginBottom: 12,
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical',
                            overflow: 'hidden',
                          }}>
                            {article.summary}
                          </p>
                        )}
                        {article.tags && (
                          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 12 }}>
                            {article.tags.split(',').slice(0, 2).map((tag, i) => (
                              <Tag
                                key={i}
                                style={{
                                  background: '#f3f4f6',
                                  color: '#6b7280',
                                  borderRadius: 8,
                                  fontSize: 11,
                                  border: 'none',
                                }}
                              >
                                {tag.trim()}
                              </Tag>
                            ))}
                          </div>
                        )}
                        <div style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          color: '#9ca3af',
                          fontSize: 12,
                        }}>
                          <div style={{ display: 'flex', gap: 12 }}>
                            <span><EyeOutlined /> {article.view_count}</span>
                            <span><LikeOutlined /> {article.like_count}</span>
                          </div>
                          <span>
                            {new Date(article.created_at).toLocaleDateString('zh-CN')}
                          </span>
                        </div>
                      </div>
                    </Card>
                  </Col>
                )
              })}
            </Row>

            {/* Pagination */}
            <div style={{ textAlign: 'center', marginTop: 40 }}>
              <Pagination
                current={page}
                total={total}
                pageSize={pageSize}
                onChange={setPage}
                showSizeChanger={false}
                style={{ display: 'inline-block' }}
              />
            </div>
          </>
        ) : (
          <Card
            style={{
              textAlign: 'center',
              padding: '60px 20px',
              border: 'none',
              borderRadius: 20,
            }}
          >
            <BookOutlined style={{ fontSize: 48, color: '#d1d5db', marginBottom: 16 }} />
            <h3 style={{ color: '#6b7280', marginBottom: 8 }}>暂无文章</h3>
            <p style={{ color: '#9ca3af', fontSize: 14 }}>试试其他分类或搜索条件</p>
          </Card>
        )}
      </div>
    </div>
  )
}

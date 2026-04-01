import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { Card, Tag, Spin, Button, Divider } from 'antd'
import { ArrowLeftOutlined, EyeOutlined, LikeOutlined, StarOutlined } from '@ant-design/icons'
import { api } from '../../api/request'

export default function ArticleDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [article, setArticle] = useState<any>(null)
  const [related, setRelated] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [isCollected, setIsCollected] = useState(false)

  useEffect(() => {
    if (id) {
      loadArticle(Number(id))
    }
  }, [id])

  const loadArticle = async (articleId: number) => {
    setLoading(true)
    try {
      const res = await api.knowledge.articleDetail(articleId)
      setArticle(res.article)
      setRelated(res.related_articles || [])
    } catch (error) {
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleCollect = async () => {
    if (!article) return
    try {
      const res = await api.knowledge.collect(article.id)
      setIsCollected(res.is_collected)
    } catch (error) {
      console.error(error)
    }
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <Spin size="large" />
      </div>
    )
  }

  if (!article) {
    return (
      <div style={{ textAlign: 'center', padding: 60 }}>
        <h2>文章不存在</h2>
        <Link to="/knowledge">
          <Button type="primary" style={{ marginTop: 16, background: '#722ed1' }}>
            返回知识库
          </Button>
        </Link>
      </div>
    )
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5', paddingBottom: 40 }}>
      {/* Header */}
      <header style={{
        background: '#fff',
        padding: '16px 0',
        boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Link to="/knowledge">
            <Button icon={<ArrowLeftOutlined />} type="text">
              返回知识库
            </Button>
          </Link>
          <div style={{ display: 'flex', gap: 16 }}>
            <span style={{ color: '#8c8c8c' }}>
              <EyeOutlined /> {article.view_count}
            </span>
            <span style={{ color: '#8c8c8c' }}>
              <LikeOutlined /> {article.like_count}
            </span>
          </div>
        </div>
      </header>

      <div className="container" style={{ padding: '24px 16px' }}>
        <Card>
          {/* Title */}
          <h1 style={{ fontSize: 28, marginBottom: 16 }}>{article.title}</h1>

          {/* Meta */}
          <div style={{ display: 'flex', gap: 16, marginBottom: 24, color: '#8c8c8c' }}>
            {article.author && <span>作者: {article.author}</span>}
            <span>{new Date(article.created_at).toLocaleDateString()}</span>
            {article.category && <Tag color="purple">{article.category}</Tag>}
          </div>

          {/* Tags */}
          {article.tags && (
            <div style={{ marginBottom: 24 }}>
              {article.tags.split(',').map((tag: string, i: number) => (
                <Tag key={i} style={{ marginBottom: 8 }}>{tag}</Tag>
              ))}
            </div>
          )}

          <Divider />

          {/* Content */}
          <div style={{ lineHeight: 2, fontSize: 16, color: '#262626' }}>
            {article.content ? (
              <div dangerouslySetInnerHTML={{ __html: article.content }} />
            ) : (
              <p>{article.summary || '暂无内容'}</p>
            )}
          </div>

          {/* Actions */}
          <div style={{ marginTop: 32, display: 'flex', gap: 16 }}>
            <Button
              icon={<StarOutlined />}
              onClick={handleCollect}
              type={isCollected ? 'primary' : 'default'}
              style={{ background: isCollected ? '#722ed1' : undefined }}
            >
              {isCollected ? '已收藏' : '收藏'}
            </Button>
          </div>
        </Card>

        {/* Related Articles */}
        {related.length > 0 && (
          <Card title="相关文章" style={{ marginTop: 24 }}>
            {related.map((item) => (
              <div
                key={item.id}
                style={{
                  padding: '12px 0',
                  borderBottom: '1px solid #f0f0f0',
                  cursor: 'pointer',
                }}
                onClick={() => navigate(`/knowledge/${item.id}`)}
              >
                <div style={{ fontSize: 16, marginBottom: 4 }}>{item.title}</div>
                <div style={{ color: '#8c8c8c', fontSize: 13 }}>
                  {item.summary?.slice(0, 100)}...
                </div>
              </div>
            ))}
          </Card>
        )}
      </div>
    </div>
  )
}
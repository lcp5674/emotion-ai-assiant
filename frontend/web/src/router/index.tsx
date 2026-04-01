// 路由类型定义
export interface RouteConfig {
  path: string
  element: React.ReactElement
  children?: RouteConfig[]
}

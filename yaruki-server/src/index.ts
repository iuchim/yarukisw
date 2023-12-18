import { Hono } from 'hono'
import { basicAuth } from 'hono/basic-auth'

// コンテキストの型
// 設定した情報はこの型に紐付けられる
type Bindings = {
  state_kv: KVNamespace,
  username: string,
  password: string,
}

const app = new Hono<{Bindings: Bindings}>()

// Basic 認証
app.use('*', async (c, next) => {
  const auth = basicAuth({
    username: c.env.username,
    password: c.env.password
  })
  return auth(c, next)
})

// prefix を指定して取得
app.get('/states/:prefix', async (c) => {
  const prefix = c.req.param('prefix')
  const list = await c.env.state_kv.list({ prefix })
  const results = await Promise.all(list.keys.map(async key => {
    const value = await c.env.state_kv.get(key.name)
    const timestamp = Number(key.name.replace(/^.*:/, ''))
    return { key: key.name, value, timestamp }
  }))
  return c.json({ ok: true, results })
})

// 現在時刻の状態を登録
app.post('/states/now', async (c) => {
  const param = await c.req.json()
  const value = String(param?.state ?? '')
  const now = new Date()
  const timestamp = now.getTime()
  const key = now.toLocaleString('sv-SE', { timeZone: 'Asia/Tokyo' })
    .replace(/[ \-:]/g, '') + ':' + timestamp
  await c.env.state_kv.put(key, value)
  return c.json({ ok: true, timestamp, key, value }, 201)
})

export default app

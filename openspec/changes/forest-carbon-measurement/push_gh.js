// 把指定本機檔推到 GitHub repo（重用 githubSyncService 的 token / repo 設定）
// Usage: node push_gh.js <repoPath> <localFile> "<commit msg>"
require('dotenv').config()
const fs = require('fs')
const REPO = process.env.GITHUB_REPO || 'Yuchiaoniu/forest-carbon-measurement'
const BRANCH = process.env.GITHUB_BRANCH || 'master'
const TOKEN = process.env.GITHUB_TOKEN

async function gh(method, p, body) {
  return fetch(`https://api.github.com${p}`, {
    method,
    headers: { Authorization: `token ${TOKEN}`, Accept: 'application/vnd.github.v3+json', 'Content-Type': 'application/json', 'User-Agent': 'forest-carbon-measurement' },
    body: body ? JSON.stringify(body) : undefined,
  })
}
async function upsert(repoPath, localFile, msg) {
  const content = fs.readFileSync(localFile).toString('base64')
  let sha = null
  const g = await gh('GET', `/repos/${REPO}/contents/${repoPath}?ref=${BRANCH}`)
  if (g.ok) sha = (await g.json()).sha
  const r = await gh('PUT', `/repos/${REPO}/contents/${repoPath}`, { message: msg, content, branch: BRANCH, ...(sha ? { sha } : {}) })
  if (!r.ok) { const e = await r.json().catch(() => ({})); throw new Error(e.message || `HTTP ${r.status}`) }
  console.log(`pushed ${repoPath} → ${sha ? 'updated' : 'created'}`)
}
;(async () => {
  if (!TOKEN) { console.error('no GITHUB_TOKEN in .env'); process.exit(1) }
  const [repoPath, localFile, msg] = process.argv.slice(2)
  if (!repoPath || !localFile) { console.error('usage: node push_gh.js <repoPath> <localFile> "<msg>"'); process.exit(1) }
  await upsert(repoPath, localFile, msg || 'update')
  console.log('DONE')
})().catch(e => { console.error('FATAL', e.message); process.exit(1) })

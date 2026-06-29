// One-shot: fill missing env_context + Story A + regenerate latest Story C
require('dotenv').config()
const Database = require('better-sqlite3')
const db = new Database('data.db')

const { persistEnvironmentContext } = require('./src/services/weatherService')
const { generateStoryA, generateStoryC } = require('./src/services/storyService')
const { insert: insertStory } = require('./src/db/stories')
const { setStoryC, getTreesInEvent } = require('./src/db/events')
const { pushTreesJson } = require('./src/services/githubSyncService')

const EVENT_ID = '6138fc64-6670-42a7-bd38-4dfe8c02cf12'

const TREES_NEED_ENV = [
  '32b07239-e856-42bd-9ef1-09978d79013a', // IMG_5800
  'e06aa4b9-7d83-43a1-a98c-9c6e69221c6f', // IMG_5807
  '3eaea6f9-02a9-4dae-95a0-dba4fbcd3d50', // IMG_5819
]

const TREES_NEED_STORY_A = [
  '39a452d7-18e1-49a5-8e60-1c4c3931d8b0', // IMG_5793 (has env, missing A)
  '32b07239-e856-42bd-9ef1-09978d79013a', // IMG_5800
  'e06aa4b9-7d83-43a1-a98c-9c6e69221c6f', // IMG_5807
  '3eaea6f9-02a9-4dae-95a0-dba4fbcd3d50', // IMG_5819
]

async function main() {
  console.log('=== fill-missing start ===')

  // === Phase 1: env_context ===
  console.log('\n--- Phase 1: persistEnvironmentContext ---')
  const treeStmt = db.prepare('SELECT id, video_original_name, gps, create_date, altitude_m FROM trees WHERE id = ?')
  for (const treeId of TREES_NEED_ENV) {
    const t = treeStmt.get(treeId)
    if (!t) { console.warn('  tree not found:', treeId); continue }
    let lat = null, lng = null
    if (t.gps && typeof t.gps === 'string') {
      const m = t.gps.match(/^(-?[0-9.]+),\s*(-?[0-9.]+)$/)
      if (m) { lat = parseFloat(m[1]); lng = parseFloat(m[2]) }
    }
    const ts = t.create_date || Math.floor(Date.now() / 1000)
    try {
      await persistEnvironmentContext(treeId, lat, lng, ts, t.altitude_m ?? null)
      console.log(`  OK env: ${t.video_original_name} (${treeId.slice(0,8)})`)
    } catch (e) {
      console.warn(`  FAIL env: ${t.video_original_name}: ${e.message}`)
    }
  }

  // === Phase 2: Story A for trees missing it ===
  console.log('\n--- Phase 2: generateStoryA ---')
  for (const treeId of TREES_NEED_STORY_A) {
    const t = treeStmt.get(treeId)
    if (!t) { console.warn('  tree not found:', treeId); continue }
    try {
      const storyA = await generateStoryA(treeId)
      if (storyA) {
        insertStory({
          treeId,
          eventId: EVENT_ID,
          storyType: 'A',
          markdown: storyA.markdown,
          summary: storyA.summary,
          weatherSnapshot: storyA.weather,
        })
        console.log(`  OK story A: ${t.video_original_name} (${treeId.slice(0,8)})`)
      } else {
        console.warn(`  empty story A returned for ${t.video_original_name}`)
      }
    } catch (e) {
      console.warn(`  FAIL story A: ${t.video_original_name}: ${e.message}`)
    }
  }

  // === Phase 3: regenerate latest Story C ===
  console.log('\n--- Phase 3: generateStoryC (latest version) ---')
  try {
    const treesInEvent = getTreesInEvent(EVENT_ID)
    console.log(`  event has ${treesInEvent.length} trees`)
    const storyC = await generateStoryC(EVENT_ID)
    if (storyC) {
      insertStory({ eventId: EVENT_ID, storyType: 'C', markdown: storyC })
      setStoryC(EVENT_ID, storyC)
      console.log(`  OK story C regenerated (${storyC.length} chars)`)
    } else {
      console.warn('  empty story C returned')
    }
  } catch (e) {
    console.warn(`  FAIL story C: ${e.message}`)
  }

  // === Phase 4: pushTreesJson ===
  console.log('\n--- Phase 4: pushTreesJson ---')
  try {
    await pushTreesJson()
    console.log('  OK pushed to GitHub')
  } catch (e) {
    console.warn(`  FAIL push: ${e.message}`)
  }

  console.log('\n=== fill-missing done ===')
  db.close()
}

main().catch(e => { console.error('FATAL:', e); process.exit(1) })

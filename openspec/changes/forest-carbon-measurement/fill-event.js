// Phase 5: assign 3 orphan trees to the event, then regenerate Story C
require('dotenv').config()
const Database = require('better-sqlite3')
const db = new Database('data.db')

const { assignToEvent } = require('./src/services/clusterService')
const { generateStoryC } = require('./src/services/storyService')
const { insert: insertStory } = require('./src/db/stories')
const { setStoryC, getTreesInEvent } = require('./src/db/events')
const { pushTreesJson } = require('./src/services/githubSyncService')

const EVENT_ID = '6138fc64-6670-42a7-bd38-4dfe8c02cf12'
const ORPHANS = [
  '32b07239-e856-42bd-9ef1-09978d79013a', // IMG_5800
  'e06aa4b9-7d83-43a1-a98c-9c6e69221c6f', // IMG_5807
  '3eaea6f9-02a9-4dae-95a0-dba4fbcd3d50', // IMG_5819
]

async function main() {
  console.log('=== fill-event start ===')
  console.log('before:', getTreesInEvent(EVENT_ID).length, 'trees in event')

  for (const treeId of ORPHANS) {
    try {
      const { eventId, isNew } = assignToEvent(treeId)
      console.log(`  ${treeId.slice(0,8)} → event=${eventId.slice(0,8)} isNew=${isNew}`)
    } catch (e) {
      console.warn(`  FAIL assign ${treeId.slice(0,8)}: ${e.message}`)
    }
  }

  console.log('after:', getTreesInEvent(EVENT_ID).length, 'trees in event')

  console.log('\n--- regenerate Story C (final 31-tree version) ---')
  const storyC = await generateStoryC(EVENT_ID)
  if (storyC) {
    insertStory({ eventId: EVENT_ID, storyType: 'C', markdown: storyC })
    setStoryC(EVENT_ID, storyC)
    console.log(`  OK story C (${storyC.length} chars)`)
  }

  console.log('\n--- push ---')
  await pushTreesJson()
  console.log('  OK')
  console.log('=== done ===')
  db.close()
}
main().catch(e => { console.error('FATAL:', e); process.exit(1) })

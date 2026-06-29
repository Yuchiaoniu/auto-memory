const { ethers } = require('ethers')

const ABI = [
  'function recordMeasurement(string gps, string species, uint32 dbhMm, uint32 volumeCm3x100, uint32 carbonG, bytes32 videoHash, uint256 localTreeId, uint32 originalDbhMm, uint32 correctionFactorX10000) returns (uint256)',
  'function getMeasurement(uint256 id) view returns (tuple(string gps, string species, uint32 dbhMm, uint32 volumeCm3x100, uint32 carbonG, bytes32 videoHash, uint256 timestamp, uint256 localTreeId, uint32 originalDbhMm, uint32 correctionFactorX10000))',
  'event MeasurementRecorded(uint256 indexed id, string gps, string species, uint32 dbhMm, uint32 volumeCm3x100, uint32 carbonG, bytes32 videoHash, uint256 timestamp, uint256 localTreeId, uint32 originalDbhMm, uint32 correctionFactorX10000)',
]

const GROUND_TRUTH_ABI = [
  'function recordGroundTruth(bytes32 videoHash, uint32 manualTapeDbhMm) returns (uint256)',
  'event GroundTruthRecorded(uint256 indexed id, bytes32 indexed videoHash, uint32 manualTapeDbhMm, uint256 timestamp)',
]

let contract
let gtContract

function getProvider() {
  return new ethers.JsonRpcProvider(process.env.BESU_RPC_URL)
}
function getWallet() {
  const provider = getProvider()
  return new ethers.Wallet(process.env.SIGNER_PRIVATE_KEY || process.env.DEPLOYER_PRIVATE_KEY, provider)
}

function getContract() {
  if (!contract) {
    contract = new ethers.Contract(process.env.CONTRACT_ADDRESS, ABI, getWallet())
  }
  return contract
}

function getGroundTruthContract() {
  if (!gtContract) {
    if (!process.env.GROUND_TRUTH_CONTRACT_ADDRESS) {
      throw new Error('GROUND_TRUTH_CONTRACT_ADDRESS 未設定')
    }
    gtContract = new ethers.Contract(process.env.GROUND_TRUTH_CONTRACT_ADDRESS, GROUND_TRUTH_ABI, getWallet())
  }
  return gtContract
}

function encodeVideoHash(videoHash) {
  return ethers.zeroPadBytes(ethers.toUtf8Bytes(String(videoHash || '').slice(0, 32)), 32)
}

async function recordMeasurement({ gps, species, dbhCm, volumeM3, carbonKg, videoHash, treeId, originalDbhCm, appliedCorrectionFactor }) {
  const c = getContract()
  const dbhMm             = Math.round(dbhCm * 10)
  const volumeCm3x100     = Math.round(volumeM3 * 1e6)
  const carbonG           = Math.round(carbonKg * 1000)
  const localTreeId       = (() => { try { return BigInt(treeId || 0) } catch { return 0n } })()
  const originalDbhMm         = originalDbhCm ? Math.round(originalDbhCm * 10) : 0
  const correctionFactorX10000 = appliedCorrectionFactor ? Math.round(appliedCorrectionFactor * 10000) : 0

  const tx = await c.recordMeasurement(
    gps || '', species || 'unknown',
    dbhMm, volumeCm3x100, carbonG,
    encodeVideoHash(videoHash),
    localTreeId,
    originalDbhMm,
    correctionFactorX10000
  )
  const receipt = await tx.wait()
  return receipt.hash
}

async function recordGroundTruth({ videoHash, manualTapeDbhCm }) {
  const c = getGroundTruthContract()
  const dbhMm = Math.round(manualTapeDbhCm * 10)
  const tx = await c.recordGroundTruth(encodeVideoHash(videoHash), dbhMm)
  const receipt = await tx.wait()
  return receipt.hash
}

module.exports = { recordMeasurement, recordGroundTruth }

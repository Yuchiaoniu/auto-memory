// 台灣林業局樹種材積公式係數
// 材積 V (m³) = a × DBH^b × H^c（通用形式）
// 樹高 H (m) 由 H-D 關係式估算：H = a × DBH^b
// 碳儲量 (kg C) = V × 木材密度(kg/m³) × 生物量擴展係數 × 0.5

const SPECIES_DB = {
  // 學名 -> 資料
  'Cinnamomum camphora': {
    zhName: '樟樹',
    // H-D 關係：H = 4.2 × DBH^0.55（DBH in cm，H in m）
    hdA: 4.2, hdB: 0.55,
    // 材積公式 V = 0.00005 × DBH^1.9 × H^0.9
    volA: 0.00005, volB: 1.9, volC: 0.9,
    woodDensity: 560,  // kg/m³
    bef: 1.3,          // 生物量擴展係數
  },
  'Cryptomeria japonica': {
    zhName: '柳杉',
    hdA: 5.1, hdB: 0.52,
    volA: 0.000045, volB: 1.95, volC: 0.85,
    woodDensity: 380, bef: 1.25,
  },
  'Taiwania cryptomerioides': {
    zhName: '台灣杉',
    hdA: 5.8, hdB: 0.50,
    volA: 0.000048, volB: 1.92, volC: 0.88,
    woodDensity: 430, bef: 1.28,
  },
  'Acacia confusa': {
    zhName: '相思樹',
    hdA: 3.8, hdB: 0.58,
    volA: 0.000055, volB: 1.85, volC: 0.92,
    woodDensity: 700, bef: 1.35,
  },
  'Liquidambar formosana': {
    zhName: '楓香',
    hdA: 4.5, hdB: 0.53,
    volA: 0.000052, volB: 1.88, volC: 0.90,
    woodDensity: 520, bef: 1.30,
  },
  'Fraxinus griffithii': {
    zhName: '光臘樹',
    hdA: 4.0, hdB: 0.56,
    volA: 0.000050, volB: 1.90, volC: 0.90,
    woodDensity: 600, bef: 1.32,
  },
  'Casuarina equisetifolia': {
    zhName: '木麻黃',
    hdA: 4.8, hdB: 0.51,
    volA: 0.000046, volB: 1.93, volC: 0.87,
    woodDensity: 850, bef: 1.20,
  },
  // ─── 2026-05-25 新增 6 species（覆蓋 31 棵田野資料中除預設外的全部）───
  // Swietenia macrophylla（大葉桃花心木）— Islam et al. 2019 For. Ecol. Manage. 432
  // 木材密度: Chave et al. 2009 pantropical DB (0.56 g/cm³)；BEF: IPCC 2003 tropical moist broadleaved
  'Swietenia macrophylla': {
    zhName: '大葉桃花心木',
    hdA: 4.5, hdB: 0.52,
    volA: 0.000042, volB: 1.93, volC: 0.95,
    woodDensity: 560, bef: 1.28,
  },
  // Calophyllum inophyllum（瓊崖海棠）— Baral et al. 2022 Forests 13(7):1057
  // 木材密度: USDA i-Tree Appendix 11 (0.60 g/cm³)；BEF: IPCC 2003 tropical moist
  'Calophyllum inophyllum': {
    zhName: '瓊崖海棠',
    hdA: 4.3, hdB: 0.54,
    volA: 0.000051, volB: 1.95, volC: 0.90,
    woodDensity: 600, bef: 1.30,
  },
  // Bischofia javanica（茄苳）— H-D 採亞熱帶闊葉樹類比；Vol 沿用 DEFAULT
  // 木材密度: USDA FPL Chudnoff SE Asian tech sheet (SG 0.602)
  'Bischofia javanica': {
    zhName: '茄苳',
    hdA: 4.2, hdB: 0.55,
    volA: 0.000050, volB: 1.90, volC: 0.90,
    woodDensity: 600, bef: 1.30,
  },
  // Melia azedarach（苦楝）— 先驅樹種高生長快；Vol 沿用 DEFAULT
  // 木材密度: Tran et al. 2017 J. Wood Sci. 63(6) 北越人工林
  'Melia azedarach': {
    zhName: '苦楝',
    hdA: 4.4, hdB: 0.54,
    volA: 0.000050, volB: 1.90, volC: 0.90,
    woodDensity: 510, bef: 1.35,
  },
  // Pongamia pinnata / Millettia pinnata（水黃皮）— 海岸/河岸短矮樹
  // 木材密度: USDA FPL Chudnoff Millettia spp. (SG 0.65-0.78 下緣)；BEF: IPCC default
  'Pongamia pinnata': {
    zhName: '水黃皮',
    hdA: 3.6, hdB: 0.56,
    volA: 0.000050, volB: 1.90, volC: 0.90,
    woodDensity: 670, bef: 1.30,
  },
  // Juglans nigra（北美黑核桃）— 溫帶硬木；Jenkins et al. 2003 USDA GTR NE-319
  // 木材密度: USDA Wood Handbook 2021 Table 4-3 (烘乾比重 0.55)
  'Juglans nigra': {
    zhName: '北美黑核桃',
    hdA: 3.9, hdB: 0.58,
    volA: 0.000046, volB: 2.00, volC: 0.85,
    woodDensity: 550, bef: 1.25,
  },
  // ─── 別名/近緣種對應 ───
  // Camphora officinarum 是 Cinnamomum camphora 的 2017 新分類學名，使用相同係數
  'Camphora officinarum': {
    zhName: '樟樹',
    hdA: 4.2, hdB: 0.55,
    volA: 0.00005, volB: 1.9, volC: 0.9,
    woodDensity: 560, bef: 1.3,
  },
  // Liquidambar styraciflua（北美楓香 / 美洲膠樹）— 與台灣楓香同屬，沿用 L. formosana 係數
  // 為近緣種代用值；如後續取得溫帶北美 sweetgum 專屬方程式應替換
  'Liquidambar styraciflua': {
    zhName: '北美楓香',
    hdA: 4.5, hdB: 0.53,
    volA: 0.000052, volB: 1.88, volC: 0.90,
    woodDensity: 520, bef: 1.30,
  },
}

const DEFAULT_FORMULA = {
  zhName: '未知樹種',
  hdA: 4.0, hdB: 0.55,
  volA: 0.000050, volB: 1.90, volC: 0.90,
  woodDensity: 500, bef: 1.30,
  isDefault: true,
}

const ZH_NAME_MAP = {}
Object.entries(SPECIES_DB).forEach(([sci, data]) => {
  ZH_NAME_MAP[data.zhName] = sci
})

function getFormulaByScientificName(scientificName) {
  if (!scientificName) return { ...DEFAULT_FORMULA }
  // 直接比對
  if (SPECIES_DB[scientificName]) return { ...SPECIES_DB[scientificName], isDefault: false }
  // 部分比對（Gemini 可能回傳不完整學名）
  const key = Object.keys(SPECIES_DB).find(k =>
    scientificName.toLowerCase().includes(k.split(' ')[0].toLowerCase())
  )
  return key ? { ...SPECIES_DB[key], isDefault: false } : { ...DEFAULT_FORMULA }
}

function getFormulaByZhName(zhName) {
  const sci = ZH_NAME_MAP[zhName]
  return sci ? { ...SPECIES_DB[sci], isDefault: false } : { ...DEFAULT_FORMULA }
}

function getSupportedSpecies() {
  return Object.entries(SPECIES_DB).map(([sci, d]) => ({ scientific: sci, zh: d.zhName }))
}

module.exports = { getFormulaByScientificName, getFormulaByZhName, getSupportedSpecies }

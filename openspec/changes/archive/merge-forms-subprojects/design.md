## Context

form-automation-system 是一套 Flask + SQLite + Google Forms API 的自動化表單系統，部署在 GCP VM（forest-carbon.duckdns.org/forms/）。開發過程中，每個憑證方案迭代都產生了獨立的 OpenSpec 子專案，導致主專案缺少架構記錄，且待辦的 ADC VM 部署步驟散落在子專案中。

## Goals / Non-Goals

**Goals:**
- 在主專案建立 memory.md，保存四代憑證演進決策與現行架構
- 將 ADC 部署待辦任務整合進主專案 tasks.md
- 更新 STATE.md 反映真實現況

**Non-Goals:**
- 不修改任何程式碼
- 不合併廢棄方案（SA、OAuth、GAS）的部署步驟
- 不重新設計系統架構

## Decisions

**memory.md 只記錄決策結論，不記錄廢棄方案的操作細節**
廢棄方案（SA、OAuth、GAS）只需要知道「曾試過、被取代」，操作細節已在封存的子專案中，不需要搬進來。

**ADC 部署步驟完整合併，不只摘要**
forms-adc-setup 的 3.1–4.2 共 7 個步驟是可執行的待辦，直接複製，不改寫。

## Risks / Trade-offs

- [風險] 子專案封存後，若需要查閱廢棄方案的完整操作記錄，需要到 archive/ 目錄找 → 緩解：memory.md 中標記「詳見 archive/forms-gas-integration 等」

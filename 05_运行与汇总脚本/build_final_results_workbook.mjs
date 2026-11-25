import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const base = process.env.BOOKSIM_RESULTS_DIR || path.resolve(scriptDir, "../01_最终汇总");
const outputPath = path.join(base, "BookSim_final_results_20260812.xlsx");

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') {
        field += '"';
        i += 1;
      } else if (ch === '"') {
        quoted = false;
      } else {
        field += ch;
      }
    } else if (ch === '"') {
      quoted = true;
    } else if (ch === ",") {
      row.push(field);
      field = "";
    } else if (ch === "\n") {
      row.push(field.replace(/\r$/, ""));
      rows.push(row);
      row = [];
      field = "";
    } else {
      field += ch;
    }
  }
  if (field.length || row.length) {
    row.push(field.replace(/\r$/, ""));
    rows.push(row);
  }
  return rows;
}

const numericHeaders = new Set([
  "endpoints", "injection_rate", "total_runs", "stable_runs", "unstable_runs", "failed_runs",
  "mean_latency_cycles", "std_latency_cycles", "ci95_latency_cycles", "mean_accepted_rate",
  "seed", "latency", "injected_rate", "accepted_rate", "mean_latency", "std_latency", "ci95_latency",
]);

function typedRows(rows) {
  const headers = rows[0];
  return rows.map((row, rowIndex) => row.map((value, colIndex) => {
    if (rowIndex === 0 || value === "" || !numericHeaders.has(headers[colIndex])) return value;
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : value;
  }));
}

function styleTable(sheet, matrix, tableName) {
  const rowCount = matrix.length;
  const colCount = matrix[0].length;
  const used = sheet.getRangeByIndexes(0, 0, rowCount, colCount);
  used.values = matrix;
  const header = sheet.getRangeByIndexes(0, 0, 1, colCount);
  header.format = {
    fill: "#245B78",
    font: { bold: true, color: "#FFFFFF" },
    wrapText: true,
    verticalAlignment: "center",
    borders: { preset: "outside", style: "thin", color: "#173B4D" },
  };
  header.format.rowHeight = 32;
  if (rowCount > 1) {
    sheet.getRangeByIndexes(1, 0, rowCount - 1, colCount).format.borders = {
      insideHorizontal: { style: "thin", color: "#E2E8EC" },
    };
  }
  sheet.tables.add(`A1:${columnName(colCount)}${rowCount}`, true, tableName);
  sheet.freezePanes.freezeRows(1);
  sheet.showGridLines = false;
  used.format.autofitColumns();
  for (let col = 0; col < colCount; col += 1) {
    const width = Math.min(Math.max(sheet.getRangeByIndexes(0, col, rowCount, 1).format.columnWidth, 10), 24);
    sheet.getRangeByIndexes(0, col, rowCount, 1).format.columnWidth = width;
  }
  const headers = matrix[0];
  for (let col = 0; col < headers.length; col += 1) {
    const name = headers[col];
    const dataRange = rowCount > 1 ? sheet.getRangeByIndexes(1, col, rowCount - 1, 1) : null;
    if (!dataRange) continue;
    if (name === "injection_rate" || name === "mean_accepted_rate" || name === "injected_rate" || name === "accepted_rate") {
      dataRange.format.numberFormat = "0.000";
    } else if (name.includes("latency")) {
      dataRange.format.numberFormat = "0.000";
    } else if (["endpoints", "total_runs", "stable_runs", "unstable_runs", "failed_runs", "seed"].includes(name)) {
      dataRange.format.numberFormat = "0";
    }
  }
}

function columnName(count) {
  let n = count;
  let name = "";
  while (n > 0) {
    n -= 1;
    name = String.fromCharCode(65 + (n % 26)) + name;
    n = Math.floor(n / 26);
  }
  return name;
}

const workbook = Workbook.create();
const readme = workbook.worksheets.add("README");
readme.showGridLines = false;
readme.getRange("A1:B1").merge();
readme.getRange("A1").values = [["BookSim Traffic-Skew Experiment Results"]];
readme.getRange("A1:B1").format = {
  fill: "#163D4F",
  font: { bold: true, color: "#FFFFFF", size: 16 },
  verticalAlignment: "center",
};
readme.getRange("A1:B1").format.rowHeight = 34;
readme.getRange("A3:B11").values = [
  ["Item", "Definition"],
  ["Main comparison", "Mesh, Torus, and Fat-Tree; 64 endpoints each"],
  ["Supplementary result", "Dragonfly; 72 endpoints because the BookSim configuration cannot instantiate 64"],
  ["Traffic patterns", "Uniform random and 20% hotspot to node 0"],
  ["Seeds", "101, 202, 303, 404, 505"],
  ["Common injection rates", "0.02, 0.04, 0.06, 0.07, 0.075, 0.08, 0.10 flits/node/cycle"],
  ["Error bars", "Two-sided 95% confidence interval using Student's t, df=4"],
  ["Unstable", "BookSim reported Simulation unstable; latency is intentionally blank, not zero"],
  ["Dragonfly scan", "Seed 101 only; used to locate the hotspot saturation boundary, not as a five-seed mean"],
];
readme.getRange("A3:B3").format = { fill: "#DCEAF0", font: { bold: true, color: "#163D4F" } };
readme.getRange("A3:B11").format.borders = { insideHorizontal: { style: "thin", color: "#D7E0E5" }, outside: { style: "thin", color: "#9FB4BF" } };
readme.getRange("A3:B11").format.wrapText = true;
readme.getRange("A:A").format.columnWidth = 25;
readme.getRange("B:B").format.columnWidth = 75;
readme.getRange("A3:B11").format.autofitRows();

const sheets = [
  ["Main64Summary", "main_64endpoint_summary.csv", "Main64SummaryTable"],
  ["AllSummary", "all_topologies_summary.csv", "AllSummaryTable"],
  ["MeshTorusRaw", "mesh_torus_raw_runs.csv", "MeshTorusRawTable"],
  ["FatTreeRaw", "fattree64_raw_runs.csv", "FatTreeRawTable"],
  ["DragonflyRaw", "dragonfly72_raw_runs.csv", "DragonflyRawTable"],
  ["DragonflyScan", "dragonfly72_hotspot_boundary_scan.csv", "DragonflyScanTable"],
];

for (const [sheetName, fileName, tableName] of sheets) {
  const text = await fs.readFile(path.join(base, fileName), "utf8");
  const matrix = typedRows(parseCsv(text));
  const sheet = workbook.worksheets.add(sheetName);
  styleTable(sheet, matrix, tableName);
}

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);

const check = await workbook.inspect({
  kind: "table",
  range: "Main64Summary!A1:N8",
  include: "values,formulas",
  tableMaxRows: 8,
  tableMaxCols: 14,
  maxChars: 5000,
});
console.log(check.ndjson);
const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "formula error scan",
});
console.log(errors.ndjson);
const preview = await workbook.render({ sheetName: "README", range: "A1:B11", scale: 1.5, format: "png" });
await fs.writeFile(path.join(base, "workbook_readme_preview.png"), new Uint8Array(await preview.arrayBuffer()));
console.log(outputPath);

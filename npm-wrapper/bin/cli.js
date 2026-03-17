#!/usr/bin/env node

/**
 * pydbsec-mcp — npm wrapper for pydbsec MCP server
 *
 * Automatically finds the best way to run the Python MCP server:
 *   1. uvx (fastest, no install needed)
 *   2. pipx (if installed)
 *   3. pip + auto venv (fallback, always works if Python exists)
 *
 * Usage:
 *   npx pydbsec-mcp
 *
 * Claude Desktop config:
 *   {
 *     "mcpServers": {
 *       "dbsec": {
 *         "command": "npx",
 *         "args": ["pydbsec-mcp"],
 *         "env": { "DBSEC_APP_KEY": "...", "DBSEC_APP_SECRET": "..." }
 *       }
 *     }
 *   }
 */

const { spawn, execSync } = require("child_process");
const path = require("path");
const fs = require("fs");
const os = require("os");

const PYPI_PACKAGE = "pydbsec[mcp]";
const ENTRY_POINT = "pydbsec-mcp";
const VENV_DIR = path.join(os.homedir(), ".pydbsec-mcp", "venv");

function commandExists(cmd) {
  try {
    execSync(`${isWindows() ? "where" : "which"} ${cmd}`, {
      stdio: "ignore",
    });
    return true;
  } catch {
    return false;
  }
}

function isWindows() {
  return process.platform === "win32";
}

function runProcess(cmd, args) {
  const child = spawn(cmd, args, {
    stdio: "inherit",
    env: process.env,
  });

  child.on("error", (err) => {
    process.stderr.write(`Failed to start: ${err.message}\n`);
    process.exit(1);
  });

  child.on("exit", (code) => {
    process.exit(code ?? 1);
  });
}

// Strategy 1: uvx (fastest — no install, runs from PyPI directly)
function tryUvx() {
  if (!commandExists("uvx")) return false;
  process.stderr.write("[pydbsec-mcp] Using uvx\n");
  runProcess("uvx", ["--from", PYPI_PACKAGE, ENTRY_POINT]);
  return true;
}

// Strategy 2: pipx
function tryPipx() {
  if (!commandExists("pipx")) return false;

  // Ensure installed
  try {
    execSync(`pipx list --json`, { stdio: "ignore" });
    const listOutput = execSync(`pipx list --json`).toString();
    if (!listOutput.includes("pydbsec")) {
      process.stderr.write("[pydbsec-mcp] Installing via pipx...\n");
      execSync(`pipx install "${PYPI_PACKAGE}"`, { stdio: "inherit" });
    }
  } catch {
    try {
      process.stderr.write("[pydbsec-mcp] Installing via pipx...\n");
      execSync(`pipx install "${PYPI_PACKAGE}"`, { stdio: "inherit" });
    } catch {
      return false;
    }
  }

  process.stderr.write("[pydbsec-mcp] Using pipx\n");
  runProcess("pipx", ["run", "--spec", PYPI_PACKAGE, ENTRY_POINT]);
  return true;
}

// Strategy 3: pip + auto venv (fallback — always works if Python exists)
function tryPipVenv() {
  // Find python
  const pythonCmds = isWindows()
    ? ["python", "python3", "py"]
    : ["python3", "python"];

  let pythonCmd = null;
  for (const cmd of pythonCmds) {
    if (commandExists(cmd)) {
      pythonCmd = cmd;
      break;
    }
  }

  if (!pythonCmd) return false;

  const venvPython = isWindows()
    ? path.join(VENV_DIR, "Scripts", "python.exe")
    : path.join(VENV_DIR, "bin", "python");

  const venvEntryPoint = isWindows()
    ? path.join(VENV_DIR, "Scripts", `${ENTRY_POINT}.exe`)
    : path.join(VENV_DIR, "bin", ENTRY_POINT);

  // Create venv if needed
  if (!fs.existsSync(venvPython)) {
    process.stderr.write(
      `[pydbsec-mcp] Creating Python venv at ${VENV_DIR}...\n`
    );
    fs.mkdirSync(path.dirname(VENV_DIR), { recursive: true });
    execSync(`${pythonCmd} -m venv "${VENV_DIR}"`, { stdio: "inherit" });
  }

  // Install/upgrade if entry point missing
  if (!fs.existsSync(venvEntryPoint)) {
    process.stderr.write("[pydbsec-mcp] Installing pydbsec[mcp]...\n");
    execSync(`"${venvPython}" -m pip install --upgrade "${PYPI_PACKAGE}"`, {
      stdio: "inherit",
    });
  }

  process.stderr.write("[pydbsec-mcp] Using pip venv\n");
  runProcess(venvEntryPoint, []);
  return true;
}

// Main
function main() {
  if (tryUvx()) return;
  if (tryPipx()) return;
  if (tryPipVenv()) return;

  process.stderr.write(
    "Error: Python is required but not found.\n" +
      "Install Python 3.10+ from https://www.python.org/downloads/\n"
  );
  process.exit(1);
}

main();

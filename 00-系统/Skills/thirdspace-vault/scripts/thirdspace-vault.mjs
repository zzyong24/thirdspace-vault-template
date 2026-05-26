#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";

const WORKSPACES = [
  ["system", "00-系统", "workspace-system"],
  ["inbox", "01-收件箱", "workspace-inbox"],
  ["journal", "02-日记", "workspace-journal"],
  ["knowledge", "03-知识", "workspace-knowledge"],
  ["projects", "04-项目", "workspace-projects"],
  ["resources", "05-资源", "workspace-resources"],
  ["outputs", "06-输出", "workspace-outputs"],
  ["archive", "99-归档", "workspace-archive"],
];

const WORKSPACE_SUBDIRS = {
  "00-系统": ["规范", "Skills", "Agent", "Schema", "运行时", "审计"],
  "01-收件箱": ["网页剪藏", "临时想法", "待整理", "素材暂存"],
  "02-日记": ["每日", "工作日志", "反思", "复盘", "人际事件"],
  "03-知识": ["AI学科", "AI工具学习", "AI工程", "AI论文", "Harness工程", "上下文工程", "书籍笔记", "多Agent协作开发", "开发", "开发工具", "开源项目蒸馏", "认知神经科学"],
  "04-项目": ["内容创作", "产品系统", "运营增长", "商业合作", "研究验证", "实验原型"],
  "05-资源": ["CLI工具", "工作流", "模板", "附件", "图片", "人物档案"],
  "06-输出": ["文章", "口播稿", "视频脚本", "PPT", "发布稿"],
  "99-归档": ["迁移记录", "废弃系统", "废弃工具", "完结项目"],
};

const TYPE_DEFAULTS = {
  "01-收件箱": { type: "clipping", status: "draft", source: "obsidian-clipper", subdir: "待整理" },
  "02-日记": { type: "worklog", status: "active", source: "manual", subdir: "每日" },
  "03-知识": { type: "note", status: "active", source: "manual", subdir: "AI工程" },
  "04-项目": { type: "project", status: "active", source: "manual", subdir: "产品系统" },
  "05-资源": { type: "resource", status: "active", source: "manual", subdir: "模板" },
  "06-输出": { type: "article", status: "draft", source: "manual", subdir: "文章" },
  "99-归档": { type: "note", status: "archived", source: "manual", subdir: "迁移记录" },
};

const SUBSYSTEM_CONTRACTS = {
  system: {
    workspace: "00-系统",
    name: "System Control Plane",
    skill: "workspace-system",
    allowedStatus: ["active", "archived"],
    requiredFiles: ["WORKSPACE.md", "规范/07_自治子系统设计规范.md"],
    requiredDirs: WORKSPACE_SUBDIRS["00-系统"],
  },
  inbox: {
    workspace: "01-收件箱",
    name: "Intake Router",
    skill: "workspace-inbox",
    allowedStatus: ["draft", "processed", "archived"],
    requiredFiles: ["WORKSPACE.md"],
    requiredDirs: ["网页剪藏", "临时想法", "待整理", "素材暂存"],
  },
  journal: {
    workspace: "02-日记",
    name: "Timeline System",
    skill: "workspace-journal",
    allowedStatus: ["active", "archived"],
    requiredFiles: ["WORKSPACE.md"],
    requiredDirs: ["每日", "工作日志", "反思", "复盘", "人际事件"],
  },
  knowledge: {
    workspace: "03-知识",
    name: "Knowledge Memory",
    skill: "workspace-knowledge",
    allowedStatus: ["active", "archived"],
    requiredFiles: ["WORKSPACE.md"],
    requiredDirs: WORKSPACE_SUBDIRS["03-知识"],
  },
  projects: {
    workspace: "04-项目",
    name: "Project Runtime",
    skill: "workspace-projects",
    allowedStatus: ["active", "ready", "archived"],
    requiredFiles: ["WORKSPACE.md"],
    requiredDirs: WORKSPACE_SUBDIRS["04-项目"],
  },
  resources: {
    workspace: "05-资源",
    name: "Resource Library",
    skill: "workspace-resources",
    allowedStatus: ["active", "archived"],
    requiredFiles: ["WORKSPACE.md"],
    requiredDirs: WORKSPACE_SUBDIRS["05-资源"],
  },
  outputs: {
    workspace: "06-输出",
    name: "Publishing Pipeline",
    skill: "workspace-outputs",
    allowedStatus: ["draft", "ready", "published", "archived"],
    requiredFiles: ["WORKSPACE.md"],
    requiredDirs: WORKSPACE_SUBDIRS["06-输出"],
  },
  archive: {
    workspace: "99-归档",
    name: "Archive Ledger",
    skill: "workspace-archive",
    allowedStatus: ["archived"],
    requiredFiles: ["WORKSPACE.md"],
    requiredDirs: WORKSPACE_SUBDIRS["99-归档"],
  },
};

const PROJECT_CATEGORIES = {
  content: {
    label: "内容创作",
    directory: "内容创作",
    keywords: ["创作", "视频", "口播", "脚本", "分镜", "publish", "storyboard", "topic", "内容"],
  },
  product: {
    label: "产品系统",
    directory: "产品系统",
    keywords: ["MoonOS", "产品", "系统", "插件", "MCP", "CLI", "PRD", "spec", "harness", "Msg-Collect", "灵犀"],
  },
  operations: {
    label: "运营增长",
    directory: "运营增长",
    keywords: ["知识星球", "运营", "增长", "SOP", "用户地图", "内容矩阵", "数据看板", "变现"],
  },
  business: {
    label: "商业合作",
    directory: "商业合作",
    keywords: ["商业", "合作", "客户", "代理商", "pricing", "线索", "变现", "报价", "声文智汇"],
  },
  research: {
    label: "研究验证",
    directory: "研究验证",
    keywords: ["调研", "研究", "验证", "方案", "探索", "spike", "评估"],
  },
  experiment: {
    label: "实验原型",
    directory: "实验原型",
    keywords: ["MVP", "原型", "实验", "试验", "AI童伴", "demo", "prototype"],
  },
};

const WEEKDAYS = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"];

const INTENT_ROUTES = [
  {
    id: "dev_doc",
    patterns: ["开发文档", "技术方案", "部署", "架构", "接口", "SDK", "API", "工程文档"],
    workspace: "03-知识",
    subdir: "开发",
    type: "note",
    topic: "dev",
    status: "active",
    reason: "意图包含开发文档/技术方案语义，路由到长期技术知识。",
  },
  {
    id: "tool_doc",
    patterns: ["CLI", "工具", "命令", "脚本", "自动化"],
    workspace: "03-知识",
    subdir: "开发工具",
    type: "note",
    topic: "tools",
    status: "active",
    reason: "意图包含工具/命令/自动化语义，路由到开发工具知识。",
  },
  {
    id: "article",
    patterns: ["文章", "教程", "发布", "长文"],
    workspace: "06-输出",
    subdir: "文章",
    type: "article",
    topic: "writing",
    status: "draft",
    reason: "意图包含可发布文章语义，路由到输出工作区。",
  },
  {
    id: "voiceover",
    patterns: ["口播", "口播稿", "短视频文案"],
    workspace: "06-输出",
    subdir: "口播稿",
    type: "voiceover",
    topic: "creation",
    status: "draft",
    reason: "意图包含口播/短视频文案语义，路由到口播稿。",
  },
  {
    id: "worklog",
    patterns: ["工作日志", "日报", "记录今天"],
    workspace: "02-日记",
    subdir: "工作日志",
    type: "worklog",
    topic: "work",
    status: "active",
    reason: "意图包含工作日志语义，路由到日记工作区。",
  },
  {
    id: "lifeos_event",
    patterns: ["人际", "关系事件", "人物", "LifeOS", "lifeos", "事件复盘", "关系复盘"],
    workspace: "02-日记",
    subdir: "人际事件/事件",
    type: "event",
    topic: "lifeos",
    status: "active",
    reason: "意图包含人际关系、人物或事件复盘语义，路由到 LifeOS 人际事件。",
  },
];

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith("--")) {
      args._.push(token);
      continue;
    }
    const key = token.slice(2);
    const next = argv[i + 1];
    if (!next || next.startsWith("--")) {
      args[key] = true;
    } else {
      args[key] = next;
      i += 1;
    }
  }
  return args;
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function scriptFilePath() {
  return decodeURIComponent(new URL(import.meta.url).pathname);
}

function writeIfMissing(file, content) {
  if (fs.existsSync(file)) return false;
  ensureDir(path.dirname(file));
  fs.writeFileSync(file, content, "utf8");
  return true;
}

function writeIfChanged(file, content, mode) {
  ensureDir(path.dirname(file));
  if (fs.existsSync(file) && fs.readFileSync(file, "utf8") === content) return false;
  fs.writeFileSync(file, content, mode ? { encoding: "utf8", mode } : "utf8");
  if (mode) fs.chmodSync(file, mode);
  return true;
}

function copyDir(source, target) {
  if (!fs.existsSync(source)) return { copied: 0 };
  ensureDir(target);
  let copied = 0;
  for (const entry of fs.readdirSync(source, { withFileTypes: true })) {
    if (["node_modules", "__pycache__", ".git"].includes(entry.name)) continue;
    const src = path.join(source, entry.name);
    const dst = path.join(target, entry.name);
    if (entry.isDirectory()) {
      copied += copyDir(src, dst).copied;
    } else if (entry.isFile()) {
      ensureDir(path.dirname(dst));
      fs.copyFileSync(src, dst);
      copied += 1;
    }
  }
  return { copied };
}

function nowString() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

function dateString() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}`;
}

function normalizeTitle(title) {
  const normalized = String(title || "")
    .trim()
    .replace(/[\\/:*?"<>|\s]+/g, "_")
    .replace(/_+/g, "_")
    .replace(/^_+|_+$/g, "");
  if (!normalized) throw new Error("title is required");
  return normalized;
}

function detectWorkspace(cwd, vaultRoot) {
  const resolvedCwd = path.resolve(cwd);
  const resolvedRoot = path.resolve(vaultRoot);
  for (const [id, dir, skill] of WORKSPACES) {
    const workspacePath = path.join(resolvedRoot, dir);
    if (resolvedCwd === workspacePath || resolvedCwd.startsWith(`${workspacePath}${path.sep}`)) {
      return { id, dir, skill, path: workspacePath, workspaceDoc: path.join(workspacePath, "WORKSPACE.md") };
    }
  }
  return { id: "unknown", dir: "", skill: "thirdspace-vault", path: resolvedRoot, workspaceDoc: path.join(resolvedRoot, "AGENTS.md") };
}

function yamlList(items) {
  return `[${items.map((item) => `"${String(item).replaceAll('"', '\\"')}"`).join(", ")}]`;
}

function yamlScalar(value) {
  if (Array.isArray(value)) return yamlList(value);
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  return `"${String(value ?? "").replaceAll('"', '\\"')}"`;
}

function buildFrontmatter(meta) {
  const tags = meta.tags?.length ? meta.tags : [meta.topic, meta.type, meta.status].filter(Boolean);
  const lines = [
    "---",
    `title: "${meta.title}"`,
    `type: "${meta.type}"`,
    `topic: "${meta.topic}"`,
    `workspace: "${meta.workspace}"`,
    `created: "${meta.created}"`,
    `modified: "${meta.modified}"`,
    `tags: ${yamlList(tags)}`,
    `source: "${meta.source}"`,
    `status: "${meta.status}"`,
  ];
  for (const [key, value] of Object.entries(meta.extra || {})) {
    if (value !== undefined && value !== null && value !== "") lines.push(`${key}: ${yamlScalar(value)}`);
  }
  lines.push("---", "");
  return lines.join("\n");
}

function stripFrontmatter(markdown) {
  if (!markdown.startsWith("---\n")) return markdown;
  const end = markdown.indexOf("\n---", 4);
  if (end === -1) return markdown;
  return markdown.slice(end + 5).replace(/^\n+/, "");
}

function parseFrontmatter(markdown) {
  if (!markdown.startsWith("---\n")) return { meta: {}, body: markdown };
  const end = markdown.indexOf("\n---", 4);
  if (end === -1) return { meta: {}, body: markdown };
  const raw = markdown.slice(4, end);
  const body = markdown.slice(end + 5).replace(/^\n+/, "");
  const meta = {};
  for (const line of raw.split("\n")) {
    const match = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (!match) continue;
    const [, key, value] = match;
    meta[key] = value.trim().replace(/^"(.*)"$/, "$1");
  }
  return { meta, body };
}

function uniquePath(target) {
  if (!fs.existsSync(target)) return target;
  const dir = path.dirname(target);
  const ext = path.extname(target);
  const base = path.basename(target, ext);
  for (let i = 2; i < 1000; i += 1) {
    const candidate = path.join(dir, `${base}_${i}${ext}`);
    if (!fs.existsSync(candidate)) return candidate;
  }
  throw new Error(`cannot find unique path for ${target}`);
}

function parseFluxFilename(file) {
  const base = path.basename(file, path.extname(file));
  const match = base.match(/^([^_]+)_(\d{8})(?:_(\d{6}))?_(.+)$/);
  if (!match) {
    return {
      sourcePrefix: "flux",
      date: dateString(),
      created: nowString(),
      title: base,
    };
  }
  const [, sourcePrefix, date, time, rest] = match;
  const created = `${date.slice(0, 4)}-${date.slice(4, 6)}-${date.slice(6, 8)} ${time ? `${time.slice(0, 2)}:${time.slice(2, 4)}:${time.slice(4, 6)}` : "00:00:00"}`;
  return { sourcePrefix, date, created, title: rest };
}

function rewriteFluxAssetLinks(markdown) {
  return markdown.replaceAll("(assets/images/", "(../../05-资源/图片/flux-intake-assets/");
}

function migrateFluxIntake(args = {}) {
  const resolved = resolveVault(args);
  const vaultRoot = resolved.vaultRoot;
  const dryRun = Boolean(args["dry-run"]);
  const sourceRoot = path.join(vaultRoot, "flux", "intake");
  const sourceAssets = path.join(sourceRoot, "assets", "images");
  const targetInbox = path.join(vaultRoot, "01-收件箱", "网页剪藏");
  const targetAssets = path.join(vaultRoot, "05-资源", "图片", "flux-intake-assets");
  const targetData = path.join(vaultRoot, "05-资源", "附件", "flux-intake-data");
  const manifestDir = path.join(vaultRoot, ".thirdspace", "manifests");
  const reportPath = path.join(manifestDir, `${dateString()}_flux-intake-migration.json`);
  const markdownFiles = fs.existsSync(sourceRoot)
    ? fs.readdirSync(sourceRoot).filter((name) => name.endsWith(".md")).map((name) => path.join(sourceRoot, name))
    : [];
  const dataFiles = fs.existsSync(sourceRoot)
    ? fs.readdirSync(sourceRoot, { withFileTypes: true })
      .filter((entry) => entry.isFile() && !entry.name.endsWith(".md"))
      .map((entry) => path.join(sourceRoot, entry.name))
    : [];
  const assetFiles = fs.existsSync(sourceAssets)
    ? fs.readdirSync(sourceAssets, { withFileTypes: true }).filter((entry) => entry.isFile()).map((entry) => path.join(sourceAssets, entry.name))
    : [];
  const moves = [];

  for (const asset of assetFiles) {
    const target = uniquePath(path.join(targetAssets, path.basename(asset)));
    moves.push({ type: "asset", source: path.relative(vaultRoot, asset), target: path.relative(vaultRoot, target) });
    if (!dryRun) {
      ensureDir(path.dirname(target));
      fs.renameSync(asset, target);
    }
  }

  for (const file of dataFiles) {
    const target = uniquePath(path.join(targetData, path.basename(file)));
    moves.push({ type: "data", source: path.relative(vaultRoot, file), target: path.relative(vaultRoot, target) });
    if (!dryRun) {
      ensureDir(path.dirname(target));
      fs.renameSync(file, target);
    }
  }

  for (const file of markdownFiles) {
    const parsedName = parseFluxFilename(file);
    const original = fs.readFileSync(file, "utf8");
    const { meta, body } = parseFrontmatter(original);
    const title = meta.title || parsedName.title;
    const filename = `${parsedName.date}_${normalizeTitle(title)}.md`;
    const target = uniquePath(path.join(targetInbox, filename));
    const oldTags = meta.tags ? Array.from(meta.tags.matchAll(/"([^"]+)"|'([^']+)'|([\u4e00-\u9fa5A-Za-z0-9_-]+)/g)).map((m) => m[1] || m[2] || m[3]).filter((tag) => tag !== "tags") : [];
    const frontmatter = buildFrontmatter({
      title,
      type: "clipping",
      topic: meta.topic || "intake",
      workspace: "01-收件箱",
      created: meta.created || parsedName.created,
      modified: nowString(),
      tags: Array.from(new Set([...oldTags, "flux-intake", "clipping", "draft"])),
      source: meta.source || parsedName.sourcePrefix || "web",
      status: "draft",
      extra: {
        url: meta.url,
        author: meta.author,
        publish_date: meta.publish_date,
        site_name: meta.site_name,
        site_type: meta.site_type,
        origin: meta.origin || "flux",
        original_status: meta.status,
        original_path: path.relative(vaultRoot, file),
      },
    });
    const rewritten = rewriteFluxAssetLinks(body);
    moves.push({ type: "markdown", source: path.relative(vaultRoot, file), target: path.relative(vaultRoot, target) });
    if (!dryRun) {
      ensureDir(path.dirname(target));
      fs.writeFileSync(target, `${frontmatter}${rewritten}`, "utf8");
      fs.unlinkSync(file);
    }
  }

  const result = {
    generatedAt: nowString(),
    vaultRoot,
    dryRun,
    source: "flux/intake",
    targetInbox: "01-收件箱/网页剪藏",
    targetAssets: "05-资源/图片/flux-intake-assets",
    targetData: "05-资源/附件/flux-intake-data",
    summary: {
      markdown: markdownFiles.length,
      assets: assetFiles.length,
      data: dataFiles.length,
      totalMoves: moves.length,
    },
    moves,
  };
  if (!dryRun) {
    ensureDir(manifestDir);
    fs.writeFileSync(reportPath, `${JSON.stringify(result, null, 2)}\n`, "utf8");
    result.manifestPath = reportPath;
    for (const maybeEmpty of [sourceAssets, path.join(sourceRoot, "assets"), sourceRoot]) {
      try {
        if (fs.existsSync(maybeEmpty) && fs.readdirSync(maybeEmpty).length === 0) fs.rmdirSync(maybeEmpty);
      } catch {
        // Keep non-empty legacy folders for later review.
      }
    }
  }
  return result;
}

function initVault(vaultRoot, args = {}) {
  let dirs = 0;
  let files = 0;
  for (const [, dir] of WORKSPACES) {
    const root = path.join(vaultRoot, dir);
    ensureDir(root);
    dirs += 1;
    for (const subdir of WORKSPACE_SUBDIRS[dir] || []) {
      ensureDir(path.join(root, subdir));
      dirs += 1;
    }
  }
  for (const dir of ["schema", "queues", "manifests", "reports", "data/lifeos"]) {
    ensureDir(path.join(vaultRoot, ".thirdspace", dir));
    dirs += 1;
  }
  ensureDir(path.join(vaultRoot, ".thirdspace", "events"));
  dirs += 1;
  files += writeIfMissing(path.join(vaultRoot, "AGENTS.md"), "# ThirdSpace Agent 入口\n\n读取 `.thirdspace/workspace-index.yaml` 后按当前工作区规范执行。\n") ? 1 : 0;
  files += writeIfMissing(path.join(vaultRoot, "CLAUDE.md"), "# ThirdSpace Claude Code 入口\n\n先读 `AGENTS.md`、`.thirdspace/workspace-index.yaml` 和 `.thirdspace/schema/workspace-taxonomy.yaml`，再读取当前工作区的 `WORKSPACE.md`。\n") ? 1 : 0;
  files += writeIfMissing(path.join(vaultRoot, "README.md"), "# ThirdSpace 知识库\n\n中文管理、扁平工作区、Agent-native 的知识库。\n") ? 1 : 0;
  files += writeIfMissing(path.join(vaultRoot, ".thirdspace", "workspace-index.yaml"), renderWorkspaceIndex(vaultRoot)) ? 1 : 0;
  files += writeIfMissing(path.join(vaultRoot, ".thirdspace", "schema", "workspace-taxonomy.yaml"), renderWorkspaceTaxonomy()) ? 1 : 0;
  files += writeIfMissing(path.join(vaultRoot, ".thirdspace", "schema", "project-taxonomy.yaml"), renderProjectTaxonomy()) ? 1 : 0;
  files += writeIfMissing(path.join(vaultRoot, ".thirdspace", "schema", "subsystems.yaml"), renderSubsystemContracts()) ? 1 : 0;
  files += writeIfMissing(path.join(vaultRoot, ".thirdspace", "schema", "event-capture.yaml"), renderEventCaptureSchema()) ? 1 : 0;
  files += writeIfMissing(path.join(vaultRoot, ".thirdspace", "schema", "workspace-tools.yaml"), renderWorkspaceToolsSchema()) ? 1 : 0;
  const skills = ensureCanonicalSkills(vaultRoot, args);
  const runtime = ensureRuntimeAssets({ vault: vaultRoot });
  for (const [, dir, skill] of WORKSPACES) {
    files += writeIfMissing(path.join(vaultRoot, dir, "WORKSPACE.md"), `# ${dir} 工作区规范\n\n## 子 Skill\n\n使用 \`${skill}\`。\n`) ? 1 : 0;
  }
  const result = { vaultRoot, dirsTouched: dirs, filesCreated: files, skills, runtime };
  if (args.installRuntime || args.install_runtime || args.all) {
    result.installedRuntime = installRuntime({ ...args, vault: vaultRoot, all: true });
  }
  return result;
}

function renderWorkspaceIndex(vaultRoot) {
  const lines = [
    `vault_root: "${vaultRoot}"`,
    'default_filename: "YYYYMMDD_主题.md"',
    'workspace_doc: "WORKSPACE.md"',
    "workspaces:",
  ];
  for (const [id, dir, skill] of WORKSPACES) {
    lines.push(`  ${id}:`);
    lines.push(`    path: "${dir}"`);
    lines.push(`    skill: "${skill}"`);
  }
  return `${lines.join("\n")}\n`;
}

function renderWorkspaceTaxonomy() {
  const lines = [
    'version: "2026-05-24"',
    'description: "ThirdSpace 工作区一级目录分类表。"',
    "workspaces:",
  ];
  for (const [, dir] of WORKSPACES) {
    const subdirs = WORKSPACE_SUBDIRS[dir] || [];
    const defaults = TYPE_DEFAULTS[dir] || {};
    lines.push(`  "${dir}":`);
    lines.push(`    allowed_subdirs: ${yamlList(subdirs)}`);
    lines.push(`    default_subdir: "${defaults.subdir || ""}"`);
  }
  lines.push("fallback:");
  lines.push('  unknown_workspace: "01-收件箱/待整理"');
  lines.push('  unknown_category: "01-收件箱/待整理"');
  return `${lines.join("\n")}\n`;
}

function renderProjectTaxonomy() {
  const lines = [
    "project_categories:",
  ];
  for (const [id, category] of Object.entries(PROJECT_CATEGORIES)) {
    lines.push(`  ${id}:`);
    lines.push(`    label: "${category.label}"`);
    lines.push(`    directory: "${category.directory}"`);
    lines.push(`    keywords: ${yamlList(category.keywords)}`);
  }
  lines.push("audit_policy:");
  lines.push("  high_confidence: 0.8");
  lines.push("  auto_move: false");
  lines.push("  require_trace_for_move: true");
  return `${lines.join("\n")}\n`;
}

function renderWorkspaceToolsSchema() {
  return [
    'version: "2026-05-24"',
    'description: "ThirdSpace 工作区工具框架。根 Skill 负责解析和路由，工作区 Skill 负责自治，领域 Skill 按需加载。"',
    "root:",
    '  skill: "thirdspace-vault"',
    '  skill_root: "00-系统/Skills"',
    '  tools: ["resolve-vault", "detect", "route-create", "ensure-worklog", "record-agent-event", "ensure-runtime-assets", "install-runtime", "audit-workspaces", "audit-subsystems", "audit-skill-locations"]',
    "progressive_loading:",
    '  level_0_global: ["AGENTS.md", ".thirdspace/workspace-index.yaml", ".thirdspace/schema/workspace-taxonomy.yaml", ".thirdspace/schema/subsystems.yaml", ".thirdspace/schema/event-capture.yaml", ".thirdspace/schema/workspace-tools.yaml"]',
    '  level_1_workspace: ["<workspace>/WORKSPACE.md", "<workspace-skill>/SKILL.md"]',
    '  level_2_domain: "Only load domain skills when the intent or file type requires them."',
    "workspaces:",
    '  "01-收件箱": { workspace_skill: "workspace-inbox", domain_skills: ["knowledge", "video-collector"], tools: ["route-create", "migrate-flux-intake", "build-intake-queue"], archived_legacy_sources: ["flux/intake", "flux/videos"] }',
    '  "02-日记": { workspace_skill: "workspace-journal", domain_skills: ["worklog", "reflect", "review", "lifeos"], legacy_sources: ["space/crafted/work"], archived_legacy_sources: ["space/crafted/lifeos"] }',
    '  "03-知识": { workspace_skill: "workspace-knowledge", domain_skills: ["knowledge", "harness-architect", "obsidian-canvas"] }',
    '  "04-项目": { workspace_skill: "workspace-projects", domain_skills: ["mvp-project", "ship-learn-next", "creation-tracking"] }',
    '  "05-资源": { workspace_skill: "workspace-resources", domain_skills: ["lifeos", "video-analyzer", "mkd2pic"], legacy_sources: ["space/templates", "space/workflow"], archived_legacy_sources: ["flux/intake/assets", "flux/lifeos/people.json"] }',
    '  "06-输出": { workspace_skill: "workspace-outputs", domain_skills: ["article", "video-analyzer", "huashu-slides"] }',
    '  "99-归档": { workspace_skill: "workspace-archive", domain_skills: [] }',
    "",
  ].join("\n");
}

function renderSubsystemContracts() {
  const lines = [
    'version: "2026-05-24"',
    'description: "ThirdSpace 自治子系统契约。"',
    "subsystems:",
  ];
  for (const [id, contract] of Object.entries(SUBSYSTEM_CONTRACTS)) {
    lines.push(`  ${id}:`);
    lines.push(`    workspace: "${contract.workspace}"`);
    lines.push(`    name: "${contract.name}"`);
    lines.push(`    skill: "${contract.skill}"`);
    lines.push(`    allowed_status: ${yamlList(contract.allowedStatus)}`);
    lines.push(`    required_files: ${yamlList(contract.requiredFiles)}`);
    lines.push(`    required_dirs: ${yamlList(contract.requiredDirs)}`);
  }
  lines.push("audit_policy:");
  lines.push('  report_path: ".thirdspace/reports/YYYYMMDD_自治子系统审计.md"');
  lines.push('  queue_path: ".thirdspace/queues/subsystem-maintenance.yaml"');
  lines.push("  cross_workspace_move_requires_trace: true");
  return `${lines.join("\n")}\n`;
}

function renderEventCaptureSchema() {
  return [
    'version: "2026-05-24"',
    'description: "全局路由、Git Hook、Agent Hook 和工作日志事件采集契约。"',
    "vault_resolver:",
    '  order: ["walk_up:.thirdspace/workspace-index.yaml", "env:THIRDSPACE_VAULT", "file:~/.thirdspace/config.yaml", "fallback:error (no hardcoded fallback)"]',
    "worklog:",
    '  path_template: "02-日记/工作日志/YYYYMMDD_工作日志_周X.md"',
    '  sections: ["今日重点", "Git 提交", "Agent 产出", "关键决策", "问题与风险", "明日计划"]',
    "hook_policy:",
    '  git_hook: "post-commit"',
    "  overwrite_existing_hook: false",
    '  vault_runtime_root: "00-系统/运行时"',
    '  hook_template: "00-系统/运行时/hooks/global-post-commit.sh"',
    '  crontab_template: "00-系统/运行时/crontab/thirdspace-worklog.cron"',
    '  automation_spec: "00-系统/运行时/automations/codex-thirdspace-worklog.yaml"',
    "",
  ].join("\n");
}

function runtimeRoot(vaultRoot) {
  return path.join(vaultRoot, "00-系统", "运行时");
}

function skillRoot(vaultRoot) {
  return path.join(vaultRoot, "00-系统", "Skills");
}

function sourceSkillRoot() {
  return path.resolve(path.dirname(scriptFilePath()), "..", "..");
}

function ensureCanonicalSkills(vaultRoot, args = {}) {
  const source = sourceSkillRoot();
  const target = skillRoot(vaultRoot);
  if (path.resolve(source) === path.resolve(target)) {
    ensureDir(target);
    return { source, target, status: "already-canonical", copied: 0 };
  }
  if (fs.existsSync(path.join(target, "thirdspace-vault", "SKILL.md")) && !args.refreshSkills && !args.refresh_skills) {
    return { source, target, status: "already-exists", copied: 0 };
  }
  const { copied } = copyDir(source, target);
  return { source, target, status: "copied", copied };
}

function currentScriptPath(vaultRoot) {
  return path.join(skillRoot(vaultRoot), "thirdspace-vault", "scripts", "thirdspace-vault.mjs");
}

function renderGlobalPostCommitHook(vaultRoot) {
  const scriptPath = currentScriptPath(vaultRoot);
  return [
    "#!/bin/sh",
    "# ThirdSpace portable global post-commit hook.",
    "# Source of truth: 00-系统/运行时/hooks/global-post-commit.sh",
    `VAULT="${vaultRoot}"`,
    `SCRIPT="${scriptPath}"`,
    'NODE_BIN="$(command -v node 2>/dev/null)"',
    '[ -n "$NODE_BIN" ] || exit 0',
    '[ -f "$SCRIPT" ] || exit 0',
    '[ -d "$VAULT" ] || exit 0',
    'REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"',
    '"$NODE_BIN" "$SCRIPT" capture-git-commit --vault "$VAULT" --repo "$REPO_ROOT" >/dev/null 2>&1 || true',
    "exit 0",
    "",
  ].join("\n");
}

function renderRepoPostCommitHook(vaultRoot) {
  const scriptPath = currentScriptPath(vaultRoot);
  return [
    "#!/bin/sh",
    "# ThirdSpace portable repo post-commit hook.",
    "# Source of truth: 00-系统/运行时/hooks/repo-post-commit.sh",
    `VAULT="${vaultRoot}"`,
    `SCRIPT="${scriptPath}"`,
    'NODE_BIN="$(command -v node 2>/dev/null)"',
    '[ -n "$NODE_BIN" ] || exit 0',
    '[ -f "$SCRIPT" ] || exit 0',
    'REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"',
    '"$NODE_BIN" "$SCRIPT" capture-git-commit --vault "$VAULT" --repo "$REPO_ROOT" >/dev/null 2>&1 || true',
    "exit 0",
    "",
  ].join("\n");
}

function renderCrontabTemplate(vaultRoot) {
  const scriptPath = currentScriptPath(vaultRoot);
  return [
    "# ThirdSpace daily worklog bootstrap.",
    "# Source of truth: 00-系统/运行时/crontab/thirdspace-worklog.cron",
    "# Installed by: thirdspace-vault install-runtime --crontab",
    `0 8 * * * /bin/zsh -lc 'node "${scriptPath}" ensure-worklog --vault "${vaultRoot}" >/tmp/thirdspace-worklog.log 2>&1'`,
    "",
  ].join("\n");
}

function renderCodexAutomationSpec(vaultRoot) {
  const scriptPath = currentScriptPath(vaultRoot);
  return [
    'name: "ThirdSpace 每日工作日志初始化"',
    'kind: "cron"',
    'status: "ACTIVE"',
    'schedule: "daily 08:00 Asia/Shanghai"',
    `cwd: "${vaultRoot}"`,
    'execution_environment: "local"',
    'model: "gpt-5.2"',
    'reasoning_effort: "low"',
    "prompt: >-",
    `  Run node ${scriptPath} ensure-worklog --vault ${vaultRoot}.`,
    "",
  ].join("\n");
}

function renderRuntimeReadme(vaultRoot) {
  return [
    "---",
    'workspace: "00-系统"',
    'type: "spec"',
    'topic: "runtime"',
    'status: "active"',
    'source: "agent"',
    "---",
    "",
    "# ThirdSpace 运行时资产",
    "",
    "这里保存跨电脑迁移需要的运行时规格。Agent 应该把这里当成 hook、crontab、自动化任务的源头，而不是只依赖本机散落配置。",
    "",
    "## 目录",
    "",
    "- `hooks/`: Git hook 模板。",
    "- `crontab/`: crontab 模板。",
    "- `automations/`: Codex 或其他 Agent 平台的自动化任务规格。",
    "- `manifest.yaml`: 当前运行时资产索引。",
    "",
    "## 初始化",
    "",
    "Agent 在新机器上应调用：",
    "",
    "```bash",
    `node ${currentScriptPath(vaultRoot)} install-runtime --vault ${vaultRoot} --all`,
    "```",
    "",
    "这会从 vault 内模板安装全局 Git hook，并注册每日工作日志 crontab。",
    "",
  ].join("\n");
}

function renderRuntimeManifest(vaultRoot) {
  return [
    'version: "2026-05-26"',
    'description: "ThirdSpace 可迁移运行时资产索引。"',
    `vault_root: "${vaultRoot}"`,
    'skill_root: "00-系统/Skills"',
    'runtime_root: "00-系统/运行时"',
    "assets:",
    '  global_git_hook: "00-系统/运行时/hooks/global-post-commit.sh"',
    '  repo_git_hook: "00-系统/运行时/hooks/repo-post-commit.sh"',
    '  crontab: "00-系统/运行时/crontab/thirdspace-worklog.cron"',
    '  codex_automation: "00-系统/运行时/automations/codex-thirdspace-worklog.yaml"',
    "install:",
    '  command: "thirdspace-vault install-runtime --all"',
    '  global_git_hooks_path: "~/.config/git/hooks"',
    '  crontab_marker: "THIRDSPACE DAILY WORKLOG"',
    "",
  ].join("\n");
}

function ensureRuntimeAssets(args = {}) {
  const vaultRoot = path.resolve(args.vault || resolveVault(args).vaultRoot);
  const root = runtimeRoot(vaultRoot);
  const files = [
    [path.join(root, "README.md"), renderRuntimeReadme(vaultRoot), null],
    [path.join(root, "manifest.yaml"), renderRuntimeManifest(vaultRoot), null],
    [path.join(root, "hooks", "global-post-commit.sh"), renderGlobalPostCommitHook(vaultRoot), 0o755],
    [path.join(root, "hooks", "repo-post-commit.sh"), renderRepoPostCommitHook(vaultRoot), 0o755],
    [path.join(root, "crontab", "thirdspace-worklog.cron"), renderCrontabTemplate(vaultRoot), null],
    [path.join(root, "automations", "codex-thirdspace-worklog.yaml"), renderCodexAutomationSpec(vaultRoot), null],
  ];
  let changed = 0;
  for (const [file, content, mode] of files) {
    if (writeIfChanged(file, content, mode)) changed += 1;
  }
  return { vaultRoot, runtimeRoot: root, files: files.map(([file]) => file), changed };
}

function installGlobalGitHook(vaultRoot, args = {}) {
  const home = process.env.HOME || "";
  if (!home) throw new Error("HOME is not set");
  const hookDir = path.join(home, ".config", "git", "hooks");
  const hookPath = path.join(hookDir, "post-commit");
  const content = renderGlobalPostCommitHook(vaultRoot);
  ensureDir(hookDir);
  if (fs.existsSync(hookPath)) {
    const existing = fs.readFileSync(hookPath, "utf8");
    const owned = existing.includes("ThirdSpace portable global post-commit hook") || existing.includes("Global Git post-commit hook for ThirdSpace");
    if (!owned && !args.force) {
      const sidecar = path.join(hookDir, "post-commit.thirdspace-vault");
      writeIfChanged(sidecar, content, 0o755);
      return { status: "sidecar-created-existing-hook-not-overwritten", hookPath: sidecar, hooksPath: hookDir };
    }
  }
  writeIfChanged(hookPath, content, 0o755);
  execFileSync("git", ["config", "--global", "core.hooksPath", hookDir], { encoding: "utf8" });
  return { status: "installed", hookPath, hooksPath: hookDir };
}

function installCrontab(vaultRoot) {
  const body = renderCrontabTemplate(vaultRoot).trim();
  const begin = "# BEGIN THIRDSPACE DAILY WORKLOG";
  const end = "# END THIRDSPACE DAILY WORKLOG";
  let current = "";
  try {
    current = execFileSync("crontab", ["-l"], { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
  } catch {
    current = "";
  }
  const block = `${begin}\n${body}\n${end}`;
  const pattern = new RegExp(`${begin}[\\s\\S]*?${end}\\n?`, "m");
  const next = pattern.test(current)
    ? current.replace(pattern, `${block}\n`)
    : `${current.trim() ? `${current.trim()}\n\n` : ""}${block}\n`;
  execFileSync("crontab", ["-"], { input: next, encoding: "utf8" });
  return { status: pattern.test(current) ? "updated" : "installed", marker: "THIRDSPACE DAILY WORKLOG" };
}

function installRuntime(args = {}) {
  const vaultRoot = path.resolve(args.vault || resolveVault(args).vaultRoot);
  const assets = ensureRuntimeAssets({ vault: vaultRoot });
  const installAll = args.all || (!args.globalHook && !args.global_hook && !args.crontab);
  const result = { vaultRoot, assets, installed: {} };
  if (installAll || args.globalHook || args.global_hook) {
    result.installed.globalGitHook = installGlobalGitHook(vaultRoot, args);
  }
  if (installAll || args.crontab) {
    result.installed.crontab = installCrontab(vaultRoot);
  }
  return result;
}

function createFile(args) {
  const vaultRoot = path.resolve(args.vault || resolveVault(process.cwd()).vaultRoot);
  const workspace = args.workspace || detectWorkspace(args.cwd || process.cwd(), vaultRoot).dir || "01-收件箱";
  const defaults = TYPE_DEFAULTS[workspace] || TYPE_DEFAULTS["01-收件箱"];
  const title = args.title || args._[1];
  const topic = args.topic || "knowledge-vault";
  const type = args.type || defaults.type;
  const status = args.status || defaults.status;
  const source = args.source || defaults.source;
  const subdir = args.subdir || defaults.subdir || "";
  const created = args.created || nowString();
  const filename = args.filename || `${dateString()}_${normalizeTitle(title)}.md`;
  const targetDir = path.join(vaultRoot, workspace, subdir);
  const target = path.join(targetDir, filename);
  if (fs.existsSync(target) && !args.force) {
    throw new Error(`target exists: ${target}`);
  }
  const body = args.content || `# ${title}\n`;
  const frontmatter = buildFrontmatter({ title, type, topic, workspace, created, modified: created, tags: args.tags ? args.tags.split(",") : [], source, status });
  ensureDir(targetDir);
  fs.writeFileSync(target, `${frontmatter}${stripFrontmatter(body)}`, "utf8");
  return { path: target, workspace, type, topic, status };
}

function updateFrontmatter(args) {
  const file = path.resolve(args.file);
  const vaultRoot = path.resolve(args.vault || resolveVault(process.cwd()).vaultRoot);
  const current = fs.existsSync(file) ? fs.readFileSync(file, "utf8") : "";
  if (!current) throw new Error(`file not found or empty: ${file}`);
  const detected = detectWorkspace(path.dirname(file), vaultRoot);
  const title = args.title || path.basename(file, ".md").replace(/^\d{8}_/, "");
  const workspace = args.workspace || detected.dir || "01-收件箱";
  const defaults = TYPE_DEFAULTS[workspace] || TYPE_DEFAULTS["01-收件箱"];
  const created = args.created || nowString();
  const frontmatter = buildFrontmatter({
    title,
    type: args.type || defaults.type,
    topic: args.topic || "knowledge-vault",
    workspace,
    created,
    modified: nowString(),
    tags: args.tags ? args.tags.split(",") : [],
    source: args.source || defaults.source,
    status: args.status || defaults.status,
  });
  fs.writeFileSync(file, `${frontmatter}${stripFrontmatter(current)}`, "utf8");
  return { path: file, workspace };
}

function findVaultUpwards(cwd) {
  let current = path.resolve(cwd || process.cwd());
  while (true) {
    if (fs.existsSync(path.join(current, ".thirdspace", "workspace-index.yaml"))) return current;
    const parent = path.dirname(current);
    if (parent === current) return "";
    current = parent;
  }
}

function readConfiguredVault() {
  const home = process.env.HOME || require("os").homedir();
  const config = path.join(home, ".thirdspace", "config.yaml");
  if (!fs.existsSync(config)) return "";
  const text = fs.readFileSync(config, "utf8");
  const match = text.match(/(?:vault_root|default_vault):\s*"?([^"\n]+)"?/);
  return match ? match[1].trim() : "";
}

function resolveVault(args = {}) {
  if (args.vault) return { vaultRoot: path.resolve(args.vault), source: "arg" };
  const cwd = path.resolve(args.cwd || process.cwd());
  const upward = findVaultUpwards(cwd);
  if (upward) return { vaultRoot: upward, source: "walk_up", cwd };
  if (process.env.THIRDSPACE_VAULT) {
    const envRoot = path.resolve(process.env.THIRDSPACE_VAULT);
    if (fs.existsSync(path.join(envRoot, ".thirdspace", "workspace-index.yaml"))) {
      return { vaultRoot: envRoot, source: "env", cwd };
    }
  }
  const configured = readConfiguredVault();
  if (configured) return { vaultRoot: path.resolve(configured), source: "config", cwd };
  throw new Error("Cannot resolve vault root. Run from within a vault directory or set THIRDSPACE_VAULT.");
}

function routeIntent(intent = "") {
  const normalized = String(intent || "");
  for (const route of INTENT_ROUTES) {
    if (route.patterns.some((pattern) => normalized.toLowerCase().includes(pattern.toLowerCase()))) {
      return route;
    }
  }
  return {
    id: "fallback",
    workspace: "01-收件箱",
    subdir: "待整理",
    type: "note",
    topic: "knowledge-vault",
    status: "draft",
    reason: "未匹配到高置信度意图，保守路由到收件箱待整理。",
  };
}

function routeCreate(args) {
  const resolved = resolveVault(args);
  const vaultRoot = resolved.vaultRoot;
  const cwd = path.resolve(args.cwd || process.cwd());
  const intent = args.intent || args._[1] || "";
  const route = routeIntent(intent);
  const title = args.title || intent || "未命名记录";
  const created = args.created || nowString();
  const filename = args.filename || `${dateString()}_${normalizeTitle(title)}.md`;
  const targetDir = path.join(vaultRoot, route.workspace, route.subdir);
  const target = path.join(targetDir, filename);
  if (fs.existsSync(target) && !args.force) throw new Error(`target exists: ${target}`);
  const body = args.content || `# ${title}\n\n`;
  const frontmatter = buildFrontmatter({
    title,
    type: args.type || route.type,
    topic: args.topic || route.topic,
    workspace: route.workspace,
    created,
    modified: created,
    tags: args.tags ? args.tags.split(",") : [route.topic, route.type, route.id],
    source: args.source || "agent-route",
    status: args.status || route.status,
    extra: {
      origin_cwd: cwd,
      route_intent: intent,
      route_reason: route.reason,
      route_id: route.id,
    },
  });
  ensureDir(targetDir);
  fs.writeFileSync(target, `${frontmatter}${stripFrontmatter(body)}`, "utf8");
  return {
    vaultRoot,
    resolver: resolved.source,
    route: route.id,
    reason: route.reason,
    path: target,
    workspace: route.workspace,
    subdir: route.subdir,
  };
}

function todayParts() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  return {
    date: `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`,
    compact: `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}`,
    weekday: WEEKDAYS[d.getDay()],
    timestamp: nowString(),
  };
}

function worklogPath(vaultRoot, parts = todayParts()) {
  return path.join(vaultRoot, "02-日记", "工作日志", `${parts.compact}_工作日志_${parts.weekday}.md`);
}

function ensureWorklog(args = {}) {
  const resolved = resolveVault(args);
  const vaultRoot = resolved.vaultRoot;
  const parts = todayParts();
  const file = worklogPath(vaultRoot, parts);
  if (fs.existsSync(file)) return { path: file, created: false, vaultRoot };
  const frontmatter = buildFrontmatter({
    title: `${parts.date} ${parts.weekday} 工作日志`,
    type: "worklog",
    topic: "work",
    workspace: "02-日记",
    created: parts.timestamp,
    modified: parts.timestamp,
    tags: ["worklog", "work", "event-capture"],
    source: "thirdspace-vault",
    status: "active",
  });
  const body = [
    `# ${parts.date} ${parts.weekday} 工作日志`,
    "",
    "## 今日重点",
    "",
    "## Git 提交",
    "",
    "## Agent 产出",
    "",
    "## 关键决策",
    "",
    "## 问题与风险",
    "",
    "## 明日计划",
    "",
  ].join("\n");
  ensureDir(path.dirname(file));
  fs.writeFileSync(file, `${frontmatter}${body}`, "utf8");
  return { path: file, created: true, vaultRoot };
}

function appendToSection(markdown, section, content, eventId = "") {
  if (eventId && markdown.includes(eventId)) return { markdown, appended: false };
  const heading = `## ${section}`;
  const idx = markdown.indexOf(heading);
  if (idx === -1) return { markdown: `${markdown.trimEnd()}\n\n${heading}\n\n${content}\n`, appended: true };
  const nextIdx = markdown.indexOf("\n## ", idx + heading.length);
  const insertAt = nextIdx === -1 ? markdown.length : nextIdx;
  const before = markdown.slice(0, insertAt).trimEnd();
  const after = markdown.slice(insertAt);
  return { markdown: `${before}\n\n${content}\n${after}`, appended: true };
}

function appendEventToWorklog(vaultRoot, event) {
  const ensured = ensureWorklog({ vault: vaultRoot });
  const file = ensured.path;
  let markdown = fs.readFileSync(file, "utf8");
  const section = event.section || (event.type === "git_commit" ? "Git 提交" : event.type === "decision" ? "关键决策" : "Agent 产出");
  const eventId = event.event_id || `${event.type}:${event.commit || event.timestamp}`;
  const content = formatEvent(event, eventId);
  const result = appendToSection(markdown, section, content, eventId);
  if (result.appended) {
    markdown = result.markdown.replace(/modified: ".*?"/, `modified: "${nowString()}"`);
    fs.writeFileSync(file, markdown, "utf8");
  }
  appendRawEvent(vaultRoot, { ...event, event_id: eventId });
  return { path: file, appended: result.appended, eventId };
}

function appendRawEvent(vaultRoot, event) {
  const parts = todayParts();
  const eventFile = path.join(vaultRoot, ".thirdspace", "events", `${parts.compact}.ndjson`);
  ensureDir(path.dirname(eventFile));
  fs.appendFileSync(eventFile, `${JSON.stringify(event)}\n`, "utf8");
}

function formatEvent(event, eventId) {
  if (event.type === "git_commit") {
    const files = event.files?.length ? `；文件：${event.files.join(", ")}` : "";
    return `- ${event.timestamp} [${eventId}] \`${event.repo_name || event.repo}\` ${event.branch} ${event.commit_short}：${event.subject}${files}`;
  }
  if (event.type === "decision") {
    return `- ${event.timestamp} [${eventId}] 决策：${event.decision}；理由：${event.reason}；来源：\`${event.origin_cwd}\``;
  }
  const decision = event.decision ? `；决策：${event.decision}` : "";
  const reason = event.reason ? `；理由：${event.reason}` : "";
  const artifact = event.artifact ? `；产物：${event.artifact}` : "";
  return `- ${event.timestamp} [${eventId}] ${event.summary}${decision}${reason}${artifact}；来源：\`${event.origin_cwd}\``;
}

function git(repo, args) {
  return execFileSync("git", ["-C", repo, ...args], { encoding: "utf8" }).trim();
}

function gitOptional(repo, args) {
  try {
    return git(repo, args);
  } catch {
    return "";
  }
}

function captureGitCommit(args = {}) {
  const resolved = resolveVault(args);
  const repo = path.resolve(args.repo || args.cwd || process.cwd());
  const commit = args.commit || git(repo, ["rev-parse", "HEAD"]);
  const subject = git(repo, ["log", "-1", "--pretty=%s", commit]);
  const branch = git(repo, ["rev-parse", "--abbrev-ref", "HEAD"]);
  const files = git(repo, ["show", "--pretty=", "--name-only", commit]).split("\n").filter(Boolean).slice(0, 20);
  const event = {
    type: "git_commit",
    timestamp: nowString(),
    repo,
    repo_name: path.basename(repo),
    branch,
    commit,
    commit_short: commit.slice(0, 7),
    subject,
    files,
  };
  return { vaultRoot: resolved.vaultRoot, ...appendEventToWorklog(resolved.vaultRoot, event), event };
}

function recordAgentEvent(args = {}) {
  const resolved = resolveVault(args);
  const event = {
    type: args.decision ? "decision" : "agent_event",
    timestamp: nowString(),
    summary: args.summary || args._[1] || "Agent 产出记录",
    decision: args.decision || "",
    reason: args.reason || "",
    artifact: args.artifact || "",
    origin_cwd: path.resolve(args.cwd || process.cwd()),
    importance: args.importance || "normal",
  };
  return { vaultRoot: resolved.vaultRoot, ...appendEventToWorklog(resolved.vaultRoot, event), event };
}

function registerHooks(args = {}) {
  const repo = path.resolve(args.repo || args.cwd || process.cwd());
  const gitDir = git(repo, ["rev-parse", "--git-dir"]);
  const configuredHooksPath = gitOptional(repo, ["config", "--get", "core.hooksPath"]);
  const hookDir = configuredHooksPath
    ? (path.isAbsolute(configuredHooksPath) ? configuredHooksPath : path.join(repo, configuredHooksPath))
    : (path.isAbsolute(gitDir) ? path.join(gitDir, "hooks") : path.join(repo, gitDir, "hooks"));
  const hookPath = path.join(hookDir, "post-commit");
  const scriptPath = scriptFilePath();
  const nodePath = process.execPath;
  const vaultRoot = resolveVault(args).vaultRoot;
  const content = [
    "#!/bin/sh",
    "# thirdspace-vault post-commit hook",
    'REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"',
    `"${nodePath}" "${scriptPath}" capture-git-commit --vault "${vaultRoot}" --repo "$REPO_ROOT" >/dev/null 2>&1 || true`,
    "",
  ].join("\n");
  ensureDir(hookDir);
  if (fs.existsSync(hookPath)) {
    const existing = fs.readFileSync(hookPath, "utf8");
    if (existing.includes("thirdspace-vault post-commit hook")) {
      fs.writeFileSync(hookPath, content, { encoding: "utf8", mode: 0o755 });
      return { repo, hookPath, hooksPath: configuredHooksPath || ".git/hooks", status: "updated" };
    }
    const sidecar = path.join(hookDir, "post-commit.thirdspace-vault");
    fs.writeFileSync(sidecar, content, { encoding: "utf8", mode: 0o755 });
    return { repo, hookPath: sidecar, hooksPath: configuredHooksPath || ".git/hooks", status: "sidecar-created-existing-hook-not-overwritten" };
  }
  fs.writeFileSync(hookPath, content, { encoding: "utf8", mode: 0o755 });
  fs.chmodSync(hookPath, 0o755);
  return { repo, hookPath, hooksPath: configuredHooksPath || ".git/hooks", status: "installed" };
}

function auditSystem(vaultRoot) {
  const checks = [];
  const activeBad = [
    ["00-系统/Agent/CONTEXT.md", "旧全局上下文不应常驻 Agent 运行时"],
    ["00-系统/Agent/CURRENT_STATE.md", "旧状态文件需要归档或改为生成物"],
    ["00-系统/Agent/bootstrap.md", "旧 bootstrap 与新工作区模型冲突"],
    ["00-系统/Skills/legacy-prompts-migration.md", "旧 prompt 机制说明应归档"],
  ];
  for (const [relative, message] of activeBad) {
    const full = path.join(vaultRoot, relative);
    if (fs.existsSync(full)) checks.push({ severity: "warning", path: relative, message });
  }
  for (const relative of ["00-系统/WORKSPACE.md", "00-系统/Agent/README.md", "00-系统/Skills/README.md"]) {
    const full = path.join(vaultRoot, relative);
    checks.push({ severity: fs.existsSync(full) ? "ok" : "error", path: relative, message: fs.existsSync(full) ? "exists" : "missing" });
  }
  return checks;
}

function walkFiles(dir, maxDepth = 2, depth = 0) {
  if (!fs.existsSync(dir) || depth > maxDepth) return [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    if (entry.name === "node_modules" || entry.name === ".git") continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...walkFiles(full, maxDepth, depth + 1));
    } else {
      files.push(full);
    }
  }
  return files;
}

function readProjectEvidence(projectDir) {
  const files = walkFiles(projectDir, 2).slice(0, 80);
  const names = files.map((file) => path.basename(file)).join(" ");
  const markdownSnippets = files
    .filter((file) => file.endsWith(".md"))
    .slice(0, 12)
    .map((file) => {
      try {
        return fs.readFileSync(file, "utf8").slice(0, 1200);
      } catch {
        return "";
      }
    })
    .join("\n");
  return `${projectDir}\n${names}\n${markdownSnippets}`;
}

function classifyProject(projectDir, currentCategory) {
  const base = path.basename(projectDir);
  const evidence = readProjectEvidence(projectDir);
  const normalizedEvidence = evidence.toLowerCase();
  const scores = {};
  const reasons = [];

  for (const [id, category] of Object.entries(PROJECT_CATEGORIES)) {
    let score = 0;
    for (const keyword of category.keywords) {
      const normalizedKeyword = keyword.toLowerCase();
      if (normalizedEvidence.includes(normalizedKeyword)) {
        score += 1;
      }
    }
    scores[id] = score;
  }

  const name = base.toLowerCase();
  if (base.includes("20260415_创作")) {
    scores.content += 8;
    reasons.push("项目名和内部结构指向内容创作流水线");
  }
  if (base.includes("知识星球")) {
    scores.operations += 8;
    reasons.push("项目名和文档包含知识星球运营语义");
  }
  if (base.includes("MoonOS") || base.includes("短视频创作者AI知识库")) {
    scores.product += 7;
    reasons.push("项目名指向软件/知识库产品系统");
  }
  if (base.includes("声文智汇")) {
    scores.business += 7;
    reasons.push("项目名和文档包含商业构想/客户线索语义");
  }
  if (base.includes("AI童伴") || name.includes("demo") || name.includes("mvp")) {
    scores.experiment += 5;
    reasons.push("项目名指向早期试验或原型，需要人工确认是否升级为产品系统");
  }

  if (currentCategory === "创作") scores.content += 1;
  if (currentCategory === "产品") scores.product += 1;
  if (currentCategory === "知识星球") scores.operations += 1;
  for (const [id, category] of Object.entries(PROJECT_CATEGORIES)) {
    if (currentCategory === category.directory) scores[id] += 2;
  }

  const ranked = Object.entries(scores).sort((a, b) => b[1] - a[1]);
  const [bestId, bestScore] = ranked[0];
  const [, secondScore] = ranked[1] || ["", 0];
  const category = PROJECT_CATEGORIES[bestId];
  const confidence = Math.max(0.45, Math.min(0.95, 0.55 + (bestScore - secondScore) * 0.08 + bestScore * 0.02));
  const targetPath = path.join("04-项目", category.directory, base);

  if (!reasons.length) {
    reasons.push(`关键词匹配 ${category.label}，但证据较少`);
  }

  return {
    project: base,
    currentPath: path.relative(path.dirname(path.dirname(projectDir)), projectDir).startsWith("..")
      ? projectDir
      : path.relative(process.cwd(), projectDir),
    currentCategory,
    suggestedType: bestId,
    suggestedCategory: category.label,
    suggestedPath: targetPath,
    confidence: Number(confidence.toFixed(2)),
    needsHumanConfirmation: confidence < 0.8,
    reasons,
    scores,
  };
}

function discoverProjectDirs(vaultRoot) {
  const projectsRoot = path.join(vaultRoot, "04-项目");
  if (!fs.existsSync(projectsRoot)) return [];
  const firstLevel = fs.readdirSync(projectsRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && !entry.name.startsWith("."))
    .map((entry) => entry.name);
  const projectDirs = [];
  for (const category of firstLevel) {
    const categoryDir = path.join(projectsRoot, category);
    const children = fs.readdirSync(categoryDir, { withFileTypes: true })
      .filter((entry) => entry.isDirectory() && !entry.name.startsWith("."));
    for (const child of children) {
      projectDirs.push({ currentCategory: category, dir: path.join(categoryDir, child.name) });
    }
  }
  return projectDirs;
}

function renderProjectAuditMarkdown(audit) {
  const lines = [
    "# 04-项目 分类审计报告",
    "",
    `- 生成时间：${audit.generatedAt}`,
    `- 项目数：${audit.projects.length}`,
    `- 高置信度建议：${audit.summary.highConfidence}`,
    `- 需要人工确认：${audit.summary.needsHumanConfirmation}`,
    "",
    "## 建议表",
    "",
    "| 当前路径 | 建议分类 | 建议路径 | 置信度 | 人工确认 | 理由 |",
    "|---|---|---|---:|---|---|",
  ];
  for (const item of audit.projects) {
    lines.push(`| \`${item.currentPath}\` | ${item.suggestedCategory} | \`${item.suggestedPath}\` | ${item.confidence} | ${item.needsHumanConfirmation ? "需要" : "否"} | ${item.reasons.join("；")} |`);
  }
  lines.push("");
  lines.push("## 执行原则");
  lines.push("");
  lines.push("- 本报告只提供分类建议，不自动移动项目目录。");
  lines.push("- 低于 0.8 的建议必须人工确认。");
  lines.push("- 执行移动时只能移动完整项目目录，并写入 trace。");
  lines.push("- 复杂项目内部结构保留，不打散 `_assets/`、`research/`、`renders/`、`.codex/skills/`。");
  lines.push("");
  return `${lines.join("\n")}\n`;
}

function auditProjects(vaultRoot, args = {}) {
  const discovered = discoverProjectDirs(vaultRoot);
  const projects = discovered.map(({ dir, currentCategory }) => classifyProject(dir, currentCategory));
  const summary = {
    highConfidence: projects.filter((item) => item.confidence >= 0.8).length,
    needsHumanConfirmation: projects.filter((item) => item.needsHumanConfirmation).length,
  };
  const audit = {
    generatedAt: nowString(),
    taxonomy: "00-系统/规范/06_项目工作区分类治理规则.md",
    projects,
    summary,
  };
  if (args["write-report"]) {
    const reportPath = path.join(vaultRoot, ".thirdspace", "reports", `${dateString()}_04-项目_分类审计.md`);
    ensureDir(path.dirname(reportPath));
    fs.writeFileSync(reportPath, renderProjectAuditMarkdown(audit), "utf8");
    audit.reportPath = reportPath;
  }
  return audit;
}

function auditWorkspaces(vaultRoot, args = {}) {
  const checks = [];
  for (const [, dir] of WORKSPACES) {
    const root = path.join(vaultRoot, dir);
    const allowed = new Set(WORKSPACE_SUBDIRS[dir] || []);
    if (!fs.existsSync(root)) {
      checks.push({ severity: "error", path: dir, message: "workspace missing" });
      continue;
    }
    for (const subdir of allowed) {
      const full = path.join(root, subdir);
      checks.push({ severity: fs.existsSync(full) ? "ok" : "warning", path: path.join(dir, subdir), message: fs.existsSync(full) ? "exists" : "allowed subdir missing" });
    }
    const firstLevelDirs = fs.readdirSync(root, { withFileTypes: true })
      .filter((entry) => entry.isDirectory() && !entry.name.startsWith("."))
      .map((entry) => entry.name);
    for (const name of firstLevelDirs) {
      if (!allowed.has(name)) {
        checks.push({ severity: "warning", path: path.join(dir, name), message: "unexpected first-level directory" });
      }
    }
    if (dir !== "04-项目" && dir !== "99-归档") {
      for (const file of walkFiles(root, 8)) {
        const relative = path.relative(vaultRoot, file);
        const parts = relative.split(path.sep);
        const isAllowedLifeosNestedFile = dir === "02-日记"
          && parts[1] === "人际事件"
          && ["事件", "原始记录"].includes(parts[2])
          && parts.length === 4;
        const isAllowedResourceBundleFile = dir === "05-资源"
          && ((parts[1] === "图片" && parts[2] === "flux-intake-assets")
            || (parts[1] === "附件" && parts[2] === "flux-intake-data"))
          && parts.length === 4;
        const isAllowedSkillImplementationFile = dir === "00-系统" && parts[1] === "Skills";
        const isAllowedSystemRuntimeFile = dir === "00-系统" && parts[1] === "运行时";
        if (isAllowedLifeosNestedFile || isAllowedResourceBundleFile || isAllowedSkillImplementationFile || isAllowedSystemRuntimeFile) continue;
        if (parts.length > 3) {
          checks.push({ severity: "warning", path: relative, message: "active workspace file is deeper than one category level" });
        }
      }
    }
  }
  const audit = {
    generatedAt: nowString(),
    summary: {
      ok: checks.filter((item) => item.severity === "ok").length,
      warning: checks.filter((item) => item.severity === "warning").length,
      error: checks.filter((item) => item.severity === "error").length,
    },
    checks,
  };
  if (args["write-report"]) {
    const lines = [
      "# 全库工作区结构审计",
      "",
      `- 生成时间：${audit.generatedAt}`,
      `- OK：${audit.summary.ok}`,
      `- Warning：${audit.summary.warning}`,
      `- Error：${audit.summary.error}`,
      "",
      "| 级别 | 路径 | 信息 |",
      "|---|---|---|",
      ...checks.map((item) => `| ${item.severity} | \`${item.path}\` | ${item.message} |`),
      "",
    ];
    const reportPath = path.join(vaultRoot, ".thirdspace", "reports", `${dateString()}_全库工作区结构审计.md`);
    ensureDir(path.dirname(reportPath));
    fs.writeFileSync(reportPath, lines.join("\n"), "utf8");
    audit.reportPath = reportPath;
  }
  return audit;
}

function countMarkdownFiles(dir) {
  return walkFiles(dir, 20).filter((file) => {
    if (!file.endsWith(".md")) return false;
    if (file.includes(`${path.sep}00-系统${path.sep}Skills${path.sep}`)) return false;
    return true;
  }).length;
}

function countFilesMissingFrontmatter(dir) {
  return walkFiles(dir, 20).filter((file) => {
    if (!file.endsWith(".md")) return false;
    if (file.includes(`${path.sep}00-系统${path.sep}Skills${path.sep}`)) return false;
    try {
      return !fs.readFileSync(file, "utf8").startsWith("---\n");
    } catch {
      return false;
    }
  }).length;
}

function skillPathFor(vaultRoot, skillName) {
  return path.join(vaultRoot, "00-系统", "Skills", skillName, "SKILL.md");
}

function auditSkillLocations(vaultRoot, args = {}) {
  const canonicalRoot = skillRoot(vaultRoot);
  const checks = [];
  const allFiles = walkFiles(vaultRoot, 30);
  const skillFiles = allFiles.filter((file) => path.basename(file) === "SKILL.md");
  const scriptFiles = allFiles.filter((file) => file.split(path.sep).includes("scripts"));
  for (const file of skillFiles) {
    const relative = path.relative(vaultRoot, file);
    const inCanonicalRoot = file.startsWith(`${canonicalRoot}${path.sep}`);
    const inLegacy = relative.startsWith(`_legacy${path.sep}`);
    checks.push({
      severity: inCanonicalRoot || inLegacy ? "ok" : "warning",
      path: relative,
      message: inCanonicalRoot ? "canonical skill" : (inLegacy ? "legacy skill ignored" : "skill outside 00-系统/Skills"),
    });
  }
  for (const file of scriptFiles) {
    const relative = path.relative(vaultRoot, file);
    const inCanonicalRoot = file.startsWith(`${canonicalRoot}${path.sep}`);
    const inLegacy = relative.startsWith(`_legacy${path.sep}`);
    if (!inCanonicalRoot && !inLegacy) {
      checks.push({ severity: "warning", path: relative, message: "script outside canonical Skill root" });
    }
  }
  const audit = {
    generatedAt: nowString(),
    canonicalRoot,
    summary: {
      ok: checks.filter((item) => item.severity === "ok").length,
      warning: checks.filter((item) => item.severity === "warning").length,
      error: checks.filter((item) => item.severity === "error").length,
    },
    checks,
  };
  if (args["write-report"]) {
    const lines = [
      "# Skill 位置审计",
      "",
      `- 生成时间：${audit.generatedAt}`,
      `- Canonical root：\`${canonicalRoot}\``,
      `- OK：${audit.summary.ok}`,
      `- Warning：${audit.summary.warning}`,
      `- Error：${audit.summary.error}`,
      "",
      "| 级别 | 路径 | 信息 |",
      "|---|---|---|",
      ...checks.map((item) => `| ${item.severity} | \`${item.path}\` | ${item.message} |`),
      "",
    ];
    const reportPath = path.join(vaultRoot, ".thirdspace", "reports", `${dateString()}_Skill位置审计.md`);
    ensureDir(path.dirname(reportPath));
    fs.writeFileSync(reportPath, lines.join("\n"), "utf8");
    audit.reportPath = reportPath;
  }
  return audit;
}

function auditSubsystems(vaultRoot, args = {}) {
  const checks = [];
  const maintenanceItems = [];
  const schemaFiles = [
    ".thirdspace/workspace-index.yaml",
    ".thirdspace/schema/workspace-taxonomy.yaml",
    ".thirdspace/schema/subsystems.yaml",
    ".thirdspace/schema/frontmatter.yaml",
    ".thirdspace/schema/event-capture.yaml",
    ".thirdspace/schema/workspace-tools.yaml",
  ];

  for (const relative of schemaFiles) {
    const full = path.join(vaultRoot, relative);
    checks.push({ severity: fs.existsSync(full) ? "ok" : "error", subsystem: "root", path: relative, message: fs.existsSync(full) ? "control file exists" : "control file missing" });
  }

  for (const [id, contract] of Object.entries(SUBSYSTEM_CONTRACTS)) {
    const root = path.join(vaultRoot, contract.workspace);
    if (!fs.existsSync(root)) {
      const item = { severity: "error", subsystem: id, path: contract.workspace, message: "workspace missing" };
      checks.push(item);
      maintenanceItems.push(item);
      continue;
    }

    const skillFile = skillPathFor(vaultRoot, contract.skill);
    checks.push({ severity: fs.existsSync(skillFile) ? "ok" : "error", subsystem: id, path: skillFile, message: fs.existsSync(skillFile) ? "skill exists" : "skill missing" });

    for (const relative of contract.requiredFiles) {
      const full = path.join(root, relative);
      const item = { severity: fs.existsSync(full) ? "ok" : "warning", subsystem: id, path: path.join(contract.workspace, relative), message: fs.existsSync(full) ? "required file exists" : "required file missing" };
      checks.push(item);
      if (item.severity !== "ok") maintenanceItems.push(item);
    }

    for (const relative of contract.requiredDirs) {
      const full = path.join(root, relative);
      const item = { severity: fs.existsSync(full) ? "ok" : "warning", subsystem: id, path: path.join(contract.workspace, relative), message: fs.existsSync(full) ? "required directory exists" : "required directory missing" };
      checks.push(item);
      if (item.severity !== "ok") maintenanceItems.push(item);
    }

    const missingFrontmatter = countFilesMissingFrontmatter(root);
    const markdownCount = countMarkdownFiles(root);
    if (missingFrontmatter > 0) {
      const item = { severity: "warning", subsystem: id, path: contract.workspace, message: `${missingFrontmatter}/${markdownCount} markdown files missing frontmatter` };
      checks.push(item);
      maintenanceItems.push(item);
    } else {
      checks.push({ severity: "ok", subsystem: id, path: contract.workspace, message: `${markdownCount} markdown files have frontmatter or no markdown files` });
    }
  }

  const audit = {
    generatedAt: nowString(),
    summary: {
      ok: checks.filter((item) => item.severity === "ok").length,
      warning: checks.filter((item) => item.severity === "warning").length,
      error: checks.filter((item) => item.severity === "error").length,
      maintenanceItems: maintenanceItems.length,
    },
    checks,
  };

  if (args["write-report"]) {
    const reportPath = path.join(vaultRoot, ".thirdspace", "reports", `${dateString()}_自治子系统审计.md`);
    const lines = [
      "# 自治子系统审计",
      "",
      `- 生成时间：${audit.generatedAt}`,
      `- OK：${audit.summary.ok}`,
      `- Warning：${audit.summary.warning}`,
      `- Error：${audit.summary.error}`,
      `- 维护项：${audit.summary.maintenanceItems}`,
      "",
      "| 级别 | 子系统 | 路径 | 信息 |",
      "|---|---|---|---|",
      ...checks.map((item) => `| ${item.severity} | ${item.subsystem} | \`${item.path}\` | ${item.message} |`),
      "",
    ];
    ensureDir(path.dirname(reportPath));
    fs.writeFileSync(reportPath, lines.join("\n"), "utf8");
    audit.reportPath = reportPath;

    const queuePath = path.join(vaultRoot, ".thirdspace", "queues", "subsystem-maintenance.yaml");
    const queueLines = [
      `generated: "${audit.generatedAt}"`,
      "items:",
      ...maintenanceItems.map((item) => [
        `  - subsystem: "${item.subsystem}"`,
        `    severity: "${item.severity}"`,
        `    path: "${String(item.path).replaceAll('"', '\\"')}"`,
        `    message: "${String(item.message).replaceAll('"', '\\"')}"`,
      ].join("\n")),
      "",
    ];
    ensureDir(path.dirname(queuePath));
    fs.writeFileSync(queuePath, queueLines.join("\n"), "utf8");
    audit.queuePath = queuePath;
  }

  return audit;
}

function printHelp() {
  console.log(`thirdspace-vault commands:
  resolve-vault --cwd <path>
  detect --vault <path> --cwd <path>
  init --vault <path> [--refresh-skills]
  init --vault <path> --install-runtime [--refresh-skills]
  create --vault <path> --workspace <dir> --title <title> [--topic ai] [--type note] [--subdir AI工程]
  route-create --intent <text> --title <title> [--cwd <path>] [--content <markdown>]
  migrate-flux-intake [--vault <path>] [--dry-run]
  ensure-worklog [--vault <path>]
  record-agent-event --summary <text> [--decision <text>] [--reason <text>] [--artifact <path>] [--cwd <path>]
  capture-git-commit --repo <path> [--vault <path>]
  register-hooks --repo <path> [--vault <path>]
  ensure-runtime-assets [--vault <path>]
  install-runtime [--vault <path>] [--all] [--global-hook] [--crontab]
  update-frontmatter --file <path> [--vault <path>] [--topic ai] [--type note]
  audit-system --vault <path>
  audit-projects --vault <path> [--write-report]
  audit-workspaces --vault <path> [--write-report]
  audit-subsystems --vault <path> [--write-report]
  audit-skill-locations --vault <path> [--write-report]
`);
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const command = args._[0] || "help";
  const vaultRoot = path.resolve(args.vault || resolveVault(process.cwd()).vaultRoot);
  let result;
  if (command === "help") {
    printHelp();
    return;
  }
  if (command === "resolve-vault") result = resolveVault(args);
  else if (command === "detect") result = detectWorkspace(args.cwd || process.cwd(), vaultRoot);
  else if (command === "init") result = initVault(vaultRoot, args);
  else if (command === "create") result = createFile(args);
  else if (command === "route-create") result = routeCreate(args);
  else if (command === "migrate-flux-intake") result = migrateFluxIntake(args);
  else if (command === "ensure-worklog") result = ensureWorklog(args);
  else if (command === "record-agent-event") result = recordAgentEvent(args);
  else if (command === "capture-git-commit") result = captureGitCommit(args);
  else if (command === "register-hooks") result = registerHooks(args);
  else if (command === "ensure-runtime-assets") result = ensureRuntimeAssets(args);
  else if (command === "install-runtime") result = installRuntime(args);
  else if (command === "update-frontmatter") result = updateFrontmatter(args);
  else if (command === "audit-system") result = auditSystem(vaultRoot);
  else if (command === "audit-projects") result = auditProjects(vaultRoot, args);
  else if (command === "audit-workspaces") result = auditWorkspaces(vaultRoot, args);
  else if (command === "audit-subsystems") result = auditSubsystems(vaultRoot, args);
  else if (command === "audit-skill-locations") result = auditSkillLocations(vaultRoot, args);
  else throw new Error(`unknown command: ${command}`);
  console.log(JSON.stringify(result, null, 2));
}

try {
  main();
} catch (error) {
  console.error(error.message);
  process.exit(1);
}

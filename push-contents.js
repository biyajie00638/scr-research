// 通过 GitHub Contents API 批量上传文件
const fs = require('fs');
const path = require('path');

const TOKEN = process.env.GITHUB_TOKEN;
const OWNER = 'biyajie00638';
const REPO = 'scr-research';
const BRANCH = 'main';
const BASE_URL = 'https://api.github.com';

const REPO_DIR = __dirname;

function walkDir(dir, base = '') {
  const results = [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.name === '.git' || entry.name === 'node_modules' || entry.name === '.vitepress') continue;
    const fullPath = path.join(dir, entry.name);
    const relPath = base ? `${base}/${entry.name}` : entry.name;
    if (entry.isDirectory()) {
      results.push(...walkDir(fullPath, relPath));
    } else {
      results.push({ path: relPath.replace(/\\/g, '/'), fullPath });
    }
  }
  return results;
}

async function uploadFile(filePath, content) {
  const base64 = Buffer.from(content).toString('base64');
  const url = `${BASE_URL}/repos/${OWNER}/${REPO}/contents/${filePath}`;
  const body = JSON.stringify({
    message: `添加 ${filePath}`,
    content: base64,
    branch: BRANCH,
    encoding: 'base64',
  });

  const res = await fetch(url, {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      Accept: 'application/vnd.github.v3+json',
      'Content-Type': 'application/json',
    },
    body,
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(`PUT ${filePath} → ${res.status}: ${JSON.stringify(data)}`);
  }
  return data;
}

async function pushAll() {
  const files = walkDir(REPO_DIR);
  console.log(`共 ${files.length} 个文件\n`);

  let success = 0;
  let failed = 0;

  for (let i = 0; i < files.length; i++) {
    const { path: filePath, fullPath } = files[i];
    try {
      const content = fs.readFileSync(fullPath);
      await uploadFile(filePath, content);
      success++;
      console.log(`[${i + 1}/${files.length}] OK  ${filePath}`);
    } catch (e) {
      failed++;
      console.log(`[${i + 1}/${files.length}] ERR ${filePath}: ${e.message}`);
    }

    // 小延迟避免触发限速
    if (i % 5 === 4) await new Promise(r => setTimeout(r, 500));
  }

  console.log(`\n完成: ${success} 成功, ${failed} 失败`);
  console.log(`查看: https://github.com/${OWNER}/${REPO}`);
}

pushAll().catch(e => console.error('Error:', e.message));

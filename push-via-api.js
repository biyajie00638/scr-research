// 通过 GitHub REST API 推送（绕过 git push）
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

async function api(method, endpoint, body = null) {
  const url = `${BASE_URL}${endpoint}`;
  const headers = {
    Authorization: `Bearer ${TOKEN}`,
    Accept: 'application/vnd.github.v3+json',
    'Content-Type': 'application/json',
  };
  const opts = { method, headers };
  if (body) opts.body = JSON.stringify(body);

  const res = await fetch(url, opts);
  const data = await res.json();
  if (!res.ok) {
    throw new Error(`${method} ${endpoint} → ${res.status}: ${JSON.stringify(data)}`);
  }
  return data;
}

async function pushAll() {
  // 获取所有文件
  console.log('扫描文件...');
  const files = walkDir(REPO_DIR);
  console.log(`找到 ${files.length} 个文件`);

  // Step 1: 获取当前 ref
  console.log('\n获取分支信息...');
  let ref;
  try {
    const branchData = await api('GET', `/repos/${OWNER}/${REPO}/git/ref/heads/${BRANCH}`);
    ref = branchData.object.sha;
    console.log(`分支 ${BRANCH} 已存在，基于 ${ref.slice(0, 7)}`);
  } catch {
    // 分支不存在，创建空 commit
    console.log('分支不存在，将创建新分支');
    ref = null;
  }

  // Step 2: 创建 blobs
  console.log('\n上传文件...');
  const treeEntries = [];
  for (let i = 0; i < files.length; i++) {
    const { path: filePath, fullPath } = files[i];
    const content = fs.readFileSync(fullPath);
    const base64 = content.toString('base64');

    const blob = await api('POST', `/repos/${OWNER}/${REPO}/git/blobs`, {
      content: base64,
      encoding: 'base64',
    });

    treeEntries.push({
      path: filePath,
      mode: '100644',
      type: 'blob',
      sha: blob.sha,
    });
    console.log(`  [${i + 1}/${files.length}] ${filePath}`);
  }

  // Step 3: 创建 tree
  console.log('\n创建 tree...');
  const tree = await api('POST', `/repos/${OWNER}/${REPO}/git/trees`, {
    tree: treeEntries,
  });
  console.log(`Tree: ${tree.sha}`);

  // Step 4: 创建 commit
  console.log('创建 commit...');
  const commitData = {
    message: '初始化 SCR 研究网站',
    tree: tree.sha,
    parents: ref ? [ref] : [],
  };
  const commit = await api('POST', `/repos/${OWNER}/${REPO}/git/commits`, commitData);
  console.log(`Commit: ${commit.sha}`);

  // Step 5: 更新 ref
  console.log('更新分支...');
  await api('PATCH', `/repos/${OWNER}/${REPO}/git/refs/heads/${BRANCH}`, {
    sha: commit.sha,
    force: true,
  });

  console.log('\n推送成功！');
  console.log(`查看: https://github.com/${OWNER}/${REPO}`);
  console.log(`Actions: https://github.com/${OWNER}/${REPO}/actions`);
}

pushAll().catch((e) => {
  console.error('\n失败:', e.message);
});

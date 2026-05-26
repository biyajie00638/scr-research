// 纯 JS Git 操作 — 初始化、提交、推送到 GitHub
const fs = require('fs');
const path = require('path');
const git = require('isomorphic-git');
const http = require('isomorphic-git/http/node');

const REPO_DIR = __dirname;
const REMOTE_URL = 'https://github.com/biyajie00638/scr-research.git';
const GITHUB_USERNAME = 'biyajie00638';

async function main() {
  const token = process.env.GITHUB_TOKEN;
  if (!token) {
    console.log('需要 GitHub Personal Access Token。');
    console.log('');
    console.log('获取方式：');
    console.log('1. 打开 https://github.com/settings/tokens');
    console.log('2. 点 Generate new token (classic)');
    console.log('3. 勾选 repo 权限，生成');
    console.log('4. 复制 token 回来告诉我');
    console.log('');
    console.log('（token 看起来像 ghp_xxxxxxxxxxxx）');
    return;
  }

  // 1. 初始化仓库
  console.log('1/4 初始化 Git 仓库...');
  await git.init({ fs, dir: REPO_DIR, defaultBranch: 'main' });
  console.log('   完成');

  // 2. 添加所有文件
  console.log('2/4 添加文件...');
  const files = await git.statusMatrix({ fs, dir: REPO_DIR });
  const toAdd = files
    .filter(([filepath, , worktreeStatus]) => worktreeStatus)
    .map(([filepath]) => filepath);

  for (const filepath of toAdd) {
    await git.add({ fs, dir: REPO_DIR, filepath });
  }
  console.log(`   已添加 ${toAdd.length} 个文件`);

  // 3. 提交
  console.log('3/4 提交...');
  const sha = await git.commit({
    fs,
    dir: REPO_DIR,
    message: '初始化 SCR 研究网站',
    author: { name: GITHUB_USERNAME, email: `${GITHUB_USERNAME}@users.noreply.github.com` },
  });
  console.log(`   Commit: ${sha}`);

  // 4. 推送
  console.log('4/4 推送到 GitHub...');
  try {
    await git.push({
      fs,
      http,
      dir: REPO_DIR,
      remote: 'origin',
      remoteRef: 'refs/heads/main',
      url: REMOTE_URL,
      onAuth: () => ({
        username: GITHUB_USERNAME,
        password: token,
      }),
    });
    console.log('   推送成功！');
    console.log('');
    console.log('查看部署进度: https://github.com/biyajie00638/scr-research/actions');
  } catch (e) {
    if (e.message && e.message.includes('not found') || e.message.includes('404')) {
      console.log('   仓库不存在！请先去 https://github.com/new 创建仓库 scr-research（不要勾选 README）');
    } else {
      console.log('   推送失败:', e.message);
    }
  }
}

main().catch(console.error);

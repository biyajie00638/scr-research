import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  base: '/',
  title: 'SCR脱硝系统CFD研究',
  description: '固定式工业SCR系统流场分析与优化 - 喉道临界流、气液两相雾化、尿素喷射冷区管理',
  lang: 'zh-CN',
  ignoreDeadLinks: true,
  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }],
    ['link', { rel: 'stylesheet', href: 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css' }],
  ],
  markdown: {
    math: true,
  },

  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: '首页', link: '/' },
      { text: '项目', link: '/projects/scr-nz001' },
      { text: '研究', link: '/research/critical-flow' },
      { text: '系统', link: '/system/catalyst' },
      { text: '下载', link: '/data/files' },
    ],

    sidebar: {
      '/projects/': [
        {
          text: '项目文档',
          items: [
            { text: 'SCR_NZ001 概述', link: '/projects/scr-nz001' },
            { text: 'CFD流量验证', link: '/projects/cfd-validation' },
            { text: '参数准备', link: '/projects/parameter-prep' },
            { text: '控制系统', link: '/projects/control-system' },
          ]
        }
      ],
      '/research/': [
        {
          text: '核心研究',
          items: [
            { text: '喉道临界流', link: '/research/critical-flow' },
            { text: '气液两相雾化', link: '/research/atomization' },
            { text: '尿素喷射分析', link: '/research/urea-injection' },
            { text: '氨逃逸与NOx', link: '/research/nh3-nox' },
            { text: '氨逃逸估算方法', link: '/research/nh3-slip-estimation' },
          ]
        }
      ],
      '/system/': [
        {
          text: '系统组件',
          items: [
            { text: '催化剂分析', link: '/system/catalyst' },
            { text: '气助式喷射', link: '/system/air-assist' },
            { text: '喷嘴设计', link: '/system/nozzle-design' },
          ]
        }
      ],
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/biyajie00638/scr-research' }
    ],

    search: {
      provider: 'local',
    },

    footer: {
      message: 'SCR脱硝系统CFD研究',
      copyright: 'Copyright 2026 SCR Research',
    },

    outline: {
      level: [2, 3],
      label: '页面导航',
    },

    docFooter: {
      prev: '上一页',
      next: '下一页',
    },

    editLink: {
      pattern: 'https://github.com/biyajie00638/scr-research/edit/main/:path',
      text: '在 GitHub 上编辑此页',
    },
  },
})

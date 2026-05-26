import { defineConfig } from 'vitepress'
import katex from 'markdown-it-katex'

export default defineConfig({
  lang: 'zh-CN',
  title: 'SCR脱硝系统CFD研究',
  description: '固定式工业SCR系统 - 喉道临界流、气液两相雾化、尿素喷射冷区分析',
  ignoreDeadLinks: true,
  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }],
    ['link', { rel: 'stylesheet', href: 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css' }]
  ],

  markdown: {
    lineNumbers: true,
    config: (md) => {
      md.use(katex)
    }
  },

  themeConfig: {
    search: {
      provider: 'local',
      options: {
        translations: {
          button: { buttonText: '搜索文档' },
          modal: {
            displayDetails: '显示详情',
            resetButtonTitle: '清除',
            backButtonTitle: '返回',
            noResultsText: '未找到相关结果',
            footer: { selectText: '选择', navigateText: '切换' }
          }
        }
      }
    },

    nav: [
      { text: '首页', link: '/' },
      { text: '项目', link: '/projects/scr-nz001' },
      { text: '研究', link: '/research/critical-flow' },
      { text: '系统', link: '/system/catalyst' },
      { text: '数据', link: '/data/visualization' },
      { text: '下载', link: '/data/files' }
    ],

    sidebar: {
      '/projects/': [
        {
          text: 'SCR项目',
          items: [
            { text: 'SCR_NZ001 项目概述', link: '/projects/scr-nz001' },
            { text: 'CFD 流量验证', link: '/projects/cfd-validation' },
            { text: '参数准备', link: '/projects/parameter-prep' }
          ]
        },
        {
          text: '控制系统',
          items: [
            { text: '控制系统研发', link: '/projects/control-system' }
          ]
        }
      ],
      '/research/': [
        {
          text: '核心研究',
          items: [
            { text: '喉道临界流', link: '/research/critical-flow' },
            { text: '气液两相雾化模拟', link: '/research/atomization' },
            { text: '尿素喷射与冷区分析', link: '/research/urea-injection' },
            { text: '氨逃逸与NOx控制', link: '/research/nh3-nox' }
          ]
        },
        {
          text: '算法方案',
          items: [
            { text: 'NOx传感器估算氨逃逸', link: '/research/nh3-slip-estimation' }
          ]
        }
      ],
      '/system/': [
        {
          text: '系统与催化剂',
          items: [
            { text: 'Cu-SCR 催化剂', link: '/system/catalyst' },
            { text: '气助式尿素喷射系统', link: '/system/air-assist' }
          ]
        },
        {
          text: '硬件设计',
          items: [
            { text: '喷嘴设计与安装', link: '/system/nozzle-design' }
          ]
        }
      ],
      '/data/': [
        {
          text: '数据可视化',
          items: [
            { text: '模拟结果展示', link: '/data/visualization' }
          ]
        },
        {
          text: '测试数据',
          items: [
            { text: '催化剂台架测试数据', link: '/data/catalyst-test-data' }
          ]
        },
        {
          text: '资料下载',
          items: [
            { text: '文件下载', link: '/data/files' }
          ]
        }
      ]
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com' }
    ],

    docFooter: { prev: '上一页', next: '下一页' },
    outlineTitle: '目录',

    footer: {
      message: 'SCR脱硝系统CFD分析 · 固定式工业SCR系统研究',
      copyright: 'Copyright © 2026'
    }
  }
})

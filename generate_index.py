#!/usr/bin/env python3
"""
生成 Twitter Archive 的 index.html 首页
自动扫描所有归档文件，生成导航页面
"""

import os
import glob
import json
from collections import defaultdict

# 配置
ARCHIVE_DIR = "/root/clawd/twitter-archive/"
OUTPUT_FILE = os.path.join(ARCHIVE_DIR, "index.html")

# 内联 HTML 模板（移动端优化版）
HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title>Twitter 推文归档</title>
    <style>
        :root {
            --bg-primary: #0a0a0f;
            --bg-secondary: #14141f;
            --bg-card: rgba(20, 20, 31, 0.6);
            --accent-primary: #8b5cf6;
            --accent-secondary: #6366f1;
            --text-primary: #f5f5f7;
            --text-secondary: #a1a1aa;
            --border-color: rgba(139, 92, 246, 0.1);
            --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
            --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.4);
            --shadow-glow: 0 0 20px rgba(139, 92, 246, 0.15);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "PingFang SC", "Hiragino Sans GB", sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            padding: env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left);
            overflow-x: hidden;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        body::before {
            content: '';
            position: fixed;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle at 30% 20%, rgba(139, 92, 246, 0.08) 0%, transparent 50%),
                        radial-gradient(circle at 70% 80%, rgba(99, 102, 241, 0.06) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }

        .container {
            position: relative;
            z-index: 1;
            max-width: 640px;
            margin: 0 auto;
            padding: 16px;
        }

        header {
            text-align: center;
            padding: 24px 16px 20px;
            margin-bottom: 20px;
        }

        .logo {
            font-size: 2em;
            margin-bottom: 8px;
            filter: drop-shadow(0 0 12px rgba(139, 92, 246, 0.4));
        }

        h1 {
            font-size: 1.5em;
            font-weight: 700;
            letter-spacing: -0.02em;
            margin-bottom: 6px;
            background: linear-gradient(135deg, #a78bfa 0%, #818cf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .subtitle {
            font-size: 0.875em;
            color: var(--text-secondary);
            font-weight: 400;
        }

        .stats {
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
            overflow-x: auto;
            padding: 0 0 8px 0;
            -webkit-overflow-scrolling: touch;
            scrollbar-width: none;
        }

        .stats::-webkit-scrollbar {
            display: none;
        }

        .stat-card {
            flex: 0 0 auto;
            min-width: 110px;
            background: var(--bg-card);
            backdrop-filter: blur(20px);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 16px 12px;
            text-align: center;
            box-shadow: var(--shadow-sm);
        }

        .stat-card .number {
            font-size: 1.75em;
            font-weight: 700;
            background: linear-gradient(135deg, #a78bfa 0%, #818cf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1.2;
            margin-bottom: 4px;
        }

        .stat-card .label {
            font-size: 0.75em;
            color: var(--text-secondary);
            font-weight: 500;
        }

        .search-box {
            margin-bottom: 20px;
            position: relative;
        }

        .search-icon {
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-secondary);
            font-size: 1.1em;
            pointer-events: none;
        }

        .search-box input {
            width: 100%;
            padding: 12px 16px 12px 40px;
            font-size: 0.9375em;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            background: var(--bg-card);
            backdrop-filter: blur(20px);
            color: var(--text-primary);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            font-family: inherit;
        }

        .search-box input:focus {
            outline: none;
            border-color: var(--accent-primary);
            box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1), var(--shadow-glow);
        }

        .search-box input::placeholder {
            color: var(--text-secondary);
            opacity: 0.6;
        }

        .date-card {
            background: var(--bg-card);
            backdrop-filter: blur(20px);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            margin-bottom: 12px;
            overflow: hidden;
            box-shadow: var(--shadow-sm);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .date-card.active {
            border-color: rgba(139, 92, 246, 0.3);
            box-shadow: var(--shadow-glow), var(--shadow-md);
        }

        .date-header {
            padding: 16px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            user-select: none;
            -webkit-user-select: none;
            min-height: 60px;
        }

        .date-info {
            flex: 1;
        }

        .date-title {
            font-size: 1.0625em;
            font-weight: 600;
            margin-bottom: 2px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .weekday {
            font-size: 0.8125em;
            color: var(--text-secondary);
            font-weight: 500;
        }

        .date-meta {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .date-count {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(99, 102, 241, 0.2) 100%);
            border: 1px solid rgba(139, 92, 246, 0.3);
            color: #a78bfa;
            padding: 4px 10px;
            border-radius: 8px;
            font-size: 0.8125em;
            font-weight: 600;
        }

        .arrow {
            font-size: 0.875em;
            color: var(--accent-primary);
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .date-card.active .arrow {
            transform: rotate(180deg);
        }

        .time-links {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .date-card.active .time-links {
            max-height: 400px;
        }

        .time-links-inner {
            padding: 0 16px 16px;
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }

        .time-link {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 6px;
            padding: 14px 8px;
            background: var(--bg-secondary);
            border: 1px solid rgba(139, 92, 246, 0.15);
            border-radius: 12px;
            text-decoration: none;
            color: var(--text-primary);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            min-height: 68px;
        }

        .time-link::before {
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(99, 102, 241, 0.1) 100%);
            opacity: 0;
            transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .time-link:active {
            transform: scale(0.97);
        }

        .time-link:active::before {
            opacity: 1;
        }

        .time-emoji {
            font-size: 1.75em;
            line-height: 1;
            filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
        }

        .time-text {
            font-size: 0.875em;
            font-weight: 600;
            letter-spacing: -0.01em;
        }

        .time-label {
            font-size: 0.75em;
            color: var(--text-secondary);
            font-weight: 500;
        }

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: var(--text-secondary);
        }

        .empty-state .icon {
            font-size: 3.5em;
            margin-bottom: 16px;
            opacity: 0.4;
        }

        .empty-state h3 {
            font-size: 1.125em;
            margin-bottom: 6px;
            color: var(--text-primary);
        }

        .empty-state p {
            font-size: 0.9375em;
            opacity: 0.7;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 40px 20px;
        }

        .loading.active {
            display: block;
        }

        .spinner {
            width: 32px;
            height: 32px;
            border: 3px solid rgba(139, 92, 246, 0.2);
            border-top-color: var(--accent-primary);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin: 0 auto 12px;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .loading p {
            font-size: 0.875em;
            color: var(--text-secondary);
        }

        footer {
            text-align: center;
            padding: 32px 16px 24px;
            color: var(--text-secondary);
            font-size: 0.8125em;
            margin-top: 24px;
        }

        footer a {
            color: var(--accent-primary);
            text-decoration: none;
            font-weight: 500;
        }

        footer p + p {
            margin-top: 8px;
            opacity: 0.7;
        }

        #date-list {
            -webkit-overflow-scrolling: touch;
        }

        @supports (-webkit-touch-callout: none) {
            body {
                padding-bottom: env(safe-area-inset-bottom);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">🐦</div>
            <h1>Twitter 推文归档</h1>
            <p class="subtitle">每日精选推文，自动整理</p>
        </header>

        <div class="stats">
            <div class="stat-card">
                <div class="number" id="total-days">0</div>
                <div class="label">📅 归档天数</div>
            </div>
            <div class="stat-card">
                <div class="number" id="total-summaries">0</div>
                <div class="label">📝 总推送</div>
            </div>
            <div class="stat-card">
                <div class="number" id="latest-date">--</div>
                <div class="label">🕐 最新</div>
            </div>
        </div>

        <div class="search-box">
            <span class="search-icon">🔍</span>
            <input type="text" id="search-input" placeholder="搜索日期 (如: 02-16)">
        </div>

        <div class="loading active">
            <div class="spinner"></div>
            <p>加载中...</p>
        </div>

        <div id="date-list"></div>

        <div class="empty-state" id="empty-state" style="display: none;">
            <div class="icon">📭</div>
            <h3>暂无归档</h3>
            <p>等待第一次推送</p>
        </div>

        <footer>
            <p>由 <a href="https://github.com/fengzhao2021/twitter-archive">GitHub Pages</a> 驱动</p>
            <p>每6小时自动更新</p>
        </footer>
    </div>

    <script>
        const TIME_SLOTS = {
            '00-00': { emoji: '🌙', label: '凌晨' },
            '06-00': { emoji: '🌅', label: '早晨' },
            '12-00': { emoji: '☀️', label: '中午' },
            '18-00': { emoji: '🌆', label: '傍晚' }
        };

        const WEEKDAYS = ['日', '一', '二', '三', '四', '五', '六'];

        // 数据（由服务器生成）
        const ARCHIVE_DATA = {};

        function initPage() {
            const dateList = document.getElementById('date-list');
            const loading = document.querySelector('.loading');
            const emptyState = document.getElementById('empty-state');

            setTimeout(() => {
                loading.classList.remove('active');

                if (Object.keys(ARCHIVE_DATA).length === 0) {
                    emptyState.style.display = 'block';
                    return;
                }

                updateStats();
                const sortedDates = Object.keys(ARCHIVE_DATA).sort().reverse();

                sortedDates.forEach(date => {
                    const card = createDateCard(date, ARCHIVE_DATA[date]);
                    dateList.appendChild(card);
                });

                const firstCard = dateList.querySelector('.date-card');
                if (firstCard) {
                    firstCard.classList.add('active');
                }
            }, 300);
        }

        function createDateCard(date, times) {
            const card = document.createElement('div');
            card.className = 'date-card';
            card.dataset.date = date;

            const dateObj = new Date(date);
            const weekday = WEEKDAYS[dateObj.getDay()];

            const header = document.createElement('div');
            header.className = 'date-header';
            header.innerHTML = `
                <div class="date-info">
                    <div class="date-title">📅 ${date}</div>
                    <div class="weekday">周${weekday}</div>
                </div>
                <div class="date-meta">
                    <span class="date-count">${times.length}篇</span>
                    <span class="arrow">▼</span>
                </div>
            `;

            header.addEventListener('click', () => {
                card.classList.toggle('active');
            });

            const timeLinks = document.createElement('div');
            timeLinks.className = 'time-links';

            const timeLinksInner = document.createElement('div');
            timeLinksInner.className = 'time-links-inner';

            times.forEach(time => {
                const link = createTimeLink(date, time);
                timeLinksInner.appendChild(link);
            });

            timeLinks.appendChild(timeLinksInner);
            card.appendChild(header);
            card.appendChild(timeLinks);

            return card;
        }

        function createTimeLink(date, time) {
            const slot = TIME_SLOTS[time] || { emoji: '🕐', label: time };
            const link = document.createElement('a');
            link.className = 'time-link';
            link.href = `TWITTER_SUMMARY_${date}_${time}.html`;
            link.innerHTML = `
                <span class="time-emoji">${slot.emoji}</span>
                <span class="time-text">${time.replace('-', ':')}</span>
                <span class="time-label">${slot.label}</span>
            `;
            return link;
        }

        function updateStats() {
            const dates = Object.keys(ARCHIVE_DATA);
            const totalDays = dates.length;
            const totalSummaries = Object.values(ARCHIVE_DATA).reduce((sum, times) => sum + times.length, 0);
            const latestDate = dates.sort().reverse()[0];

            document.getElementById('total-days').textContent = totalDays;
            document.getElementById('total-summaries').textContent = totalSummaries;
            document.getElementById('latest-date').textContent = latestDate.substring(5);
        }

        document.getElementById('search-input').addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            const cards = document.querySelectorAll('.date-card');

            cards.forEach(card => {
                const date = card.dataset.date.toLowerCase();
                card.style.display = date.includes(query) ? 'block' : 'none';
            });
        });

        document.addEventListener('DOMContentLoaded', initPage);
    </script>
</body>
</html>'''


def scan_archive_files():
    """扫描归档目录"""
    pattern = os.path.join(ARCHIVE_DIR, "TWITTER_SUMMARY_*.html")
    files = glob.glob(pattern)
    files = [f for f in files if "index.html" not in f]
    return files


def parse_filename(filename):
    """解析文件名"""
    basename = os.path.basename(filename)
    parts = basename.replace("TWITTER_SUMMARY_", "").replace(".html", "")
    
    if "_" in parts:
        date, time = parts.split("_", 1)
        return (date, time)
    else:
        return (parts, "00-00")


def build_archive_data():
    """构建归档数据"""
    files = scan_archive_files()
    archive_data = defaultdict(list)

    for filepath in files:
        date, time = parse_filename(filepath)
        archive_data[date].append(time)

    for date in archive_data:
        archive_data[date].sort()

    return dict(archive_data)


def generate_index_html():
    """生成 index.html"""
    archive_data = build_archive_data()
    archive_data_js = json.dumps(archive_data, ensure_ascii=False, indent=12)
    
    html_content = HTML_TEMPLATE.replace("const ARCHIVE_DATA = {};", f"const ARCHIVE_DATA = {archive_data_js};")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ index.html 已生成: {OUTPUT_FILE}")
    print(f"📊 归档天数: {len(archive_data)}")
    print(f"📊 总推送数: {sum(len(times) for times in archive_data.values())}")


def main():
    print("🚀 生成 index.html...")
    generate_index_html()


if __name__ == "__main__":
    main()

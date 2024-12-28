from playwright.async_api import async_playwright
import json
import os
from datetime import datetime
from pathlib import Path

class WebScraper:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)

    async def initialize(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch()
        return self

    @classmethod
    async def create(cls):
        scraper = cls()
        await scraper.initialize()
        return scraper

    def _generate_filename(self):
        return "scraped_data.json"

    async def scrape_website(self, url):
        page = await self.browser.new_page()
        await page.goto(url)
        
        # Extract all website componentsds
        site_data = await page.evaluate('''
            () => {
                const getData = (element) => {
                    const computedStyle = window.getComputedStyle(element);
                    return {
                        tag: element.tagName.toLowerCase(),
                        text: element.innerText,
                        html: element.innerHTML,
                        href: element.href || null,
                        src: element.src || null,
                        value: element.value || null,
                        children: Array.from(element.children).map(child => getData(child)),
                        classes: Array.from(element.classList),
                        id: element.id || null,
                        attributes: Object.assign({}, ...Array.from(element.attributes)
                            .map(attr => ({[attr.name]: attr.value}))),
                        styles: {
                            color: computedStyle.color,
                            backgroundColor: computedStyle.backgroundColor,
                            fontSize: computedStyle.fontSize,
                            display: computedStyle.display,
                            position: computedStyle.position
                        }
                    };
                };

                // Get structured data
                const getStructuredData = () => {
                    const scripts = document.querySelectorAll('script[type="application/ld+json"]');
                    return Array.from(scripts).map(script => {
                        try {
                            return JSON.parse(script.textContent);
                        } catch {
                            return null;
                        }
                    }).filter(Boolean);
                };

                return {
                    url: window.location.href,
                    title: document.title,
                    meta: {
                        description: document.querySelector('meta[name="description"]')?.content,
                        keywords: document.querySelector('meta[name="keywords"]')?.content,
                        viewport: document.querySelector('meta[name="viewport"]')?.content,
                        robots: document.querySelector('meta[name="robots"]')?.content,
                        ogTags: Array.from(document.querySelectorAll('meta[property^="og:"]'))
                            .map(tag => ({property: tag.getAttribute('property'), content: tag.content}))
                    },
                    navigation: Array.from(document.querySelectorAll('nav')).map(nav => getData(nav)),
                    mainContent: Array.from(document.querySelectorAll('main, article, section')).map(content => getData(content)),
                    footer: Array.from(document.querySelectorAll('footer')).map(footer => getData(footer)),
                    images: Array.from(document.querySelectorAll('img')).map(img => ({
                        src: img.src,
                        alt: img.alt,
                        width: img.width,
                        height: img.height
                    })),
                    links: Array.from(document.querySelectorAll('a')).map(link => ({
                        text: link.innerText,
                        href: link.href,
                        location: link.closest('nav, header, main, footer')?.tagName.toLowerCase()
                    })),
                    forms: Array.from(document.querySelectorAll('form')).map(form => ({
                        action: form.action,
                        method: form.method,
                        inputs: Array.from(form.querySelectorAll('input, select, textarea'))
                            .map(input => getData(input))
                    })),
                    scripts: Array.from(document.querySelectorAll('script')).map(script => ({
                        src: script.src,
                        type: script.type,
                        async: script.async,
                        defer: script.defer
                    })),
                    styles: Array.from(document.querySelectorAll('link[rel="stylesheet"]')).map(style => ({
                        href: style.href
                    })),
                    iframes: Array.from(document.querySelectorAll('iframe')).map(iframe => ({
                        src: iframe.src,
                        width: iframe.width,
                        height: iframe.height
                    })),
                    tables: Array.from(document.querySelectorAll('table')).map(table => ({
                        headers: Array.from(table.querySelectorAll('th')).map(th => th.innerText),
                        rows: Array.from(table.querySelectorAll('tr')).map(tr => 
                            Array.from(tr.querySelectorAll('td')).map(td => td.innerText)
                        )
                    })),
                    structuredData: getStructuredData(),
                    fullDOM: getData(document.documentElement)
                };
            }
        ''')

        # Add metadata about the scraping
        site_data['scrape_metadata'] = {
            'timestamp': datetime.now().isoformat(),
            'url': url
        }

        filepath = self.data_dir / self._generate_filename()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(site_data, f, indent=2)

        await page.close()
        return filepath

    async def close(self):
        await self.browser.close()
        await self.playwright.stop()

    @staticmethod
    def load_scraped_data(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
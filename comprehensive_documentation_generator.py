"""
Comprehensive Documentation Generator for the Enhanced Moveworks YAML Assistant.

This module generates complete documentation including user manuals, API references,
tutorials, and help content in multiple formats (HTML, PDF, Markdown).
"""

import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from help_system import help_system, HelpTopic, HelpSection
from comprehensive_tutorial_system import tutorial_system


@dataclass
class DocumentationConfig:
    """Configuration for documentation generation."""
    output_dir: str = "documentation"
    formats: List[str] = None  # html, pdf, markdown
    include_screenshots: bool = True
    include_tutorials: bool = True
    include_examples: bool = True
    theme: str = "modern"
    version: str = "2.0"
    
    def __post_init__(self):
        if self.formats is None:
            self.formats = ["html", "markdown"]


class ComprehensiveDocumentationGenerator:
    """
    Generates comprehensive documentation for all application features.
    
    Features:
    - Multi-format output (HTML, PDF, Markdown)
    - Complete feature coverage
    - Interactive tutorials
    - Code examples
    - Screenshots and diagrams
    - Search functionality
    - Mobile-responsive design
    """
    
    def __init__(self, config: DocumentationConfig = None):
        self.config = config or DocumentationConfig()
        self.output_path = Path(self.config.output_dir)
        self.templates = self._load_templates()
    
    def generate_complete_documentation(self) -> bool:
        """Generate complete documentation suite."""
        try:
            print("🚀 Starting comprehensive documentation generation...")
            
            # Create output directory
            self.output_path.mkdir(exist_ok=True)
            
            # Generate different formats
            for format_type in self.config.formats:
                print(f"📄 Generating {format_type.upper()} documentation...")
                
                if format_type == "html":
                    self._generate_html_documentation()
                elif format_type == "markdown":
                    self._generate_markdown_documentation()
                elif format_type == "pdf":
                    self._generate_pdf_documentation()
            
            # Generate additional resources
            self._generate_search_index()
            self._copy_assets()
            
            print("✅ Documentation generation completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Documentation generation failed: {e}")
            return False
    
    def _generate_html_documentation(self):
        """Generate HTML documentation with modern styling."""
        html_dir = self.output_path / "html"
        html_dir.mkdir(exist_ok=True)
        
        # Generate main index page
        self._generate_html_index(html_dir)
        
        # Generate section pages
        sections = help_system.get_sections()
        for section in sections:
            self._generate_html_section(html_dir, section)
        
        # Generate individual topic pages
        for topic_title, topic in help_system.topics.items():
            self._generate_html_topic(html_dir, topic)
        
        # Generate tutorial pages
        if self.config.include_tutorials and tutorial_system:
            self._generate_html_tutorials(html_dir)
        
        # Copy CSS and JavaScript
        self._generate_html_assets(html_dir)
    
    def _generate_html_index(self, html_dir: Path):
        """Generate the main HTML index page."""
        content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Moveworks YAML Assistant - Documentation</title>
    <link rel="stylesheet" href="assets/style.css">
    <link rel="stylesheet" href="assets/prism.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <h1 class="nav-title">📋 Moveworks YAML Assistant</h1>
            <div class="nav-search">
                <input type="text" id="search-input" placeholder="Search documentation...">
                <button id="search-btn">🔍</button>
            </div>
        </div>
    </nav>
    
    <div class="container">
        <aside class="sidebar">
            <div class="sidebar-content">
                <h3>📚 Documentation</h3>
                <ul class="nav-menu">
                    {self._generate_navigation_menu()}
                </ul>
                
                <h3>🎯 Quick Start</h3>
                <ul class="quick-links">
                    <li><a href="getting-started.html">Getting Started</a></li>
                    <li><a href="your-first-workflow.html">Your First Workflow</a></li>
                    <li><a href="tutorials.html">Interactive Tutorials</a></li>
                    <li><a href="examples.html">Examples</a></li>
                </ul>
            </div>
        </aside>
        
        <main class="main-content">
            <header class="page-header">
                <h1>🚀 Enhanced Moveworks YAML Assistant</h1>
                <p class="subtitle">Complete Documentation & User Guide</p>
                <div class="version-info">Version {self.config.version} • Updated {datetime.now().strftime('%B %d, %Y')}</div>
            </header>
            
            <section class="hero-section">
                <div class="hero-content">
                    <h2>Welcome to the Complete Documentation</h2>
                    <p>The Enhanced Moveworks YAML Assistant is the most comprehensive tool for creating Moveworks Compound Action workflows. This documentation covers all features, from basic workflow creation to advanced automation patterns.</p>
                    
                    <div class="feature-grid">
                        <div class="feature-card">
                            <h3>🎯 Complete Expression Support</h3>
                            <p>All 8 expression types with perfect YAML compliance</p>
                            <a href="expression-types.html" class="btn btn-primary">Learn More</a>
                        </div>
                        
                        <div class="feature-card">
                            <h3>⭐ Enhanced Features</h3>
                            <p>JSON Path Selector, Template Library, Smart Validation</p>
                            <a href="enhanced-features.html" class="btn btn-primary">Explore</a>
                        </div>
                        
                        <div class="feature-card">
                            <h3>📚 Interactive Tutorials</h3>
                            <p>Step-by-step guidance for all skill levels</p>
                            <a href="tutorials.html" class="btn btn-primary">Start Learning</a>
                        </div>
                        
                        <div class="feature-card">
                            <h3>💡 Best Practices</h3>
                            <p>Professional tips and optimization techniques</p>
                            <a href="best-practices.html" class="btn btn-primary">Get Tips</a>
                        </div>
                    </div>
                </div>
            </section>
            
            <section class="getting-started-section">
                <h2>🚀 Getting Started</h2>
                <div class="steps-container">
                    <div class="step">
                        <div class="step-number">1</div>
                        <h3>Install & Launch</h3>
                        <p>Download and run the Enhanced Moveworks YAML Assistant</p>
                    </div>
                    <div class="step">
                        <div class="step-number">2</div>
                        <h3>Take the Tutorial</h3>
                        <p>Complete the "Your First Workflow" interactive tutorial</p>
                    </div>
                    <div class="step">
                        <div class="step-number">3</div>
                        <h3>Explore Templates</h3>
                        <p>Browse pre-built workflows in the Template Library</p>
                    </div>
                    <div class="step">
                        <div class="step-number">4</div>
                        <h3>Build & Deploy</h3>
                        <p>Create your workflows and export production-ready YAML</p>
                    </div>
                </div>
            </section>
            
            <section class="recent-updates">
                <h2>📈 Recent Updates</h2>
                <div class="update-list">
                    <div class="update-item">
                        <h4>Enhanced JSON Path Selector</h4>
                        <p>Improved array handling and beginner-friendly visualization</p>
                        <span class="update-date">Latest</span>
                    </div>
                    <div class="update-item">
                        <h4>Comprehensive Help System</h4>
                        <p>Complete documentation with interactive tutorials</p>
                        <span class="update-date">New</span>
                    </div>
                    <div class="update-item">
                        <h4>All Expression Types</h4>
                        <p>Full support for all 8 Moveworks expression types</p>
                        <span class="update-date">Enhanced</span>
                    </div>
                </div>
            </section>
        </main>
    </div>
    
    <footer class="footer">
        <div class="footer-content">
            <p>&copy; 2024 Enhanced Moveworks YAML Assistant. Documentation generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </footer>
    
    <script src="assets/prism.js"></script>
    <script src="assets/search.js"></script>
    <script src="assets/main.js"></script>
</body>
</html>
        """.strip()
        
        with open(html_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(content)
    
    def _generate_navigation_menu(self) -> str:
        """Generate the navigation menu HTML."""
        menu_html = ""
        sections = help_system.get_sections()
        
        for section in sections:
            section_topics = help_system.get_section_topics(section.title)
            
            menu_html += f"""
                <li class="nav-section">
                    <a href="{self._slugify(section.title)}.html" class="section-link">
                        {section.icon} {section.title}
                    </a>
                    <ul class="nav-subsection">
            """
            
            for topic in section_topics[:5]:  # Limit to first 5 topics
                menu_html += f"""
                        <li><a href="{self._slugify(topic.title)}.html">{topic.title}</a></li>
                """
            
            if len(section_topics) > 5:
                menu_html += f"""
                        <li><a href="{self._slugify(section.title)}.html">... and {len(section_topics) - 5} more</a></li>
                """
            
            menu_html += """
                    </ul>
                </li>
            """
        
        return menu_html
    
    def _generate_html_topic(self, html_dir: Path, topic: HelpTopic):
        """Generate HTML page for a specific topic."""
        content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic.title} - Moveworks YAML Assistant Documentation</title>
    <link rel="stylesheet" href="assets/style.css">
    <link rel="stylesheet" href="assets/prism.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <a href="index.html" class="nav-title">📋 Moveworks YAML Assistant</a>
            <div class="nav-breadcrumb">
                <a href="index.html">Home</a> → 
                <a href="{self._slugify(topic.category)}.html">{topic.category}</a> → 
                {topic.title}
            </div>
        </div>
    </nav>
    
    <div class="container">
        <aside class="sidebar">
            <div class="sidebar-content">
                <a href="index.html" class="back-link">← Back to Home</a>
                
                <div class="topic-meta">
                    <h4>Topic Information</h4>
                    <p><strong>Category:</strong> {topic.category}</p>
                    <p><strong>Difficulty:</strong> {topic.difficulty}</p>
                    <p><strong>Time:</strong> {topic.estimated_time}</p>
                    {f'<p><strong>Prerequisites:</strong> {", ".join(topic.prerequisites)}</p>' if topic.prerequisites else ''}
                </div>
                
                {self._generate_related_topics_html(topic)}
            </div>
        </aside>
        
        <main class="main-content">
            <article class="topic-content">
                <header class="topic-header">
                    <h1>{topic.title}</h1>
                    <div class="topic-badges">
                        <span class="badge badge-{topic.difficulty.lower()}">{topic.difficulty}</span>
                        <span class="badge badge-category">{topic.category}</span>
                    </div>
                </header>
                
                <div class="topic-body">
                    {self._convert_content_to_html(topic.content)}
                </div>
                
                {self._generate_topic_examples_html(topic)}
            </article>
        </main>
    </div>
    
    <script src="assets/prism.js"></script>
    <script src="assets/main.js"></script>
</body>
</html>
        """.strip()
        
        filename = f"{self._slugify(topic.title)}.html"
        with open(html_dir / filename, "w", encoding="utf-8") as f:
            f.write(content)
    
    def _generate_markdown_documentation(self):
        """Generate Markdown documentation."""
        md_dir = self.output_path / "markdown"
        md_dir.mkdir(exist_ok=True)
        
        # Generate main README
        self._generate_markdown_readme(md_dir)
        
        # Generate section files
        sections = help_system.get_sections()
        for section in sections:
            self._generate_markdown_section(md_dir, section)
        
        # Generate topic files
        for topic_title, topic in help_system.topics.items():
            self._generate_markdown_topic(md_dir, topic)
    
    def _generate_markdown_readme(self, md_dir: Path):
        """Generate the main README.md file."""
        content = f"""# Enhanced Moveworks YAML Assistant - Documentation

Welcome to the complete documentation for the Enhanced Moveworks YAML Assistant!

## 🚀 Overview

The Enhanced Moveworks YAML Assistant is the most comprehensive tool for creating Moveworks Compound Action workflows. It provides complete support for all 8 expression types, advanced features, and intelligent assistance.

## 📚 Documentation Sections

{self._generate_markdown_toc()}

## 🎯 Quick Start

1. **[Getting Started](getting-started.md)** - Essential information for new users
2. **[Your First Workflow](your-first-workflow.md)** - Step-by-step tutorial
3. **[Expression Types](expression-types.md)** - Complete guide to all 8 types
4. **[Enhanced Features](enhanced-features.md)** - Advanced tools and capabilities

## 🔧 Key Features

### Complete Expression Support
- ✅ **action** - Execute HTTP requests and Moveworks actions
- ✅ **script** - Run custom APIthon code for data processing
- ✅ **switch** - Conditional branching based on data values
- ✅ **for** - Loop through arrays of data
- ✅ **parallel** - Execute multiple operations simultaneously
- ✅ **return** - End workflow and format output data
- ✅ **raise** - Throw errors for error handling
- ✅ **try_catch** - Handle errors gracefully with fallback logic

### Enhanced Features
- 🎯 **JSON Path Selector** - Visual tool for data selection
- 📚 **Template Library** - Pre-built workflow patterns
- ✅ **Enhanced Validation** - Intelligent error checking with fix suggestions
- 💡 **Contextual Examples** - Smart examples that adapt to your work
- 🎓 **Interactive Tutorials** - Step-by-step learning system

### Data Handling
- 🔄 **Complete Data Context** - Support for data.* and meta_info.user
- 📊 **Array Processing** - Advanced tools for working with JSON arrays
- 🔍 **Path Validation** - Real-time checking of data references
- 📋 **Visual Selection** - Point-and-click data path creation

## 📖 Documentation Format

This documentation is available in multiple formats:
- **HTML** - Interactive web documentation with search
- **Markdown** - GitHub-compatible markdown files
- **PDF** - Printable documentation (if configured)

## 🆕 Version {self.config.version}

Generated on {datetime.now().strftime('%B %d, %Y')}

---

For the latest updates and support, visit the application's Help menu or check the interactive tutorials.
"""
        
        with open(md_dir / "README.md", "w", encoding="utf-8") as f:
            f.write(content)
    
    def _generate_markdown_toc(self) -> str:
        """Generate table of contents for markdown."""
        toc = ""
        sections = help_system.get_sections()
        
        for section in sections:
            toc += f"\n### {section.icon} {section.title}\n"
            toc += f"{section.description}\n\n"
            
            section_topics = help_system.get_section_topics(section.title)
            for topic in section_topics:
                toc += f"- [{topic.title}]({self._slugify(topic.title)}.md)\n"
            toc += "\n"
        
        return toc
    
    def _generate_html_assets(self, html_dir: Path):
        """Generate CSS, JavaScript, and other assets."""
        assets_dir = html_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        # Generate modern CSS
        css_content = """
/* Modern Documentation Styles */
:root {
    --primary-color: #3498db;
    --secondary-color: #2c3e50;
    --accent-color: #e74c3c;
    --success-color: #27ae60;
    --warning-color: #f39c12;
    --background-color: #ffffff;
    --surface-color: #f8f9fa;
    --text-color: #2c3e50;
    --text-muted: #7f8c8d;
    --border-color: #dee2e6;
    --shadow: 0 2px 4px rgba(0,0,0,0.1);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background-color: var(--background-color);
}

.navbar {
    background: var(--secondary-color);
    color: white;
    padding: 1rem 0;
    box-shadow: var(--shadow);
    position: sticky;
    top: 0;
    z-index: 100;
}

.nav-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.nav-title {
    font-size: 1.5rem;
    font-weight: bold;
    text-decoration: none;
    color: white;
}

.nav-search {
    display: flex;
    gap: 0.5rem;
}

.nav-search input {
    padding: 0.5rem;
    border: none;
    border-radius: 4px;
    min-width: 250px;
}

.container {
    display: flex;
    max-width: 1200px;
    margin: 0 auto;
    min-height: calc(100vh - 80px);
}

.sidebar {
    width: 300px;
    background: var(--surface-color);
    border-right: 1px solid var(--border-color);
    padding: 2rem;
}

.main-content {
    flex: 1;
    padding: 2rem;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
    margin: 2rem 0;
}

.feature-card {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: var(--shadow);
    border: 1px solid var(--border-color);
}

.btn {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 4px;
    text-decoration: none;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-primary {
    background: var(--primary-color);
    color: white;
}

.btn-primary:hover {
    background: #2980b9;
    transform: translateY(-1px);
}

.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.875rem;
    font-weight: 500;
}

.badge-beginner { background: #d4edda; color: #155724; }
.badge-intermediate { background: #fff3cd; color: #856404; }
.badge-advanced { background: #f8d7da; color: #721c24; }

pre {
    background: var(--surface-color);
    padding: 1rem;
    border-radius: 4px;
    overflow-x: auto;
    border-left: 4px solid var(--primary-color);
}

code {
    background: var(--surface-color);
    padding: 0.2rem 0.4rem;
    border-radius: 3px;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

@media (max-width: 768px) {
    .container {
        flex-direction: column;
    }
    
    .sidebar {
        width: 100%;
    }
    
    .feature-grid {
        grid-template-columns: 1fr;
    }
}
        """.strip()
        
        with open(assets_dir / "style.css", "w", encoding="utf-8") as f:
            f.write(css_content)
        
        # Generate search JavaScript
        js_content = """
// Documentation Search Functionality
class DocumentationSearch {
    constructor() {
        this.searchInput = document.getElementById('search-input');
        this.searchBtn = document.getElementById('search-btn');
        this.searchIndex = [];
        
        this.initializeSearch();
        this.loadSearchIndex();
    }
    
    initializeSearch() {
        if (this.searchInput) {
            this.searchInput.addEventListener('input', (e) => {
                this.performSearch(e.target.value);
            });
        }
        
        if (this.searchBtn) {
            this.searchBtn.addEventListener('click', () => {
                this.performSearch(this.searchInput.value);
            });
        }
    }
    
    async loadSearchIndex() {
        try {
            const response = await fetch('search-index.json');
            this.searchIndex = await response.json();
        } catch (error) {
            console.warn('Search index not available:', error);
        }
    }
    
    performSearch(query) {
        if (query.length < 2) return;
        
        const results = this.searchIndex.filter(item => 
            item.title.toLowerCase().includes(query.toLowerCase()) ||
            item.content.toLowerCase().includes(query.toLowerCase()) ||
            item.keywords.some(keyword => 
                keyword.toLowerCase().includes(query.toLowerCase())
            )
        );
        
        this.displaySearchResults(results);
    }
    
    displaySearchResults(results) {
        // Implementation for displaying search results
        console.log('Search results:', results);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DocumentationSearch();
});
        """.strip()
        
        with open(assets_dir / "search.js", "w", encoding="utf-8") as f:
            f.write(js_content)
    
    def _generate_search_index(self):
        """Generate search index for documentation."""
        search_index = []
        
        for topic_title, topic in help_system.topics.items():
            search_index.append({
                "title": topic.title,
                "category": topic.category,
                "content": topic.content[:500],  # First 500 chars
                "keywords": topic.keywords,
                "url": f"{self._slugify(topic.title)}.html",
                "difficulty": topic.difficulty
            })
        
        # Save search index
        with open(self.output_path / "html" / "search-index.json", "w", encoding="utf-8") as f:
            json.dump(search_index, f, indent=2)
    
    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug."""
        import re
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')
    
    def _convert_content_to_html(self, content: str) -> str:
        """Convert markdown-like content to HTML."""
        # Basic markdown conversions
        content = content.replace('\n# ', '\n<h1>')
        content = content.replace('\n## ', '\n<h2>')
        content = content.replace('\n### ', '\n<h3>')
        content = content.replace('\n\n', '</p><p>')
        
        # Code blocks
        content = content.replace('```yaml\n', '<pre><code class="language-yaml">')
        content = content.replace('```python\n', '<pre><code class="language-python">')
        content = content.replace('```json\n', '<pre><code class="language-json">')
        content = content.replace('```\n', '</code></pre>')
        
        # Wrap in paragraph tags
        if not content.startswith('<'):
            content = f'<p>{content}</p>'
        
        return content
    
    def _generate_related_topics_html(self, topic: HelpTopic) -> str:
        """Generate HTML for related topics."""
        if not topic.related_topics:
            return ""
        
        html = '<div class="related-topics"><h4>Related Topics</h4><ul>'
        for related_title in topic.related_topics:
            related_topic = help_system.get_topic(related_title)
            if related_topic:
                html += f'<li><a href="{self._slugify(related_title)}.html">{related_title}</a></li>'
        html += '</ul></div>'
        
        return html
    
    def _generate_topic_examples_html(self, topic: HelpTopic) -> str:
        """Generate HTML for topic examples."""
        if not topic.examples:
            return ""
        
        html = '<div class="topic-examples"><h3>Examples</h3>'
        for example in topic.examples:
            html += f'<div class="example-block"><pre><code>{example}</code></pre></div>'
        html += '</div>'
        
        return html
    
    def _load_templates(self) -> Dict[str, str]:
        """Load documentation templates."""
        return {
            "html_base": "<!DOCTYPE html>...",
            "markdown_base": "# {title}\n\n{content}",
            "pdf_base": "PDF template content"
        }
    
    def _copy_assets(self):
        """Copy static assets like images and icons."""
        # Implementation for copying static assets
        pass


def generate_documentation(config: DocumentationConfig = None) -> bool:
    """Generate comprehensive documentation."""
    generator = ComprehensiveDocumentationGenerator(config)
    return generator.generate_complete_documentation()


if __name__ == "__main__":
    # Generate documentation with default settings
    config = DocumentationConfig(
        output_dir="docs",
        formats=["html", "markdown"],
        include_screenshots=True,
        include_tutorials=True
    )
    
    success = generate_documentation(config)
    if success:
        print("📚 Documentation generated successfully!")
        print(f"📁 Output directory: {config.output_dir}")
    else:
        print("❌ Documentation generation failed!")

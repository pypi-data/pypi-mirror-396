"""
Test Runner - Execute scenarios and generate reports
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

from .orchestrator import TestOrchestrator
from .scenario import TestScenario
from .config import EngineConfig

logger = logging.getLogger(__name__)


class TestRunner:
    """
    Execute multiple test scenarios and generate reports.
    
    Features:
    - Run multiple scenarios
    - Generate JUnit XML reports
    - Generate HTML reports
    - Summary statistics
    - Tag-based filtering
    """
    
    def __init__(self, config: Optional[EngineConfig] = None):
        self.config = config or EngineConfig.from_env()
        self.orchestrator = TestOrchestrator(self.config)
        self.scenarios: List[TestScenario] = []
        self.results: List[Dict[str, Any]] = []
    
    def add_scenario(self, scenario: TestScenario) -> "TestRunner":
        """Add a scenario to run"""
        self.scenarios.append(scenario)
        return self
    
    def add_scenarios(self, *scenarios: TestScenario) -> "TestRunner":
        """Add multiple scenarios to run"""
        self.scenarios.extend(scenarios)
        return self
    
    def run(
        self,
        tags: Optional[List[str]] = None,
        fail_fast: bool = False,
        generate_report: bool = True,
        report_path: Optional[Path] = None,
        open_browser: bool = False
    ) -> Dict[str, Any]:
        """
        Run all scenarios.
        
        Args:
            tags: Optional tags to filter scenarios
            fail_fast: Stop on first failure
            generate_report: Whether to automatically generate HTML report (default: True)
            report_path: Custom path for HTML report (default: reports/test_report_{timestamp}.html)
            open_browser: Whether to automatically open report in browser (default: False)
        
        Returns:
            Summary results dictionary
        """
        logger.info("🚀 Starting test run")
        start_time = time.time()
        
        # Filter scenarios by tags
        scenarios_to_run = self._filter_scenarios_by_tags(tags) if tags else self.scenarios
        
        if not scenarios_to_run:
            logger.warning("⚠️ No scenarios to run")
            return self._generate_summary(0)
        
        logger.info(f"📋 Running {len(scenarios_to_run)} scenarios")
        
        # Check services health before running
        health_status = self.orchestrator.check_services_health()
        if not all(health_status.values()):
            logger.error("❌ Some services are unhealthy, aborting test run")
            return self._generate_summary(time.time() - start_time)
        
        # Run scenarios
        for scenario in scenarios_to_run:
            try:
                result = self.orchestrator.execute_scenario(scenario)
                self.results.append(result)
                
                if fail_fast and result["status"] == "failed":
                    logger.warning("⚠️ Fail-fast enabled, stopping test run")
                    break
                
            except Exception as e:
                logger.error(f"❌ Scenario execution error: {e}")
                if fail_fast:
                    break
        
        # Cleanup
        try:
            self.orchestrator.cleanup()
        except Exception as e:
            logger.warning(f"⚠️ Cleanup failed: {e}")
        
        # Generate summary
        duration = time.time() - start_time
        summary = self._generate_summary(duration)
        
        logger.info(f"✅ Test run complete: {summary['passed']}/{summary['total']} passed")
        
        # Auto-generate HTML report
        if generate_report:
            if report_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_path = Path(f"reports/test_report_{timestamp}.html")
            self.generate_html_report(report_path, open_browser=open_browser)
        
        return summary
    
    def _filter_scenarios_by_tags(self, tags: List[str]) -> List[TestScenario]:
        """Filter scenarios by tags"""
        return [
            scenario for scenario in self.scenarios
            if any(tag in scenario.tags for tag in tags)
        ]
    
    def _generate_summary(self, duration: float) -> Dict[str, Any]:
        """Generate test run summary"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "passed")
        failed = sum(1 for r in self.results if r["status"] == "failed")
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            "results": self.results
        }
    
    def generate_junit_xml(self, output_path: Path):
        """
        Generate JUnit XML report.
        
        Args:
            output_path: Path to save XML file
        """
        from xml.etree.ElementTree import Element, SubElement, tostring
        from xml.dom import minidom
        
        testsuites = Element("testsuites")
        
        for result in self.results:
            testsuite = SubElement(testsuites, "testsuite")
            testsuite.set("name", result["scenario"])
            testsuite.set("tests", str(len(result["steps"])))
            testsuite.set("failures", str(sum(1 for s in result["steps"] if s["status"] == "failed")))
            testsuite.set("time", f"{result['duration']:.3f}")
            
            for step in result["steps"]:
                testcase = SubElement(testsuite, "testcase")
                testcase.set("name", step["description"])
                testcase.set("classname", result["scenario"])
                testcase.set("time", f"{step['duration']:.3f}")
                
                if step["status"] == "failed":
                    failure = SubElement(testcase, "failure")
                    failure.set("message", step.get("error", "Unknown error"))
                    failure.text = step.get("error", "")
        
        # Pretty print
        xml_str = minidom.parseString(tostring(testsuites)).toprettyxml(indent="  ")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(xml_str, encoding="utf-8")
        
        logger.info(f"📄 JUnit XML report saved: {output_path}")
    
    def generate_html_report(self, output_path: Path, open_browser: bool = False):
        """
        Generate interactive HTML report with search and filtering.
        
        Args:
            output_path: Path to save HTML file
            open_browser: Whether to automatically open report in browser
        """
        summary = self._generate_summary(0)
        
        # Escape HTML special characters in error messages
        def escape_html(text):
            if not text:
                return ""
            return (str(text)
                   .replace("&", "&amp;")
                   .replace("<", "&lt;")
                   .replace(">", "&gt;")
                   .replace('"', "&quot;")
                   .replace("'", "&#39;"))
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report - {summary['timestamp']}</title>
    <style>
        * {{
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            flex-wrap: wrap;
            gap: 20px;
        }}
        h1 {{
            color: #333;
            margin: 0;
            font-size: 36px;
        }}
        .meta {{
            color: #666;
            font-size: 14px;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }}
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat {{
            padding: 30px;
            border-radius: 12px;
            text-align: center;
            position: relative;
            overflow: hidden;
            transition: transform 0.2s;
        }}
        .stat:hover {{
            transform: translateY(-5px);
        }}
        .stat.total {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        .stat.passed {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; }}
        .stat.failed {{ background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%); color: white; }}
        .stat h2 {{ margin: 0; font-size: 56px; font-weight: bold; }}
        .stat p {{ margin: 10px 0 0 0; font-size: 18px; opacity: 0.9; }}
        .controls {{
            display: flex;
            gap: 15px;
            margin: 30px 0;
            flex-wrap: wrap;
            align-items: center;
        }}
        .search-box {{
            flex: 1;
            min-width: 250px;
        }}
        .search-box input {{
            width: 100%;
            padding: 12px 20px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }}
        .search-box input:focus {{
            outline: none;
            border-color: #667eea;
        }}
        .filter-buttons {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .filter-btn {{
            padding: 10px 20px;
            border: 2px solid #ddd;
            background: white;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s;
        }}
        .filter-btn:hover {{
            background: #f5f5f5;
        }}
        .filter-btn.active {{
            background: #667eea;
            color: white;
            border-color: #667eea;
        }}
        .scenario {{
            margin: 20px 0;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            overflow: hidden;
            transition: all 0.3s;
        }}
        .scenario:hover {{
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        .scenario-header {{
            padding: 20px;
            background: #f9f9f9;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            user-select: none;
        }}
        .scenario-header:hover {{
            background: #f0f0f0;
        }}
        .scenario-header.passed {{ border-left: 6px solid #4CAF50; }}
        .scenario-header.failed {{ border-left: 6px solid #f44336; }}
        .scenario-left {{
            display: flex;
            align-items: center;
            gap: 15px;
            flex: 1;
        }}
        .scenario-toggle {{
            font-size: 24px;
            transition: transform 0.3s;
        }}
        .scenario.collapsed .scenario-toggle {{
            transform: rotate(-90deg);
        }}
        .scenario-name {{ 
            font-size: 20px; 
            font-weight: bold;
            color: #333;
        }}
        .scenario-right {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        .scenario-status {{
            padding: 6px 18px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .scenario-status.passed {{ background: #4CAF50; color: white; }}
        .scenario-status.failed {{ background: #f44336; color: white; }}
        .scenario-duration {{
            color: #666;
            font-size: 14px;
            font-weight: 500;
        }}
        .steps {{
            padding: 20px;
            background: white;
            max-height: 1000px;
            overflow: hidden;
            transition: max-height 0.5s ease-out;
        }}
        .scenario.collapsed .steps {{
            max-height: 0;
            padding: 0 20px;
        }}
        .step {{
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            border-left: 4px solid transparent;
            transition: all 0.2s;
        }}
        .step:hover {{
            transform: translateX(5px);
        }}
        .step.passed {{ 
            background: #e8f5e9; 
            border-left-color: #4CAF50;
        }}
        .step.failed {{ 
            background: #ffebee; 
            border-left-color: #f44336;
        }}
        .step-left {{
            flex: 1;
        }}
        .step-type {{
            display: inline-block;
            padding: 4px 12px;
            background: #667eea;
            color: white;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 8px;
        }}
        .step-description {{ 
            color: #333;
            font-size: 15px;
            line-height: 1.6;
        }}
        .step-duration {{ 
            color: #999; 
            font-size: 13px;
            white-space: nowrap;
            margin-left: 15px;
            font-weight: 500;
        }}
        .error {{
            background: #fff3f3;
            border: 2px solid #f44336;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
            color: #c62828;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.6;
            white-space: pre-wrap;
            word-break: break-word;
        }}
        .error-title {{
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 8px;
            color: #d32f2f;
        }}
        .no-results {{
            text-align: center;
            padding: 60px 20px;
            color: #999;
            font-size: 18px;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            background: #e0e0e0;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>🧪 Test Report</h1>
                <div class="meta">
                    <div class="meta-item">
                        <span>📅</span>
                        <span>{summary['timestamp']}</span>
                    </div>
                    <div class="meta-item">
                        <span>⏱️</span>
                        <span>{summary['duration']:.2f}s</span>
                    </div>
                    <div class="meta-item">
                        <span>🔧</span>
                        <span>testing-engine-core v0.3.0</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="summary">
            <div class="stat total">
                <h2>{summary['total']}</h2>
                <p>Total Scenarios</p>
            </div>
            <div class="stat passed">
                <h2>{summary['passed']}</h2>
                <p>Passed</p>
            </div>
            <div class="stat failed">
                <h2>{summary['failed']}</h2>
                <p>Failed</p>
            </div>
        </div>
        
        <div class="controls">
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="🔍 Search scenarios and steps...">
            </div>
            <div class="filter-buttons">
                <button class="filter-btn active" data-filter="all">All</button>
                <button class="filter-btn" data-filter="passed">Passed Only</button>
                <button class="filter-btn" data-filter="failed">Failed Only</button>
                <button class="filter-btn" id="expandAll">Expand All</button>
                <button class="filter-btn" id="collapseAll">Collapse All</button>
            </div>
        </div>
        
        <div id="scenariosContainer">
"""
        
        for idx, result in enumerate(self.results):
            steps_html = ""
            for step in result["steps"]:
                error_html = ""
                if step.get("error"):
                    error_html = f"""
                <div class="error">
                    <div class="error-title">❌ Error Details:</div>
                    {escape_html(step['error'])}
                </div>
"""
                
                steps_html += f"""
                <div class="step {step['status']}">
                    <div class="step-left">
                        <div class="step-type">{escape_html(step['type'])}</div>
                        <div class="step-description">{escape_html(step['description'])}</div>
                        {error_html}
                    </div>
                    <div class="step-duration">{step['duration']:.3f}s</div>
                </div>
"""
            
            passed_count = sum(1 for s in result["steps"] if s["status"] == "passed")
            failed_count = sum(1 for s in result["steps"] if s["status"] == "failed")
            
            html += f"""
        <div class="scenario" data-status="{result['status']}" data-scenario-id="{idx}">
            <div class="scenario-header {result['status']}" onclick="toggleScenario({idx})">
                <div class="scenario-left">
                    <span class="scenario-toggle">▼</span>
                    <div class="scenario-name">{escape_html(result['scenario'])}</div>
                </div>
                <div class="scenario-right">
                    <span class="badge">{passed_count} passed, {failed_count} failed</span>
                    <span class="scenario-status {result['status']}">{result['status']}</span>
                    <span class="scenario-duration">{result['duration']:.2f}s</span>
                </div>
            </div>
            <div class="steps">
                {steps_html}
            </div>
        </div>
"""
        
        html += """
        </div>
        <div class="no-results" id="noResults" style="display: none;">
            <p>No scenarios match your search or filter criteria.</p>
        </div>
    </div>
    
    <script>
        // Search functionality
        const searchInput = document.getElementById('searchInput');
        const scenariosContainer = document.getElementById('scenariosContainer');
        const scenarios = document.querySelectorAll('.scenario');
        const noResults = document.getElementById('noResults');
        
        let currentFilter = 'all';
        
        searchInput.addEventListener('input', filterScenarios);
        
        document.querySelectorAll('.filter-btn[data-filter]').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.filter-btn[data-filter]').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                currentFilter = this.dataset.filter;
                filterScenarios();
            });
        });
        
        function filterScenarios() {
            const searchTerm = searchInput.value.toLowerCase();
            let visibleCount = 0;
            
            scenarios.forEach(scenario => {
                const scenarioText = scenario.textContent.toLowerCase();
                const status = scenario.dataset.status;
                
                const matchesSearch = searchTerm === '' || scenarioText.includes(searchTerm);
                const matchesFilter = currentFilter === 'all' || status === currentFilter;
                
                if (matchesSearch && matchesFilter) {
                    scenario.style.display = 'block';
                    visibleCount++;
                } else {
                    scenario.style.display = 'none';
                }
            });
            
            noResults.style.display = visibleCount === 0 ? 'block' : 'none';
            scenariosContainer.style.display = visibleCount === 0 ? 'none' : 'block';
        }
        
        function toggleScenario(id) {
            const scenario = document.querySelector(`[data-scenario-id="${id}"]`);
            scenario.classList.toggle('collapsed');
        }
        
        document.getElementById('expandAll').addEventListener('click', () => {
            scenarios.forEach(s => s.classList.remove('collapsed'));
        });
        
        document.getElementById('collapseAll').addEventListener('click', () => {
            scenarios.forEach(s => s.classList.add('collapsed'));
        });
        
        // Auto-expand failed scenarios on load
        document.addEventListener('DOMContentLoaded', () => {
            scenarios.forEach(scenario => {
                if (scenario.dataset.status === 'failed') {
                    scenario.classList.remove('collapsed');
                } else {
                    scenario.classList.add('collapsed');
                }
            });
        });
    </script>
</body>
</html>
"""
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")
        
        abs_path = output_path.absolute()
        logger.info(f"📄 HTML report saved: {abs_path}")
        
        # Format path for Windows file:// URLs (forward slashes)
        file_url = abs_path.as_uri()
        
        print(f"\n{'='*70}")
        print(f"📊 HTML Test Report Generated")
        print(f"{'='*70}")
        print(f"📁 Location: {abs_path}")
        print(f"🌐 Open in browser: {file_url}")
        print(f"{'='*70}\n")
        
        if open_browser:
            import webbrowser
            webbrowser.open(file_url)
            logger.info("🌐 Opened report in default browser")
    
    def generate_json_report(self, output_path: Path):
        """
        Generate JSON report.
        
        Args:
            output_path: Path to save JSON file
        """
        summary = self._generate_summary(0)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(summary, indent=2),
            encoding="utf-8"
        )
        
        logger.info(f"📄 JSON report saved: {output_path}")
    
    def close(self):
        """Close orchestrator connections"""
        self.orchestrator.close()

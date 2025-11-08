#!/usr/bin/env python3
"""
PrayerOffline - Project Diagnostic & Auto-Fix Tool
Scans all project files, identifies issues, and applies automatic fixes.
"""

import os
import sys
import ast
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Issue:
    """Represents a code issue found during diagnostics"""
    file_path: str
    line_number: int
    severity: str  # 'error', 'warning', 'info'
    category: str
    message: str
    fix_available: bool = False
    fix_applied: bool = False


@dataclass
class DiagnosticReport:
    """Complete diagnostic report"""
    timestamp: str
    total_files: int
    issues: List[Issue] = field(default_factory=list)
    fixes_applied: int = 0
    
    def add_issue(self, issue: Issue):
        self.issues.append(issue)
    
    def get_summary(self) -> Dict:
        return {
            'total_files_scanned': self.total_files,
            'total_issues': len(self.issues),
            'errors': len([i for i in self.issues if i.severity == 'error']),
            'warnings': len([i for i in self.issues if i.severity == 'warning']),
            'fixes_applied': self.fixes_applied
        }


class ProjectDiagnostic:
    """Main diagnostic and auto-fix engine"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.report = DiagnosticReport(
            timestamp=datetime.now().isoformat(),
            total_files=0
        )
        self.required_structure = {
            'dirs': [
                'views', 'services', 'components', 'utils', 
                'assets', 'assets/audio', 'assets/icons',
                'i18n', 'tests', 'config'
            ],
            'files': [
                'main.py', 'app.py', 'requirements.txt',
                'README.md', 'i18n/strings.json'
            ]
        }
    
    def run_full_diagnostic(self) -> DiagnosticReport:
        """Run complete project diagnostic"""
        print("🔍 Starting PrayerOffline Project Diagnostic...\n")
        
        # 1. Check project structure
        print("📁 Checking project structure...")
        self.check_project_structure()
        
        # 2. Validate Python files
        print("🐍 Validating Python files...")
        self.validate_python_files()
        
        # 3. Check dependencies
        print("📦 Checking dependencies...")
        self.check_dependencies()
        
        # 4. Validate imports
        print("📥 Validating imports...")
        self.validate_imports()
        
        # 5. Check for common issues
        print("🔧 Checking for common issues...")
        self.check_common_issues()
        
        # 6. Validate configuration files
        print("⚙️  Validating configuration...")
        self.validate_config_files()
        
        print("\n✅ Diagnostic complete!\n")
        return self.report
    
    def check_project_structure(self):
        """Check and create missing directories and __init__.py files"""
        # Check directories
        for dir_name in self.required_structure['dirs']:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    self.report.add_issue(Issue(
                        file_path=str(dir_path),
                        line_number=0,
                        severity='warning',
                        category='structure',
                        message=f'Missing directory created: {dir_name}',
                        fix_available=True,
                        fix_applied=True
                    ))
                    self.report.fixes_applied += 1
                except Exception as e:
                    self.report.add_issue(Issue(
                        file_path=str(dir_path),
                        line_number=0,
                        severity='error',
                        category='structure',
                        message=f'Cannot create directory: {e}'
                    ))
        
        # Create __init__.py files
        python_dirs = ['views', 'services', 'components', 'utils', 'tests']
        for dir_name in python_dirs:
            init_file = self.project_root / dir_name / '__init__.py'
            if not init_file.exists():
                try:
                    init_file.parent.mkdir(parents=True, exist_ok=True)
                    init_file.write_text('"""Package initialization"""\n')
                    self.report.add_issue(Issue(
                        file_path=str(init_file),
                        line_number=0,
                        severity='info',
                        category='structure',
                        message=f'Created missing __init__.py',
                        fix_available=True,
                        fix_applied=True
                    ))
                    self.report.fixes_applied += 1
                except Exception as e:
                    self.report.add_issue(Issue(
                        file_path=str(init_file),
                        line_number=0,
                        severity='error',
                        category='structure',
                        message=f'Cannot create __init__.py: {e}'
                    ))
    
    def validate_python_files(self):
        """Validate Python syntax and structure"""
        for py_file in self.project_root.rglob('*.py'):
            if 'venv' in str(py_file) or '.venv' in str(py_file):
                continue
            
            self.report.total_files += 1
            try:
                content = py_file.read_text(encoding='utf-8')
                
                # Check syntax
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    self.report.add_issue(Issue(
                        file_path=str(py_file),
                        line_number=e.lineno or 0,
                        severity='error',
                        category='syntax',
                        message=f'Syntax error: {e.msg}'
                    ))
                    continue
                
                # Check for common issues
                self._check_file_issues(py_file, content)
                
            except Exception as e:
                self.report.add_issue(Issue(
                    file_path=str(py_file),
                    line_number=0,
                    severity='error',
                    category='file',
                    message=f'Cannot read file: {e}'
                ))
    
    def _check_file_issues(self, file_path: Path, content: str):
        """Check for specific issues in Python files"""
        lines = content.split('\n')
        
        # Check for localStorage/sessionStorage usage (forbidden in Flet artifacts)
        for i, line in enumerate(lines, 1):
            if 'localStorage' in line or 'sessionStorage' in line:
                self.report.add_issue(Issue(
                    file_path=str(file_path),
                    line_number=i,
                    severity='error',
                    category='forbidden_api',
                    message='localStorage/sessionStorage not supported in Flet. Use in-memory storage.',
                    fix_available=False
                ))
            
            # Check for missing encoding in file operations
            if re.search(r'open\([^)]*\)(?!.*encoding)', line) and 'encoding' not in line:
                if 'rb' not in line and 'wb' not in line:
                    self.report.add_issue(Issue(
                        file_path=str(file_path),
                        line_number=i,
                        severity='warning',
                        category='encoding',
                        message='File opened without encoding. Add encoding="utf-8"',
                        fix_available=True
                    ))
            
            # Check for bare except
            if re.match(r'^\s*except\s*:\s*$', line):
                self.report.add_issue(Issue(
                    file_path=str(file_path),
                    line_number=i,
                    severity='warning',
                    category='exception',
                    message='Bare except clause. Specify exception type.',
                    fix_available=False
                ))
    
    def check_dependencies(self):
        """Check and fix requirements.txt"""
        req_file = self.project_root / 'requirements.txt'
        
        required_deps = {
            'flet': '>=0.21.0',
            'plyer': '>=2.1.0',
            'prayer-times': '>=0.3.0',
            'hijri-converter': '>=2.3.1',
            'pytz': '>=2023.3',
            'pydantic': '>=2.0.0'
        }
        
        if not req_file.exists():
            # Create requirements.txt
            content = '\n'.join([f'{k}{v}' for k, v in required_deps.items()])
            req_file.write_text(content)
            self.report.add_issue(Issue(
                file_path=str(req_file),
                line_number=0,
                severity='error',
                category='dependencies',
                message='requirements.txt missing - created with default dependencies',
                fix_available=True,
                fix_applied=True
            ))
            self.report.fixes_applied += 1
        else:
            # Check existing requirements
            content = req_file.read_text()
            existing_deps = set()
            for line in content.split('\n'):
                if line.strip() and not line.startswith('#'):
                    dep_name = line.split('>=')[0].split('==')[0].strip()
                    existing_deps.add(dep_name)
            
            missing_deps = set(required_deps.keys()) - existing_deps
            if missing_deps:
                self.report.add_issue(Issue(
                    file_path=str(req_file),
                    line_number=0,
                    severity='warning',
                    category='dependencies',
                    message=f'Missing dependencies: {", ".join(missing_deps)}',
                    fix_available=True
                ))
    
    def validate_imports(self):
        """Check for import issues"""
        for py_file in self.project_root.rglob('*.py'):
            if 'venv' in str(py_file) or '.venv' in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self._check_import(py_file, node.lineno, alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self._check_import(py_file, node.lineno, node.module)
            
            except Exception:
                pass  # Already caught in syntax validation
    
    def _check_import(self, file_path: Path, line_no: int, module_name: str):
        """Check if import is valid"""
        # Check for relative imports that might fail
        if module_name.startswith('.'):
            # Check if __init__.py exists in parent
            parent_init = file_path.parent / '__init__.py'
            if not parent_init.exists():
                self.report.add_issue(Issue(
                    file_path=str(file_path),
                    line_number=line_no,
                    severity='warning',
                    category='import',
                    message=f'Relative import but missing __init__.py in {file_path.parent.name}',
                    fix_available=True
                ))
    
    def check_common_issues(self):
        """Check for common coding issues"""
        for py_file in self.project_root.rglob('*.py'):
            if 'venv' in str(py_file) or '.venv' in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                
                # Check for print statements (should use logging)
                if 'def ' in content or 'class ' in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if re.search(r'^\s*print\(', line):
                            self.report.add_issue(Issue(
                                file_path=str(py_file),
                                line_number=i,
                                severity='info',
                                category='best_practice',
                                message='Consider using logging instead of print()',
                                fix_available=False
                            ))
                
                # Check for TODO/FIXME comments
                for i, line in enumerate(content.split('\n'), 1):
                    if 'TODO' in line or 'FIXME' in line:
                        self.report.add_issue(Issue(
                            file_path=str(py_file),
                            line_number=i,
                            severity='info',
                            category='todo',
                            message=f'Unresolved: {line.strip()}',
                            fix_available=False
                        ))
            
            except Exception:
                pass
    
    def validate_config_files(self):
        """Validate JSON and YAML config files"""
        # Check strings.json
        i18n_file = self.project_root / 'i18n' / 'strings.json'
        if not i18n_file.exists():
            self.report.add_issue(Issue(
                file_path=str(i18n_file),
                line_number=0,
                severity='error',
                category='config',
                message='Missing i18n/strings.json',
                fix_available=True
            ))
        else:
            try:
                content = i18n_file.read_text(encoding='utf-8')
                json.loads(content)
            except json.JSONDecodeError as e:
                self.report.add_issue(Issue(
                    file_path=str(i18n_file),
                    line_number=e.lineno,
                    severity='error',
                    category='config',
                    message=f'Invalid JSON: {e.msg}'
                ))
    
    def generate_report(self, output_file: str = 'diagnostic_report.txt'):
        """Generate human-readable report"""
        report_path = self.project_root / output_file
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("PrayerOffline - Project Diagnostic Report\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Timestamp: {self.report.timestamp}\n")
            f.write(f"Project Root: {self.project_root.absolute()}\n\n")
            
            summary = self.report.get_summary()
            f.write("SUMMARY\n")
            f.write("-" * 70 + "\n")
            f.write(f"Total Files Scanned: {summary['total_files_scanned']}\n")
            f.write(f"Total Issues Found: {summary['total_issues']}\n")
            f.write(f"  - Errors: {summary['errors']}\n")
            f.write(f"  - Warnings: {summary['warnings']}\n")
            f.write(f"  - Info: {summary['total_issues'] - summary['errors'] - summary['warnings']}\n")
            f.write(f"Fixes Applied: {summary['fixes_applied']}\n\n")
            
            if self.report.issues:
                f.write("DETAILED ISSUES\n")
                f.write("-" * 70 + "\n\n")
                
                for issue in sorted(self.report.issues, key=lambda x: (x.severity, x.file_path)):
                    icon = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}.get(issue.severity, '•')
                    f.write(f"{icon} [{issue.severity.upper()}] {issue.category}\n")
                    f.write(f"   File: {issue.file_path}\n")
                    if issue.line_number > 0:
                        f.write(f"   Line: {issue.line_number}\n")
                    f.write(f"   Message: {issue.message}\n")
                    if issue.fix_applied:
                        f.write(f"   ✓ Fix Applied\n")
                    elif issue.fix_available:
                        f.write(f"   🔧 Fix Available\n")
                    f.write("\n")
            
            f.write("=" * 70 + "\n")
            f.write("End of Report\n")
            f.write("=" * 70 + "\n")
        
        return report_path
    
    def print_summary(self):
        """Print summary to console"""
        summary = self.report.get_summary()
        
        print("\n" + "=" * 70)
        print("DIAGNOSTIC SUMMARY")
        print("=" * 70)
        print(f"📊 Files Scanned: {summary['total_files_scanned']}")
        print(f"🔍 Total Issues: {summary['total_issues']}")
        print(f"   ❌ Errors: {summary['errors']}")
        print(f"   ⚠️  Warnings: {summary['warnings']}")
        print(f"   ℹ️  Info: {summary['total_issues'] - summary['errors'] - summary['warnings']}")
        print(f"🔧 Fixes Applied: {summary['fixes_applied']}")
        print("=" * 70)
        
        if summary['errors'] > 0:
            print("\n❌ Critical errors found! Review diagnostic_report.txt for details.")
        elif summary['warnings'] > 0:
            print("\n⚠️  Warnings found. Review diagnostic_report.txt for details.")
        else:
            print("\n✅ No critical issues found! Project looks good.")


def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║     PrayerOffline - Project Diagnostic & Auto-Fix Tool       ║
║                    Version 1.0                                ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Determine project root
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    
    # Run diagnostic
    diagnostic = ProjectDiagnostic(project_root)
    diagnostic.run_full_diagnostic()
    
    # Generate report
    report_path = diagnostic.generate_report()
    print(f"\n📄 Detailed report saved to: {report_path}")
    
    # Print summary
    diagnostic.print_summary()
    
    # Return exit code based on errors
    summary = diagnostic.report.get_summary()
    sys.exit(1 if summary['errors'] > 0 else 0)


if __name__ == '__main__':
    main()
"""
Migration utilities for transitioning from legacy tutorial systems to the unified system.

This module provides functions to:
- Backup legacy tutorial files
- Update import statements throughout the codebase
- Validate migration completeness
- Generate migration reports
"""

import os
import shutil
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import warnings


def backup_legacy_files(source_dir: str = ".", backup_dir: str = "archive/tutorials") -> bool:
    """
    Backup legacy tutorial files to archive directory.
    
    Args:
        source_dir: Directory containing legacy files
        backup_dir: Directory to store backups
        
    Returns:
        True if backup successful, False otherwise
    """
    try:
        # Create backup directory
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Legacy files to backup
        legacy_files = [
            "tutorial_system.py",
            "integrated_tutorial_system.py", 
            "comprehensive_tutorial_system.py",
            "tutorial_integration.py"
        ]
        
        backed_up_files = []
        
        for file_name in legacy_files:
            source_file = Path(source_dir) / file_name
            if source_file.exists():
                backup_file = backup_path / file_name
                shutil.copy2(source_file, backup_file)
                backed_up_files.append(file_name)
                print(f"✓ Backed up: {file_name}")
        
        # Create backup manifest
        manifest_file = backup_path / "backup_manifest.txt"
        with open(manifest_file, 'w') as f:
            f.write("Legacy Tutorial System Backup\n")
            f.write("=" * 40 + "\n\n")
            f.write("Backed up files:\n")
            for file_name in backed_up_files:
                f.write(f"- {file_name}\n")
            f.write(f"\nBackup created: {backup_path.absolute()}\n")
        
        print(f"✓ Backup completed: {len(backed_up_files)} files backed up to {backup_path}")
        return True
        
    except Exception as e:
        print(f"✗ Backup failed: {e}")
        return False


def find_import_statements(directory: str = ".") -> List[Tuple[str, int, str]]:
    """
    Find all import statements referencing legacy tutorial systems.
    
    Args:
        directory: Directory to search for Python files
        
    Returns:
        List of tuples (file_path, line_number, import_statement)
    """
    import_patterns = [
        r'from\s+tutorial_system\s+import',
        r'import\s+tutorial_system',
        r'from\s+integrated_tutorial_system\s+import',
        r'import\s+integrated_tutorial_system',
        r'from\s+comprehensive_tutorial_system\s+import',
        r'import\s+comprehensive_tutorial_system',
        r'from\s+tutorial_integration\s+import',
        r'import\s+tutorial_integration'
    ]
    
    found_imports = []
    
    for root, dirs, files in os.walk(directory):
        # Skip archive and backup directories
        dirs[:] = [d for d in dirs if d not in ['archive', '__pycache__', '.git']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            for pattern in import_patterns:
                                if re.search(pattern, line):
                                    found_imports.append((file_path, line_num, line.strip()))
                except Exception as e:
                    print(f"Warning: Could not read {file_path}: {e}")
    
    return found_imports


def update_import_statements(directory: str = ".", dry_run: bool = True) -> Dict[str, Any]:
    """
    Update import statements to use the unified tutorial system.
    
    Args:
        directory: Directory to update
        dry_run: If True, only show what would be changed without making changes
        
    Returns:
        Dictionary with update results
    """
    # Import replacement mappings
    replacements = {
        # Legacy tutorial system
        r'from\s+tutorial_system\s+import\s+TutorialManager': 
            'from tutorials import UnifiedTutorialManager as TutorialManager',
        r'from\s+tutorial_system\s+import\s+TutorialDialog':
            'from tutorials import UnifiedTutorialSelectionDialog as TutorialDialog',
        r'import\s+tutorial_system':
            'import tutorials.unified_tutorial_system as tutorial_system',
        
        # Integrated tutorial system  
        r'from\s+integrated_tutorial_system\s+import\s+InteractiveTutorialManager':
            'from tutorials import UnifiedTutorialManager as InteractiveTutorialManager',
        r'import\s+integrated_tutorial_system':
            'import tutorials.unified_tutorial_system as integrated_tutorial_system',
        
        # Comprehensive tutorial system
        r'from\s+comprehensive_tutorial_system\s+import\s+.*':
            'from tutorials import UnifiedTutorialManager',
        r'import\s+comprehensive_tutorial_system':
            'import tutorials.unified_tutorial_system as comprehensive_tutorial_system',
        
        # Tutorial integration
        r'from\s+tutorial_integration\s+import\s+TutorialIntegrationManager':
            'from tutorials import UnifiedTutorialManager as TutorialIntegrationManager',
        r'import\s+tutorial_integration':
            'import tutorials.unified_tutorial_system as tutorial_integration'
    }
    
    results = {
        'files_processed': 0,
        'files_updated': 0,
        'total_replacements': 0,
        'changes': []
    }
    
    for root, dirs, files in os.walk(directory):
        # Skip archive and backup directories
        dirs[:] = [d for d in dirs if d not in ['archive', '__pycache__', '.git']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                results['files_processed'] += 1
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    file_changes = []
                    
                    # Apply replacements
                    for pattern, replacement in replacements.items():
                        matches = re.findall(pattern, content)
                        if matches:
                            content = re.sub(pattern, replacement, content)
                            file_changes.extend(matches)
                            results['total_replacements'] += len(matches)
                    
                    # If changes were made
                    if content != original_content:
                        results['files_updated'] += 1
                        results['changes'].append({
                            'file': file_path,
                            'changes': file_changes
                        })
                        
                        if not dry_run:
                            # Write updated content
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            print(f"✓ Updated: {file_path}")
                        else:
                            print(f"Would update: {file_path}")
                
                except Exception as e:
                    print(f"Warning: Could not process {file_path}: {e}")
    
    return results


def validate_migration() -> Dict[str, Any]:
    """
    Validate that migration from legacy systems is complete.
    
    Returns:
        Dictionary with validation results
    """
    validation_results = {
        'legacy_imports_found': [],
        'missing_unified_imports': [],
        'plugin_status': {},
        'tutorial_count': {},
        'validation_passed': True
    }
    
    # Check for remaining legacy imports
    legacy_imports = find_import_statements()
    if legacy_imports:
        validation_results['legacy_imports_found'] = legacy_imports
        validation_results['validation_passed'] = False
        print(f"✗ Found {len(legacy_imports)} legacy import statements")
    else:
        print("✓ No legacy import statements found")
    
    # Check unified system availability
    try:
        from tutorials import UnifiedTutorialManager
        print("✓ Unified tutorial system imports successfully")
    except ImportError as e:
        validation_results['missing_unified_imports'].append(str(e))
        validation_results['validation_passed'] = False
        print(f"✗ Cannot import unified tutorial system: {e}")
    
    # Check plugin loading
    try:
        from tutorials.unified_tutorial_system import PluginManager
        plugin_manager = PluginManager()
        loaded_count = plugin_manager.load_all_plugins()
        
        validation_results['plugin_status'] = {
            'loaded_plugins': loaded_count,
            'plugin_metadata': plugin_manager.plugin_metadata
        }
        
        # Count tutorials by category
        all_tutorials = plugin_manager.get_all_tutorials()
        validation_results['tutorial_count']['total'] = len(all_tutorials)
        
        from tutorials.unified_tutorial_system import TutorialCategory
        for category in TutorialCategory:
            category_tutorials = plugin_manager.get_tutorials_by_category(category)
            validation_results['tutorial_count'][category.value] = len(category_tutorials)
        
        print(f"✓ Plugin system working: {loaded_count} plugins, {len(all_tutorials)} tutorials")
        
    except Exception as e:
        validation_results['plugin_status']['error'] = str(e)
        validation_results['validation_passed'] = False
        print(f"✗ Plugin system error: {e}")
    
    return validation_results


def migrate_legacy_tutorials(backup_first: bool = True, dry_run: bool = True) -> bool:
    """
    Complete migration from legacy tutorial systems.
    
    Args:
        backup_first: Whether to backup legacy files before migration
        dry_run: If True, only show what would be done without making changes
        
    Returns:
        True if migration successful, False otherwise
    """
    print("=" * 60)
    print("LEGACY TUTORIAL SYSTEM MIGRATION")
    print("=" * 60)
    
    try:
        # Step 1: Backup legacy files
        if backup_first:
            print("\n1. Backing up legacy files...")
            if not backup_legacy_files():
                print("✗ Backup failed, aborting migration")
                return False
        
        # Step 2: Update import statements
        print("\n2. Updating import statements...")
        update_results = update_import_statements(dry_run=dry_run)
        
        print(f"Files processed: {update_results['files_processed']}")
        print(f"Files to update: {update_results['files_updated']}")
        print(f"Total replacements: {update_results['total_replacements']}")
        
        if dry_run:
            print("\n(This was a dry run - no files were actually modified)")
        
        # Step 3: Validate migration
        print("\n3. Validating migration...")
        validation_results = validate_migration()
        
        if validation_results['validation_passed']:
            print("\n✓ Migration validation passed!")
            return True
        else:
            print("\n✗ Migration validation failed!")
            if validation_results['legacy_imports_found']:
                print("Legacy imports still found:")
                for file_path, line_num, import_stmt in validation_results['legacy_imports_found'][:5]:
                    print(f"  {file_path}:{line_num} - {import_stmt}")
            return False
    
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        return False


def add_deprecation_warnings(directory: str = ".", dry_run: bool = True) -> int:
    """
    Add deprecation warnings to legacy tutorial entry points.
    
    Args:
        directory: Directory to search for legacy files
        dry_run: If True, only show what would be done
        
    Returns:
        Number of files updated
    """
    deprecation_warning = '''import warnings
warnings.warn(
    "This tutorial system is deprecated. Please use Tools → Tutorials → Interactive Tutorial System instead.",
    DeprecationWarning,
    stacklevel=2
)

'''
    
    legacy_files = [
        "tutorial_system.py",
        "integrated_tutorial_system.py",
        "comprehensive_tutorial_system.py"
    ]
    
    files_updated = 0
    
    for file_name in legacy_files:
        file_path = Path(directory) / file_name
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if deprecation warning already exists
                if 'DeprecationWarning' not in content:
                    # Find the first import or class definition
                    lines = content.split('\n')
                    insert_index = 0
                    
                    for i, line in enumerate(lines):
                        if line.strip().startswith(('import ', 'from ', 'class ', 'def ')):
                            insert_index = i
                            break
                    
                    # Insert deprecation warning
                    lines.insert(insert_index, deprecation_warning)
                    new_content = '\n'.join(lines)
                    
                    if not dry_run:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"✓ Added deprecation warning to: {file_name}")
                    else:
                        print(f"Would add deprecation warning to: {file_name}")
                    
                    files_updated += 1
                else:
                    print(f"Deprecation warning already exists in: {file_name}")
            
            except Exception as e:
                print(f"Error processing {file_name}: {e}")
    
    return files_updated


if __name__ == "__main__":
    # Run migration with dry run first
    print("Running migration dry run...")
    migrate_legacy_tutorials(backup_first=True, dry_run=True)
    
    print("\nTo perform actual migration, run:")
    print("python -c \"from tutorials.utils.migration import migrate_legacy_tutorials; migrate_legacy_tutorials(dry_run=False)\"")

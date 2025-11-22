#!/usr/bin/env python3
"""Analyze Phase 2 progress from tasks.md"""
import re

def analyze_phase2_progress():
    with open('specs/002-commercial-management-phase2/tasks.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    phases = {
        'Phase 0: US12 - Advanced Product Management (P1)': {
            'start_marker': '## Phase 0: User Story 12',
            'end_marker': '## Phase 1: User Story 7'
        },
        'Phase 1: US7 - Invoicing (P1)': {
            'start_marker': '## Phase 1: User Story 7',
            'end_marker': '## Phase 2: User Story 8'
        },
        'Phase 2: US8 - Payments (P1)': {
            'start_marker': '## Phase 2: User Story 8',
            'end_marker': '## Phase 3: User Story 9'
        },
        'Phase 3: US9 - Purchasing (P2)': {
            'start_marker': '## Phase 3: User Story 9',
            'end_marker': '## Phase 4: User Story 10'
        },
        'Phase 4: US10 - Multi-Location (P2)': {
            'start_marker': '## Phase 4: User Story 10',
            'end_marker': '## Phase 5: User Story 11'
        },
        'Phase 5: US11 - Reporting (P2)': {
            'start_marker': '## Phase 5: User Story 11',
            'end_marker': '## Dependencies'
        }
    }
    
    lines = content.split('\n')
    results = {}
    
    for phase_name, markers in phases.items():
        start_idx = None
        end_idx = None
        
        for i, line in enumerate(lines):
            if markers['start_marker'] in line:
                start_idx = i
            if start_idx is not None and markers['end_marker'] in line:
                end_idx = i
                break
        
        if start_idx is None:
            continue
        
        if end_idx is None:
            end_idx = len(lines)
        
        section = '\n'.join(lines[start_idx:end_idx])
        
        completed = len(re.findall(r'- \[x\]', section, re.IGNORECASE))
        total = len(re.findall(r'- \[[ xX]\]', section))
        
        results[phase_name] = {
            'completed': completed,
            'total': total,
            'percentage': (completed * 100 // total) if total > 0 else 0,
            'remaining': total - completed
        }
    
    # Print results
    print("=" * 70)
    print("PHASE 2 DEVELOPMENT PROGRESS")
    print("=" * 70)
    print()
    
    total_completed = 0
    total_tasks = 0
    
    for phase_name, stats in results.items():
        if stats['percentage'] == 100:
            status = "[COMPLETE]"
        elif stats['percentage'] >= 50:
            status = "[IN PROGRESS]"
        else:
            status = "[PENDING]"
        print(f"{status} {phase_name}")
        print(f"   Progress: {stats['completed']}/{stats['total']} ({stats['percentage']}%)")
        if stats['remaining'] > 0:
            print(f"   Remaining: {stats['remaining']} tasks")
        print()
        total_completed += stats['completed']
        total_tasks += stats['total']
    
    print("=" * 70)
    print(f"OVERALL PROGRESS: {total_completed}/{total_tasks} ({total_completed * 100 // total_tasks if total_tasks > 0 else 0}%)")
    print("=" * 70)
    print()
    
    # Show what's next
    print("NEXT PRIORITIES:")
    print("-" * 70)
    for phase_name, stats in results.items():
        if stats['remaining'] > 0:
            print(f"  • {phase_name}: {stats['remaining']} tasks remaining")
    print()

if __name__ == '__main__':
    analyze_phase2_progress()


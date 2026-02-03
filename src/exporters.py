import json
import csv
import html
import os
from datetime import datetime


def _get_html_style():
    """Get HTML styles - same as your original."""
    return """
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            margin: 20px;
            line-height: 1.5;
            color: #333;
        }
        table { 
            border-collapse: collapse; 
            width: 100%; 
            margin-top: 10px;
            margin-bottom: 40px;
        }
        th, td { 
            border: 1px solid #ddd; 
            padding: 12px; 
            text-align: left;
            font-family: inherit;
        }
        th { 
            background-color: #f2f2f2;
            font-weight: 600;
        }
        .path1 { background-color: #ffeeee; }
        .path2 { background-color: ##BFE1F7; }
        .mismatch { background-color: #fff3cd; }
        .path-header { 
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            margin: 30px 0;
            border: 1px solid #ddd;
        }
        .path-header h3 {
            margin: 0 0 10px 0;
            font-size: 1.2em;
            color: #333;
        }
        .path-text {
            font-family: inherit;
            background-color: #fff;
            padding: 10px;
            border-radius: 4px;
            border: 1px solid #ddd;
            word-break: break-all;
            margin-bottom: 5px;
        }
        .section {
            margin-bottom: 40px;
        }
        .mode-info {
            background-color: #e9ecef;
            padding: 10px 20px;
            border-radius: 4px;
            margin-bottom: 20px;
            border: 1px solid #dee2e6;
            display: inline-block;
        }
        .dir-list {
            list-style-type: none;
            padding: 0;
            margin: 0;
        }
        .dir-list li {
            margin-bottom: 5px;
        }
        .warning-box {
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 6px;
            padding: 20px;
            margin: 30px 0;
        }
        .warning-box h3 {
            margin: 0 0 15px 0;
            color: #856404;
        }
    """


def export_to_json(data, output_file):
    """Export results to JSON format - maintains your original structure."""
    results = {
        'mode': data['mode'],
        'comparison_time': datetime.now().isoformat(),
        'group1': {
            'directories': data.get('dirs1', [data['path1']]),
            'combined_path': data['path1']
        },
        'group2': {
            'directories': data.get('dirs2', [data['path2']]),
            'combined_path': data['path2']
        },
        'files_only_in_group1': data['unique1'],
        'files_only_in_group2': data['unique2']
    }
    
    # Add frame mismatches if in advanced mode
    if 'frame_mismatches' in data:
        results['frame_count_mismatches'] = data['frame_mismatches']
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)


def export_to_txt(data, output_file):
    """Export results to text format - maintains your original structure."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"File Comparison Results\n")
        f.write(f"Mode: {data['mode']}\n")
        f.write(f"Time: {datetime.now()}\n\n")
        
        # Group 1
        f.write(f"Files only in first group:\n")
        if 'dirs1' in data and len(data['dirs1']) > 1:
            f.write("Directories:\n")
            for dir_path in data['dirs1']:
                f.write(f"  - {dir_path}\n")
        else:
            f.write(f"Directory: {data['path1']}\n")
        
        f.write(f"({len(data['unique1'])} files):\n")
        for file in sorted(data['unique1']):
            f.write(f"{file}\n")
        
        # Group 2
        f.write(f"\nFiles only in second group:\n")
        if 'dirs2' in data and len(data['dirs2']) > 1:
            f.write("Directories:\n")
            for dir_path in data['dirs2']:
                f.write(f"  - {dir_path}\n")
        else:
            f.write(f"Directory: {data['path2']}\n")
        
        f.write(f"({len(data['unique2'])} files):\n")
        for file in sorted(data['unique2']):
            f.write(f"{file}\n")
        
        # Frame mismatches if in advanced mode
        if 'frame_mismatches' in data and data['frame_mismatches']:
            f.write(f"\n{'='*80}\n")
            f.write(f"FRAME COUNT MISMATCHES ({len(data['frame_mismatches'])} files)\n")
            f.write(f"{'='*80}\n\n")
            for mismatch in sorted(data['frame_mismatches'], key=lambda x: x['difference'], reverse=True):
                f.write(f"Basename: {mismatch['basename']}\n")
                f.write(f"  Group 1: {mismatch['file1']} ({mismatch['frames1']} frames)\n")
                f.write(f"  Group 2: {mismatch['file2']} ({mismatch['frames2']} frames)\n")
                f.write(f"  Difference: {mismatch['difference']} frames\n")
                f.write(f"  Path 1: {mismatch['path1']}\n")
                f.write(f"  Path 2: {mismatch['path2']}\n\n")


def export_to_csv(data, output_file):
    """Export results to CSV format - maintains your original structure."""
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['Mode', data['mode']])
        writer.writerow(['Time', datetime.now()])
        writer.writerow([])
        
        # Write directory information
        writer.writerow(['Group 1 Directories'] + data.get('dirs1', [data['path1']]))
        writer.writerow(['Group 2 Directories'] + data.get('dirs2', [data['path2']]))
        writer.writerow([])
        
        writer.writerow(['Location', 'Path'])
        
        for file in sorted(data['unique1']):
            writer.writerow(['Group1', file])
        for file in sorted(data['unique2']):
            writer.writerow(['Group2', file])
        
        # Frame mismatches if in advanced mode
        if 'frame_mismatches' in data and data['frame_mismatches']:
            writer.writerow([])
            writer.writerow(['FRAME COUNT MISMATCHES'])
            writer.writerow(['Basename', 'File (Group 1)', 'Frames (Group 1)', 
                           'File (Group 2)', 'Frames (Group 2)', 'Difference', 
                           'Path 1', 'Path 2'])
            for mismatch in sorted(data['frame_mismatches'], key=lambda x: x['difference'], reverse=True):
                writer.writerow([
                    mismatch['basename'],
                    mismatch['file1'],
                    mismatch['frames1'],
                    mismatch['file2'],
                    mismatch['frames2'],
                    mismatch['difference'],
                    mismatch['path1'],
                    mismatch['path2']
                ])


def export_to_html(data, output_file):
    """Export results to HTML format - maintains your exact original HTML structure and styling."""
    mode_description = {
        'normal': "Normal (comparing all files by basename.extension)",
        'proxy': "Proxy (comparing video files by basename only)",
        'proxy_advanced': "Proxy Advanced (comparing video files by basename and frame count)"
    }.get(data['mode'], data['mode'])
    
    # Format directory lists
    def format_dirs_html(dirs):
        if len(dirs) == 1:
            return f'<div class="path-text">{html.escape(dirs[0])}</div>'
        else:
            dir_items = ''.join(f'<div class="path-text">{html.escape(d)}</div>' for d in dirs)
            return f'{dir_items}'
    
    dirs1_html = format_dirs_html(data.get('dirs1', [data['path1']]))
    dirs2_html = format_dirs_html(data.get('dirs2', [data['path2']]))
    
    # Frame mismatches section - only show in proxy_advanced mode
    mismatch_html = ""
    if data['mode'] == 'proxy_advanced':
        if data.get('frame_mismatches'):
            # Mismatches found
            # Helper definitions for formatting and sorting
            def fmt_num(n):
                if n is None: return "N/A"
                if isinstance(n, (int, float)): return f"{n:,}"
                return str(n)

            def get_diff_value(m):
                d = m['difference']
                if isinstance(d, (int, float)): return d
                return -1 # Push non-numeric differences to the end (or top since reverse=True)

            mismatch_rows = ''.join(f'''
            <tr class="mismatch">
                <td>{html.escape(mismatch['basename'])}</td>
                <td>{html.escape(mismatch['file1'])}</td>
                <td>{fmt_num(mismatch['frames1'])}</td>
                <td>{html.escape(mismatch['file2'])}</td>
                <td>{fmt_num(mismatch['frames2'])}</td>
                <td><strong>{fmt_num(mismatch['difference'])}</strong></td>
            </tr>
        ''' for mismatch in sorted(data['frame_mismatches'], key=get_diff_value, reverse=True))
            
            mismatch_html = f'''
        <div class="section">
            <div class="warning-box">
                <h3>⚠️ Frame Count Mismatches ({len(data['frame_mismatches'])} files)</h3>
                <p>These files exist in both groups but have different frame counts, indicating incomplete or corrupted proxy files:</p>
            </div>
            <table>
                <tr>
                    <th>Basename</th>
                    <th>File (Group 1)</th>
                    <th>Frames (Group 1)</th>
                    <th>File (Group 2)</th>
                    <th>Frames (Group 2)</th>
                    <th>Difference</th>
                </tr>
                {mismatch_rows}
            </table>
        </div>
        '''
        else:
            # No mismatches found
            mismatch_html = f'''
        <div class="section">
            <div class="warning-box" style="background-color: #d4edda; border-color: #c3e6cb;">
                <h3 style="color: #155724;">✅ Frame Count Mismatches (0 files)</h3>
                <p><strong>ALL</strong> files have matching frame counts</p>
            </div>
        </div>
        '''
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Comparison Results</title>
    <style>{_get_html_style()}</style>
</head>
<body>
    <h2>File Comparison Results</h2>
    <div class="mode-info">
        <strong>Mode:</strong> {mode_description}<br>
        <strong>Time:</strong> {datetime.now()}
    </div>
    
    {mismatch_html}
    
    <div class="section">
        <div class="path-header">
            <h3>Files only in first group: ({len(data['unique1'])} files)</h3>
            {dirs1_html}
        </div>
        <table>
            <tr><th>File Path</th></tr>
            {''.join(f'<tr class="path1"><td>{html.escape(f)}</td></tr>' for f in sorted(data['unique1']))}
        </table>
    </div>
    
    <div class="section">
        <div class="path-header">
            <h3>Files only in second group: ({len(data['unique2'])} files)</h3>
            {dirs2_html}
        </div>
        <table>
            <tr><th>File Path</th></tr>
            {''.join(f'<tr class="path2"><td>{html.escape(f)}</td></tr>' for f in sorted(data['unique2']))}
        </table>
    </div>
</body>
</html>"""
    
    # Write with UTF-8 BOM for better compatibility (same as original)
    with open(output_file, 'wb') as f:
        # Write UTF-8 BOM
        f.write(b'\xef\xbb\xbf')
        # Write content as UTF-8
        f.write(html_content.encode('utf-8'))
with open('app/templates/dashboard.html', 'r') as f:
    content = f.read()

target = """<!-- Main Titles -->
<div class="mb-8">
    <div class="text-sm font-bold uppercase mb-2" style="color: #555;">National Verification Registry • Legal Inspection
        Terminal</div>
    <h1
        style="font-size: clamp(1.75rem, 6vw, 2.5rem); font-weight: 900; text-transform: uppercase; line-height: 1.1; margin: 0.5rem 0;">
        Legal Metrology Verification</h1>
    <div class="text-sm font-bold uppercase mt-2">Non-Automatic Weighing Instrument (NAWI) • Class I / II / III / IIII
        Field Conformity</div>
</div>"""

replacement = """<!-- Main Titles -->
<div class="mb-8">
    <div class="text-sm font-bold uppercase mb-2" style="color: #555;">National Verification Registry • Legal Inspection
        Terminal</div>
    <h1
        style="font-size: clamp(1.75rem, 6vw, 2.5rem); font-weight: 900; text-transform: uppercase; line-height: 1.1; margin: 0.5rem 0;">
        Legal Metrology Verification</h1>
    <div class="text-sm font-bold uppercase mt-2">Non-Automatic Weighing Instrument (NAWI) • Class I / II / III / IIII
        Field Conformity</div>
</div>

{% if stats %}
<!-- History Stats Summary Widget -->
<div class="card mb-8" style="padding: 1.5rem;">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
        <div>
            <h3 class="section-header" style="margin-bottom: 0.5rem; font-size: 1.2rem;">Verification History Summary</h3>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.9rem;">
                Total: <strong>{{ stats.total }}</strong> | 
                <span style="color: #1a7f37;">PASS: <strong>{{ stats.pass }}</strong></span> | 
                <span style="color: #d1242f;">FAIL: <strong>{{ stats.fail }}</strong></span>
            </div>
        </div>
        <a href="{{ url_for('inspector.history') }}" class="btn btn-dark" style="font-size: 0.85rem;">View All Reports</a>
    </div>
</div>
{% endif %}"""

content = content.replace(target, replacement)

with open('app/templates/dashboard.html', 'w') as f:
    f.write(content)

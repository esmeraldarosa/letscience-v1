
import os

file_path = 'frontend/index.html'

with open(file_path, 'r') as f:
    lines = f.readlines()

new_content = """                                <div className="min-w-[700px]">
                                     {/* X-Axis Scale */}
                                     <div className="flex text-xs font-bold text-slate-400 pl-32 mb-2 border-b border-slate-100 pb-2 relative h-6">
                                        {[2015, 2020, 2025, 2030, 2035].map(year => {
                                            const left = ((year - 2015) / (2035 - 2015)) * 100;
                                            return (
                                                <span key={year} className="absolute transform -translate-x-1/2" style={{ left: `${left}%` }}>
                                                    {year}
                                                </span>
                                            );
                                        })}
                                     </div>

                                     <div className="space-y-6">
                                        {selectedIds.map(id => {
                                            const prod = products.find(p => p.id === id);
                                            const events = comparisonData.timeline_events.filter(e => e.product === prod.name);
                                            const cliff = comparisonData.patent_cliffs.find(c => c.product === prod.name);
                                            
                                            return (
                                                <div key={id} className="relative group">
                                                    <div className="flex items-center mb-2">
                                                        <span className="w-32 font-bold text-slate-700 text-sm truncate pr-4">{prod.name}</span>
                                                        <div className="flex-1 h-32 bg-slate-50 rounded-lg relative border border-slate-100">
                                                            
                                                            {/* Grid Lines */}
                                                            {[2020, 2025, 2030].map(year => (
                                                                <div key={year} className="absolute top-0 bottom-0 border-l border-slate-200 border-dashed"
                                                                     style={{ left: `${((year - 2015) / (2035 - 2015)) * 100}%` }}></div>
                                                            ))}

                                                            {/* Patent Cliff Line */}
                                                            {cliff && (
                                                                <div className="absolute top-0 bottom-0 w-0.5 bg-red-400 border-l-2 border-red-500 border-dotted z-10 flex flex-col items-center"
                                                                     style={{ left: `${((cliff.year - 2015) / (2035 - 2015)) * 100}%` }}>
                                                                    <div className="bg-red-500 text-white text-[10px] px-1 py-0.5 rounded mt-1 shadow-sm whitespace-nowrap">
                                                                        LoE {cliff.year}
                                                                    </div>
                                                                </div>
                                                            )}

                                                            {/* Gantt Bars */}
                                                            {events.map((ev, i) => {
                                                                 if (ev.type !== 'Trial Start') return null;
                                                                 
                                                                 const startYear = new Date(ev.date).getFullYear();
                                                                 const endYear = ev.end_date ? new Date(ev.end_date).getFullYear() : startYear + 2;
                                                                 
                                                                 const startPos = Math.max(0, ((startYear - 2015) / (2035 - 2015)) * 100);
                                                                 const endPos = Math.min(100, ((endYear - 2015) / (2035 - 2015)) * 100);
                                                                 const width = endPos - startPos;
                                                                 
                                                                 const color = ev.phase.includes('3') ? 'bg-purple-500' : 
                                                                               ev.phase.includes('2') ? 'bg-blue-400' : 'bg-slate-400';

                                                                 return (
                                                                     <div 
                                                                         key={i}
                                                                         className={`absolute h-4 rounded shadow-sm opacity-80 hover:opacity-100 transition-all cursor-help ${color}`}
                                                                         style={{ 
                                                                             left: `${startPos}%`, 
                                                                             width: `${width}%`,
                                                                             top: `${(i % 3) * 25 + 10}px` 
                                                                         }}
                                                                         title={`${ev.title} (${ev.phase}) \nStart: ${ev.date}`}
                                                                     ></div>
                                                                 );
                                                            })}
                                                        </div>
                                                    </div>
                                                </div>
                                            );
                                        })}
                                     </div>
                                </div>
"""

start_marker = '<div className="space-y-4 min-w-[600px]">'
# The end marker needs to be robust. 
# Based on the file content, the inner content block (lines 2920-2960) ends with </div> on line 2959, 
# and the outer wrapper ends with </div> on line 2960.
# The next section is {/* 2. PK Matrix */} at line 2962.
end_marker = '{/* 2. PK Matrix */}'

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if start_marker in line:
        start_idx = i
    if end_marker in line:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    # Logic from before:
    # end_idx is 2962 (PK Matrix comment)
    # end_idx - 1 is empty line
    # end_idx - 2 is </div> (Outer wrapper close)
    # end_idx - 3 is </div> (Inner content close)
    
    # We want to replace everything from start_idx (inclusive) up to end_idx - 2 (exclusive).
    # So we want to KEEP the outer wrapper closing div.
    
    # Let's verify end_idx - 2 contains '</div>'.
    if '</div>' in lines[end_idx - 2]:
        # Perform replacement
        # lines[:start_idx] keeps everything before <div className="space-y-4...
        # [new_content] adds the new inner block (lines 2920-ish equivalents)
        # lines[end_idx-2:] keeps the outer closing div and everything after.
        
        final_lines = lines[:start_idx] + [new_content + "\n"] + lines[end_idx-2:]
        
        with open(file_path, 'w') as f:
            f.writelines(final_lines)
        print("Successfully patched index.html")
    else:
        print(f"Error: expected </div> at line {end_idx - 2}, found: {lines[end_idx - 2]}")
else:
    print(f"Markers not found. Start: {start_idx}, End: {end_idx}")

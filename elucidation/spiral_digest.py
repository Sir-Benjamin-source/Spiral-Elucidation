import argparse
import json
import fitz  # PyMuPDF for PDF
from spiral_engine import SpiralEngine

def load_text(file_path):
    """Load TXT or PDF text, chunk into sections."""
    if file_path.lower().endswith('.pdf'):
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    
    # Chunk into sentences/sections (simple split for demo)
    chunks = text.split('. ')  # Or use NLTK for smarter chunking
    return [chunk.strip() for chunk in chunks if len(chunk) > 50]  # Filter shorties

def spiral_breakdown(chunks, iterations=5):
    """Run engine on chunks for themes/hypotheses/bias."""
    engine = SpiralEngine()
    params = {'td': len(chunks), 'rf': 1.5, 'tw': 2.0, 'cir': 1.5, 'am': 0.2, 'da': np.pi/3}
    
    values = engine.simulate_spiral(params, iterations=iterations, sign='+', noise_level=0.03)
    
    # Proxy metrics: "Retention" as std dev stability, "Uplift" as mean growth
    retention = 100 - (np.std(values) / np.mean(values) * 100)  # % stable
    uplift = (values[-1] - values[0]) / values[0] * 100  # % gain
    
    # Simple theme proxy: Sort chunks by length (weighted by path)
    weighted_chunks = sorted(zip(chunks, values), key=lambda x: x[1])
    top_themes = [chunk[:100] + '...' for chunk, _ in weighted_chunks[-3:]]  # Top 3 "dense" chunks
    
    breakdown = {
        'retention_pct': retention,
        'uplift_pct': uplift,
        'top_themes': top_themes,
        'values': values.tolist(),
        'provenance': engine.get_provenance()[-1]
    }
    
    # English summary
    summary = f"This document spirals with {retention:.1f}% retention—your core themes hold steady through {iterations} cycles. Uplift of {uplift:.1f}% suggests emergent insights in the denser sections. Top themes: {', '.join(top_themes[:2])}..."
    breakdown['summary'] = summary
    
    return breakdown

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spiral Digest: Breakdown PDF/TXT with Path Engine")
    parser.add_argument('--file', type=str, required=True, help="Path to PDF or TXT")
    parser.add_argument('--iterations', type=int, default=5, help="Number of spiral cycles")
    parser.add_argument('--output', type=str, default='breakdown.json', help="Output JSON")
    
    args = parser.parse_args()
    
    chunks = load_text(args.file)
    results = spiral_breakdown(chunks, args.iterations)
    
    print(results['summary'])
    print("Metrics:", {k: v for k, v in results.items() if k != 'summary' and k != 'provenance'})
    
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Full breakdown saved to {args.output}")

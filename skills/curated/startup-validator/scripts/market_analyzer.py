#!/usr/bin/env python3
"""
Market Analysis Data Processor
Processes and visualizes market data for startup validation
"""

import json
import sys
from typing import Dict, List, Any


def calculate_market_metrics(market_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate key market metrics from raw data
    
    Args:
        market_data: Dictionary with keys like 'tam', 'sam', 'som', 'growth_rate', etc.
    
    Returns:
        Dictionary with calculated metrics
    """
    metrics = {}
    
    # Market size calculations
    if 'tam' in market_data and 'sam' in market_data:
        metrics['sam_percentage'] = (market_data['sam'] / market_data['tam']) * 100
    
    if 'sam' in market_data and 'som' in market_data:
        metrics['som_percentage'] = (market_data['som'] / market_data['sam']) * 100
    
    # Growth projections
    if 'current_market_size' in market_data and 'growth_rate' in market_data and 'years' in market_data:
        current = market_data['current_market_size']
        rate = market_data['growth_rate'] / 100
        years = market_data['years']
        metrics['projected_market_size'] = current * ((1 + rate) ** years)
    
    # Market attractiveness score (0-100)
    score = 0
    if 'growth_rate' in market_data:
        # High growth = high score (capped at 30 points)
        score += min(market_data['growth_rate'] * 2, 30)
    
    if 'tam' in market_data:
        # Larger markets score higher (logarithmic scale)
        if market_data['tam'] > 10_000_000_000:  # >$10B
            score += 30
        elif market_data['tam'] > 1_000_000_000:  # >$1B
            score += 20
        else:
            score += 10
    
    if 'competition_level' in market_data:
        # Lower competition = higher score
        comp_score = {'low': 20, 'medium': 10, 'high': 5}
        score += comp_score.get(market_data['competition_level'], 10)
    
    if 'market_maturity' in market_data:
        # Emerging markets score higher than mature
        maturity_score = {'emerging': 20, 'growing': 15, 'mature': 5}
        score += maturity_score.get(market_data['market_maturity'], 10)
    
    metrics['market_attractiveness_score'] = min(score, 100)
    
    return metrics


def calculate_unit_economics(business_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate unit economics metrics
    
    Args:
        business_data: Dictionary with keys like 'cac', 'ltv', 'monthly_revenue', etc.
    
    Returns:
        Dictionary with unit economics metrics
    """
    metrics = {}
    
    if 'ltv' in business_data and 'cac' in business_data:
        metrics['ltv_cac_ratio'] = business_data['ltv'] / business_data['cac']
        metrics['ltv_cac_health'] = 'Excellent' if metrics['ltv_cac_ratio'] >= 3 else \
                                     'Good' if metrics['ltv_cac_ratio'] >= 2 else \
                                     'Acceptable' if metrics['ltv_cac_ratio'] >= 1 else 'Unhealthy'
    
    if 'cac' in business_data and 'monthly_revenue' in business_data:
        metrics['payback_period_months'] = business_data['cac'] / business_data['monthly_revenue']
        metrics['payback_health'] = 'Excellent' if metrics['payback_period_months'] <= 6 else \
                                     'Good' if metrics['payback_period_months'] <= 12 else \
                                     'Acceptable' if metrics['payback_period_months'] <= 18 else 'Concerning'
    
    if 'revenue' in business_data and 'cost' in business_data:
        metrics['gross_margin'] = ((business_data['revenue'] - business_data['cost']) / business_data['revenue']) * 100
        metrics['margin_health'] = 'Excellent' if metrics['gross_margin'] >= 70 else \
                                    'Good' if metrics['gross_margin'] >= 50 else \
                                    'Acceptable' if metrics['gross_margin'] >= 30 else 'Low'
    
    return metrics


def assess_viability(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Assess overall startup viability based on multiple factors
    
    Args:
        analysis_data: Comprehensive analysis data including market, competition, etc.
    
    Returns:
        Viability assessment with score and recommendation
    """
    score = 0
    max_score = 0
    factors = []
    
    # Market opportunity (30 points)
    if 'market' in analysis_data:
        max_score += 30
        market = analysis_data['market']
        
        if market.get('size', 0) > 1_000_000_000:  # >$1B
            score += 15
            factors.append("✓ Large market opportunity")
        else:
            factors.append("⚠ Limited market size")
        
        if market.get('growth_rate', 0) > 10:  # >10% CAGR
            score += 15
            factors.append("✓ High growth market")
        else:
            factors.append("⚠ Slow growth market")
    
    # Competition (20 points)
    if 'competition' in analysis_data:
        max_score += 20
        comp = analysis_data['competition']
        
        if comp.get('level') == 'low':
            score += 20
            factors.append("✓ Low competition")
        elif comp.get('level') == 'medium':
            score += 10
            factors.append("⚠ Moderate competition")
        else:
            factors.append("✗ High competition")
    
    # Problem-solution fit (25 points)
    if 'problem_validation' in analysis_data:
        max_score += 25
        prob = analysis_data['problem_validation']
        
        if prob.get('frequency') in ['daily', 'weekly']:
            score += 10
            factors.append("✓ Frequent problem occurrence")
        
        if prob.get('intensity') in ['high', 'critical']:
            score += 10
            factors.append("✓ Painful problem")
        
        if prob.get('willingness_to_pay'):
            score += 5
            factors.append("✓ Customers willing to pay")
    
    # Business model (25 points)
    if 'unit_economics' in analysis_data:
        max_score += 25
        ue = analysis_data['unit_economics']
        
        if ue.get('ltv_cac_ratio', 0) >= 3:
            score += 15
            factors.append("✓ Healthy LTV:CAC ratio")
        elif ue.get('ltv_cac_ratio', 0) >= 1:
            score += 7
            factors.append("⚠ Acceptable LTV:CAC ratio")
        
        if ue.get('payback_period_months', 999) <= 12:
            score += 10
            factors.append("✓ Fast payback period")
    
    # Calculate percentage
    viability_score = (score / max_score * 100) if max_score > 0 else 0
    
    # Determine recommendation
    if viability_score >= 70:
        recommendation = "STRONG GO"
        confidence = "High"
    elif viability_score >= 50:
        recommendation = "PROCEED WITH VALIDATION"
        confidence = "Medium"
    elif viability_score >= 30:
        recommendation = "PIVOT RECOMMENDED"
        confidence = "Low"
    else:
        recommendation = "NOT VIABLE"
        confidence = "High"
    
    return {
        'viability_score': round(viability_score, 1),
        'recommendation': recommendation,
        'confidence': confidence,
        'factors': factors,
        'raw_score': f"{score}/{max_score}"
    }


def generate_markdown_report(analysis: Dict[str, Any]) -> str:
    """
    Generate a markdown-formatted analysis report
    
    Args:
        analysis: Complete analysis data
    
    Returns:
        Markdown formatted report string
    """
    report = []
    report.append("# Startup Validation Analysis Report\n")
    
    if 'startup_name' in analysis:
        report.append(f"## {analysis['startup_name']}\n")
    
    if 'viability' in analysis:
        v = analysis['viability']
        report.append("## Overall Assessment\n")
        report.append(f"**Viability Score:** {v['viability_score']}/100\n")
        report.append(f"**Recommendation:** {v['recommendation']}\n")
        report.append(f"**Confidence:** {v['confidence']}\n\n")
        
        report.append("### Key Factors:\n")
        for factor in v.get('factors', []):
            report.append(f"- {factor}\n")
        report.append("\n")
    
    if 'market_metrics' in analysis:
        mm = analysis['market_metrics']
        report.append("## Market Metrics\n")
        for key, value in mm.items():
            key_formatted = key.replace('_', ' ').title()
            if isinstance(value, float):
                report.append(f"- **{key_formatted}:** {value:.2f}\n")
            else:
                report.append(f"- **{key_formatted}:** {value}\n")
        report.append("\n")
    
    if 'unit_economics' in analysis:
        ue = analysis['unit_economics']
        report.append("## Unit Economics\n")
        for key, value in ue.items():
            key_formatted = key.replace('_', ' ').title()
            if isinstance(value, float):
                report.append(f"- **{key_formatted}:** {value:.2f}\n")
            else:
                report.append(f"- **{key_formatted}:** {value}\n")
        report.append("\n")
    
    return ''.join(report)


def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python market_analyzer.py <analysis_data.json>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    results = {}
    
    if 'market_data' in data:
        results['market_metrics'] = calculate_market_metrics(data['market_data'])
    
    if 'business_data' in data:
        results['unit_economics'] = calculate_unit_economics(data['business_data'])
    
    results['viability'] = assess_viability(data)
    
    # Generate report
    report = generate_markdown_report({**data, **results})
    print(report)
    
    # Save results
    output_file = sys.argv[1].replace('.json', '_results.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: {output_file}")


if __name__ == "__main__":
    main()

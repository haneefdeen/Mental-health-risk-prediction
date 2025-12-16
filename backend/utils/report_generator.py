"""
MindScope AI - PDF Report Generator
Generates comprehensive PDF reports for mental health analysis
"""

import os
from datetime import datetime
from typing import Dict, List, Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import matplotlib.pyplot as plt
import io
import base64

class ReportGenerator:
    """Generate PDF reports for mental health analysis"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles for the report"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2563eb')
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.HexColor('#1e40af')
        ))
        
        # Body style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            alignment=TA_LEFT
        ))
        
        # Risk style
        self.styles.add(ParagraphStyle(
            name='RiskHigh',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#dc2626'),
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='RiskMedium',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#d97706'),
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='RiskLow',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#059669'),
            alignment=TA_CENTER
        ))
    
    def generate_report(self, user_data: Dict, analysis_data: Dict, output_path: str = None) -> str:
        """Generate comprehensive PDF report"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"reports/mindscope_report_{timestamp}.pdf"
        
        # Create reports directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Add title page
        story.extend(self._create_title_page(user_data))
        story.append(PageBreak())
        
        # Add executive summary
        story.extend(self._create_executive_summary(analysis_data))
        story.append(PageBreak())
        
        # Add detailed analysis
        story.extend(self._create_detailed_analysis(analysis_data))
        story.append(PageBreak())
        
        # Add recommendations
        story.extend(self._create_recommendations(analysis_data))
        story.append(PageBreak())
        
        # Add behavioral insights
        story.extend(self._create_behavioral_insights(analysis_data))
        story.append(PageBreak())
        
        # Add privacy and ethics
        story.extend(self._create_privacy_section())
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    def _create_title_page(self, user_data: Dict) -> List:
        """Create title page"""
        elements = []
        
        # Title
        elements.append(Paragraph("MindScope AI", self.styles['CustomTitle']))
        elements.append(Spacer(1, 20))
        
        # Subtitle
        elements.append(Paragraph("Mental Health Analysis Report", self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 40))
        
        # User information
        user_info = [
            ["Patient ID:", user_data.get('username', 'N/A')],
            ["Full Name:", user_data.get('full_name', 'N/A')],
            ["Email:", user_data.get('email', 'N/A')],
            ["Report Date:", datetime.now().strftime("%B %d, %Y")],
            ["Report Time:", datetime.now().strftime("%H:%M:%S")]
        ]
        
        user_table = Table(user_info, colWidths=[2*inch, 3*inch])
        user_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ]))
        
        elements.append(user_table)
        elements.append(Spacer(1, 40))
        
        # Disclaimer
        disclaimer = """
        <b>Important Notice:</b><br/>
        This report is generated by MindScope AI for informational purposes only. 
        It is not a substitute for professional medical advice, diagnosis, or treatment. 
        Always seek the advice of qualified health providers with questions about your mental health.
        """
        elements.append(Paragraph(disclaimer, self.styles['CustomBody']))
        
        return elements
    
    def _create_executive_summary(self, analysis_data: Dict) -> List:
        """Create executive summary section"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 20))
        
        # Overall assessment
        stress_level = analysis_data.get('stress_level', 'low')
        confidence = analysis_data.get('confidence', 0.5)
        
        summary_text = f"""
        Based on the comprehensive analysis of your text, image, and behavioral patterns, 
        your current stress level is assessed as <b>{stress_level.upper()}</b> with a confidence 
        of {confidence:.1%}.
        """
        elements.append(Paragraph(summary_text, self.styles['CustomBody']))
        elements.append(Spacer(1, 20))
        
        # Key findings
        elements.append(Paragraph("Key Findings:", self.styles['CustomSubtitle']))
        
        findings = [
            f"• Stress Level: {stress_level.upper()}",
            f"• Analysis Confidence: {confidence:.1%}",
            f"• Risk Score: {analysis_data.get('risk_score', 0.5):.1%}",
            f"• Behavioral Score: {analysis_data.get('behavioral_score', 0.5):.1%}"
        ]
        
        for finding in findings:
            elements.append(Paragraph(finding, self.styles['CustomBody']))
        
        return elements
    
    def _create_detailed_analysis(self, analysis_data: Dict) -> List:
        """Create detailed analysis section"""
        elements = []
        
        elements.append(Paragraph("Detailed Analysis", self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 20))
        
        # Modality scores
        modality_scores = analysis_data.get('modality_scores', {})
        
        analysis_table_data = [
            ["Analysis Modality", "Stress Level", "Confidence", "Weight"],
            ["Text Analysis", modality_scores.get('text', 'low').upper(), 
             f"{analysis_data.get('text_confidence', 0.5):.1%}", 
             f"{analysis_data.get('text_weight', 0.33):.1%}"],
            ["Image Analysis", modality_scores.get('image', 'low').upper(),
             f"{analysis_data.get('image_confidence', 0.5):.1%}",
             f"{analysis_data.get('image_weight', 0.33):.1%}"],
            ["Behavioral Analysis", modality_scores.get('behavioral', 'low').upper(),
             f"{analysis_data.get('behavioral_confidence', 0.5):.1%}",
             f"{analysis_data.get('behavioral_weight', 0.34):.1%}"]
        ]
        
        analysis_table = Table(analysis_table_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch])
        analysis_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(analysis_table)
        elements.append(Spacer(1, 20))
        
        # Fusion explanation
        fusion_text = """
        <b>Multimodal Fusion:</b><br/>
        The final assessment combines insights from text emotion analysis, facial emotion recognition, 
        and behavioral pattern analysis using advanced machine learning techniques. Each modality 
        contributes to the overall assessment with different weights based on reliability and relevance.
        """
        elements.append(Paragraph(fusion_text, self.styles['CustomBody']))
        
        return elements
    
    def _create_recommendations(self, analysis_data: Dict) -> List:
        """Create recommendations section"""
        elements = []
        
        elements.append(Paragraph("AI-Powered Recommendations", self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 20))
        
        recommendations = analysis_data.get('recommendations', [])
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                elements.append(Paragraph(f"{i}. {rec}", self.styles['CustomBody']))
                elements.append(Spacer(1, 10))
        else:
            elements.append(Paragraph("No specific recommendations available at this time.", self.styles['CustomBody']))
        
        elements.append(Spacer(1, 20))
        
        # General wellness tips
        elements.append(Paragraph("General Wellness Tips:", self.styles['CustomSubtitle']))
        
        wellness_tips = [
            "• Practice regular mindfulness or meditation",
            "• Maintain a consistent sleep schedule",
            "• Engage in regular physical exercise",
            "• Stay connected with friends and family",
            "• Consider professional mental health support when needed"
        ]
        
        for tip in wellness_tips:
            elements.append(Paragraph(tip, self.styles['CustomBody']))
        
        return elements
    
    def _create_behavioral_insights(self, analysis_data: Dict) -> List:
        """Create behavioral insights section"""
        elements = []
        
        elements.append(Paragraph("Behavioral Insights", self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 20))
        
        # Behavioral analysis
        behavioral_data = analysis_data.get('behavioral_analysis', {})
        
        if behavioral_data:
            elements.append(Paragraph("Recent Behavioral Patterns:", self.styles['CustomSubtitle']))
            
            # Emoji analysis
            emoji_analysis = behavioral_data.get('emoji_analysis', {})
            if emoji_analysis:
                emoji_text = f"""
                <b>Emoji Usage Analysis:</b><br/>
                • Total Emojis: {emoji_analysis.get('total_emojis', 0)}<br/>
                • Positive Emojis: {emoji_analysis.get('positive_emojis', 0)}<br/>
                • Negative Emojis: {emoji_analysis.get('negative_emojis', 0)}<br/>
                • Stress Emojis: {emoji_analysis.get('stress_emojis', 0)}<br/>
                • Emoji Diversity: {emoji_analysis.get('emoji_diversity', 0):.2f}
                """
                elements.append(Paragraph(emoji_text, self.styles['CustomBody']))
                elements.append(Spacer(1, 15))
            
            # Frequency analysis
            freq_analysis = behavioral_data.get('frequency_analysis', {})
            if freq_analysis:
                freq_text = f"""
                <b>Posting Frequency Analysis:</b><br/>
                • Posts per Day: {freq_analysis.get('posts_per_day', 0):.1f}<br/>
                • Activity Level: {freq_analysis.get('activity_level', 'low').upper()}<br/>
                • Posting Consistency: {freq_analysis.get('posting_consistency', 0):.1%}<br/>
                • Trend: {freq_analysis.get('trend', 'stable').upper()}
                """
                elements.append(Paragraph(freq_text, self.styles['CustomBody']))
        
        return elements
    
    def _create_privacy_section(self) -> List:
        """Create privacy and ethics section"""
        elements = []
        
        elements.append(Paragraph("Privacy & Ethics", self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 20))
        
        privacy_text = """
        <b>Data Privacy:</b><br/>
        • All analysis data is processed locally and securely<br/>
        • Personal information is anonymized in aggregated reports<br/>
        • You have the right to request data deletion at any time<br/>
        • No data is shared with third parties without explicit consent<br/><br/>
        
        <b>Ethical AI:</b><br/>
        • This system follows ethical AI principles<br/>
        • Analysis is transparent and explainable<br/>
        • Recommendations are evidence-based<br/>
        • Human oversight is maintained in all decisions<br/><br/>
        
        <b>Contact Information:</b><br/>
        For questions about this report or data privacy, please contact:<br/>
        Email: privacy@mindscope.ai<br/>
        Phone: +1 (555) 123-4567
        """
        
        elements.append(Paragraph(privacy_text, self.styles['CustomBody']))
        
        return elements

# Global instance
report_generator = ReportGenerator()
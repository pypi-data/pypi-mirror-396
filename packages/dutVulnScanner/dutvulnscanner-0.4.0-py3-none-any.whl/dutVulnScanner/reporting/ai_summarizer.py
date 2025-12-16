"""AI-powered vulnerability scan summarization using Google Gemini."""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class AIAnalysisError(Exception):
    """Exception raised when AI analysis fails."""

    pass


class AISummarizer:
    """
    Generate intelligent summaries of vulnerability scans using Google Gemini AI.

    This class handles:
    - Loading API credentials from environment
    - Formatting scan results into prompts
    - Calling Gemini API for analysis
    - Parsing and structuring AI responses
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize AI summarizer.

        Args:
            api_key: Gemini API key. If not provided, loads from GEMINI_API_KEY env var
            model: Gemini model to use. Defaults to gemini-2.5-flash

        Raises:
            ValueError: If API key is not provided and not found in environment
        """
        # Load environment variables from .env file
        from dotenv import load_dotenv

        load_dotenv()

        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API key not found. Please set GEMINI_API_KEY in your .env file. "
                "Get your key from: https://makersuite.google.com/app/apikey"
            )

        self.model_name = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.model = None

    def _initialize_model(self):
        """Initialize Gemini model (lazy loading)."""
        if self.model is not None:
            return

        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"Initialized Gemini model: {self.model_name}")
        except ImportError:
            raise ImportError(
                "google-generativeai package not found. " "Install it with: pip install google-generativeai"
            )
        except Exception as e:
            raise AIAnalysisError(f"Failed to initialize Gemini model: {str(e)}")

    def generate_summary(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI-powered summary of scan results.

        Args:
            scan_results: Dictionary containing scan results (from scan_manifest.json)

        Returns:
            Dictionary containing:
                - executive_summary: High-level overview
                - risk_assessment: Security posture analysis
                - prioritized_recommendations: Ordered list of remediation steps
                - technical_insights: Technology-specific guidance

        Raises:
            AIAnalysisError: If AI analysis fails
        """
        self._initialize_model()

        try:
            # Build prompt with scan data
            prompt = self._build_prompt(scan_results)

            logger.info("Sending scan results to Gemini AI for analysis...")

            # Call Gemini API
            response = self.model.generate_content(prompt)

            # Parse response
            summary = self._parse_response(response.text, scan_results)

            logger.info("AI analysis completed successfully")
            return summary

        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            raise AIAnalysisError(f"Failed to generate AI summary: {str(e)}")

    def _build_prompt(self, scan_results: Dict[str, Any]) -> str:
        """
        Build structured prompt for Gemini AI.

        Args:
            scan_results: Scan results dictionary

        Returns:
            Formatted prompt string
        """
        target = scan_results.get("target", "Unknown")
        profile = scan_results.get("profile", "Unknown")
        vulnerabilities = scan_results.get("vulnerabilities", [])
        stats = scan_results.get("statistics", {})
        tools_used = scan_results.get("tools_used", [])

        # Format vulnerabilities for the prompt
        vuln_summary = []
        for vuln in vulnerabilities[:20]:  # Limit to top 20 to avoid token limits
            vuln_summary.append(
                {
                    "severity": vuln.get("severity", "unknown"),
                    "title": vuln.get("title", ""),
                    "description": vuln.get("description", ""),
                    "technology": vuln.get("evidence", {}).get("technology", ""),
                    "version": vuln.get("evidence", {}).get("version", ""),
                }
            )

        prompt = f"""Bạn là chuyên gia an ninh mạng đang phân tích kết quả quét lỗ hổng bảo mật. Hãy cung cấp báo cáo phân tích bảo mật toàn diện BẰNG TIẾNG VIỆT.

**Thông tin quét:**
- Mục tiêu: {target}
- Hồ sơ quét: {profile}
- Công cụ sử dụng: {', '.join(tools_used)}
- Tổng số lỗ hổng phát hiện: {stats.get('total', 0)}
- Phân loại mức độ nghiêm trọng: {json.dumps(stats.get('by_severity', {}), indent=2)}

**Lỗ hổng phát hiện:**
{json.dumps(vuln_summary, indent=2)}

**Vui lòng cung cấp phân tích có cấu trúc với các phần sau (BẰNG TIẾNG VIỆT):**

1. **Tóm tắt tổng quan** (2-3 câu)
   - Đánh giá tổng thể về tình trạng bảo mật
   - Các vấn đề chính được xác định

2. **Đánh giá rủi ro** (1 đoạn văn)
   - Giải thích ý nghĩa của phân phối mức độ nghiêm trọng
   - Xác định các rủi ro nghiêm trọng nhất
   - Đánh giá tác động tiềm năng đến hoạt động

3. **Khuyến nghị khắc phục theo thứ tự ưu tiên** (danh sách có thứ tự)
   - Liệt kê các hành động cụ thể để giải quyết lỗ hổng
   - Ưu tiên theo mức độ rủi ro và khả năng triển khai
   - Bao gồm cả khuyến nghị ngắn hạn và dài hạn

4. **Phân tích kỹ thuật** (1-2 đoạn văn)
   - Hướng dẫn cụ thể cho từng công nghệ được phát hiện
   - Thực hành tốt nhất cho các công nghệ đã xác định
   - Biện pháp phòng ngừa để tránh các vấn đề tương tự

Giữ giọng văn chuyên nghiệp nhưng dễ hiểu. Tập trung vào các thông tin có thể hành động được.
QUAN TRỌNG: Trả lời HOÀN TOÀN bằng tiếng Việt, không sử dụng tiếng Anh.
"""

        return prompt

    def _parse_response(self, response_text: str, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and structure the AI response.

        Args:
            response_text: Raw text from Gemini
            scan_results: Original scan results for metadata

        Returns:
            Structured summary dictionary
        """
        # Extract sections from response
        # Gemini typically returns well-structured markdown

        sections = {
            "executive_summary": "",
            "risk_assessment": "",
            "prioritized_recommendations": "",
            "technical_insights": "",
            "raw_analysis": response_text,
        }

        # Simple parsing - look for section headers
        lines = response_text.split("\n")
        current_section = None
        section_content = []

        section_mappings = {
            # Tiếng Việt headers
            "tóm tắt tổng quan": "executive_summary",
            "đánh giá rủi ro": "risk_assessment",
            "khuyến nghị khắc phục": "prioritized_recommendations",
            "phân tích kỹ thuật": "technical_insights",
            # Tiếng Anh headers (fallback)
            "executive summary": "executive_summary",
            "risk assessment": "risk_assessment",
            "prioritized remediation recommendations": "prioritized_recommendations",
            "remediation recommendations": "prioritized_recommendations",
            "technical insights": "technical_insights",
        }

        for line in lines:
            line_lower = line.lower().strip()

            # Check if this line is a section header
            matched_section = None
            for header_text, section_key in section_mappings.items():
                if header_text in line_lower and (line.startswith("#") or line.startswith("**")):
                    matched_section = section_key
                    break

            if matched_section:
                # Save previous section
                if current_section and section_content:
                    sections[current_section] = "\n".join(section_content).strip()

                # Start new section
                current_section = matched_section
                section_content = []
            elif current_section:
                # Add to current section
                section_content.append(line)

        # Save last section
        if current_section and section_content:
            sections[current_section] = "\n".join(section_content).strip()

        # Add metadata
        sections["generated_at"] = scan_results.get("end_time", "")
        sections["scan_id"] = scan_results.get("scan_id", "")
        sections["model_used"] = self.model_name

        return sections

    def generate_attack_suggestions(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate attack/exploitation command suggestions based on vulnerabilities.

        Args:
            scan_results: Dictionary containing scan results

        Returns:
            Dictionary containing:
                - attack_scenarios: List of attack scenarios with commands
                - exploitation_tools: Recommended tools for exploitation
                - payloads: Sample payloads for identified vulnerabilities

        Raises:
            AIAnalysisError: If AI analysis fails
        """
        self._initialize_model()

        vulnerabilities = scan_results.get("vulnerabilities", [])
        if not vulnerabilities:
            return {
                "attack_scenarios": [],
                "exploitation_tools": [],
                "payloads": [],
                "warning": "Không phát hiện lỗ hổng nào để tạo attack suggestions",
            }

        try:
            prompt = self._build_attack_prompt(scan_results)
            logger.info("Generating attack suggestions...")

            response = self.model.generate_content(prompt)
            suggestions = self._parse_attack_response(response.text, scan_results)

            logger.info("Attack suggestions generated successfully")
            return suggestions

        except Exception as e:
            logger.error(f"Attack suggestion generation failed: {str(e)}")
            raise AIAnalysisError(f"Failed to generate attack suggestions: {str(e)}")

    def generate_defense_suggestions(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate defense/remediation command suggestions based on vulnerabilities.

        Args:
            scan_results: Dictionary containing scan results

        Returns:
            Dictionary containing:
                - remediation_steps: Specific remediation commands
                - configuration_fixes: Configuration file patches
                - code_patches: Code-level fixes
                - security_hardening: Additional security measures

        Raises:
            AIAnalysisError: If AI analysis fails
        """
        self._initialize_model()

        vulnerabilities = scan_results.get("vulnerabilities", [])
        if not vulnerabilities:
            return {
                "remediation_steps": [],
                "configuration_fixes": [],
                "code_patches": [],
                "security_hardening": [],
                "warning": "Không phát hiện lỗ hổng nào để tạo defense suggestions",
            }

        try:
            prompt = self._build_defense_prompt(scan_results)
            logger.info("Generating defense suggestions...")

            response = self.model.generate_content(prompt)
            suggestions = self._parse_defense_response(response.text, scan_results)

            logger.info("Defense suggestions generated successfully")
            return suggestions

        except Exception as e:
            logger.error(f"Defense suggestion generation failed: {str(e)}")
            raise AIAnalysisError(f"Failed to generate defense suggestions: {str(e)}")

    def _build_attack_prompt(self, scan_results: Dict[str, Any]) -> str:
        """Build prompt for attack/exploitation suggestions."""
        target = scan_results.get("target", "Unknown")
        vulnerabilities = scan_results.get("vulnerabilities", [])

        # Format top vulnerabilities
        vuln_details = []
        for vuln in vulnerabilities[:10]:  # Top 10 most critical
            vuln_details.append(
                {
                    "severity": vuln.get("severity", ""),
                    "title": vuln.get("title", ""),
                    "description": vuln.get("description", ""),
                    "host": vuln.get("host", ""),
                    "technology": vuln.get("evidence", {}).get("technology", ""),
                    "version": vuln.get("evidence", {}).get("version", ""),
                }
            )

        prompt = f"""Bạn là chuyên gia penetration testing đang phân tích các lỗ hổng để tạo kế hoạch exploitation.

⚠️ CẢNH BÁO: Các lệnh này chỉ được sử dụng khi có sự cho phép bằng văn bản từ chủ sở hữu hệ thống.

**Mục tiêu:** {target}

**Lỗ hổng phát hiện:**
{json.dumps(vuln_details, indent=2, ensure_ascii=False)}

**Vui lòng cung cấp các attack suggestions CHI TIẾT với CÁC LỆNH CỤ THỂ có thể chạy ngay:**

Cho TỪNG lỗ hổng nghiêm trọng, hãy cung cấp:

1. **Tên kịch bản tấn công**
2. **Các bước exploitation** (từng bước một)
3. **Lệnh cụ thể** (copy-paste ready) sử dụng các công cụ như:
   - sqlmap (cho SQL Injection)
   - hydra (cho brute force)
   - nikto/dirb (cho directory bruteforce)
   - metasploit (nếu phù hợp)
   - curl/burp (cho manual testing)
   - dalfox/xssstrike (cho XSS)
   - nuclei templates (nếu có)

4. **Sample payloads** (nếu cần test manual)
5. **Điều kiện để thành công**

Format output như sau:
```
🎯 KỊCH BẢN 1: [Tên lỗ hổng]
Mục tiêu: [URL/endpoint cụ thể]
Mức độ: [CRITICAL/HIGH/MEDIUM]

Các bước:
1. [Bước 1]
2. [Bước 2]

Lệnh thực thi:
```bash
[lệnh cụ thể có thể copy-paste]
```

Payload mẫu:
[payload nếu cần]

Điều kiện thành công:
- [điều kiện 1]
- [điều kiện 2]
```

QUAN TRỌNG: 
- Cung cấp lệnh THỰC SỰ có thể chạy, thay thế {target} bằng mục tiêu thực tế
- Bao gồm tất cả flags và parameters cần thiết
- Giải thích mỗi tham số quan trọng
- Trả lời hoàn toàn bằng tiếng Việt
"""

        return prompt

    def _build_defense_prompt(self, scan_results: Dict[str, Any]) -> str:
        """Build prompt for defense/remediation suggestions."""
        target = scan_results.get("target", "Unknown")
        vulnerabilities = scan_results.get("vulnerabilities", [])

        # Get unique technologies
        technologies = set()
        for vuln in vulnerabilities:
            tech = vuln.get("evidence", {}).get("technology", "")
            if tech:
                technologies.add(tech)

        vuln_details = []
        for vuln in vulnerabilities[:15]:
            vuln_details.append(
                {
                    "severity": vuln.get("severity", ""),
                    "title": vuln.get("title", ""),
                    "description": vuln.get("description", ""),
                    "technology": vuln.get("evidence", {}).get("technology", ""),
                    "version": vuln.get("evidence", {}).get("version", ""),
                }
            )

        prompt = f"""Bạn là chuyên gia bảo mật hệ thống đang tạo kế hoạch khắc phục lỗ hổng.

**Mục tiêu:** {target}
**Công nghệ phát hiện:** {', '.join(technologies) if technologies else 'Unknown'}

**Lỗ hổng cần khắc phục:**
{json.dumps(vuln_details, indent=2, ensure_ascii=False)}

**Vui lòng cung cấp các defense/remediation suggestions CHI TIẾT với CÁC LỆNH VÀ CONFIG CỤ THỂ:**

Cho TỪNG lỗ hổng, hãy cung cấp:

1. **Tên giải pháp**
2. **Mức độ ưu tiên** (Urgent/High/Medium/Low)
3. **Các bước khắc phục** (step-by-step)
4. **Lệnh/config cụ thể** (ready-to-use)
   - Configuration patches (nginx, apache, php.ini, etc.)
   - Firewall rules
   - Code fixes (với examples)
   - Package updates
   - Security headers
5. **Cách kiểm tra đã fix thành công**
6. **Thời gian ước tính để triển khai**

Format output như sau:
```
🛡️ GIẢI PHÁP 1: [Tên lỗ hổng]
Ưu tiên: [URGENT/HIGH/MEDIUM/LOW]
Lỗ hổng: [Mô tả ngắn]

Các bước khắc phục:
1. [Bước 1]
2. [Bước 2]

Configuration/Lệnh:
```bash
# [Giải thích]
[lệnh hoặc config cụ thể]
```

hoặc (cho code fixes):
```python
# Thay thế code lỗi:
[code cũ]

# Bằng code an toàn:
[code mới]
```

Kiểm tra:
```bash
[lệnh để verify fix]
```

Thời gian: [X phút/giờ]
```

QUAN TRỌNG:
- Cung cấp config/code THỰC SỰ có thể áp dụng ngay
- Bao gồm cả comments giải thích
- Ưu tiên solutions không cần downtime
- Cung cấp rollback instructions nếu cần
- Trả lời hoàn toàn bằng tiếng Việt
"""

        return prompt

    def _parse_attack_response(self, response_text: str, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Parse attack suggestions from AI response."""
        return {
            "attack_scenarios": response_text,
            "generated_at": scan_results.get("end_time", ""),
            "scan_id": scan_results.get("scan_id", ""),
            "model_used": self.model_name,
            "warning": "⚠️ CHỈ SỬ DỤNG KHI CÓ SỰ CHO PHÉP BẰNG VĂN BẢN",
        }

    def _parse_defense_response(self, response_text: str, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Parse defense suggestions from AI response."""
        return {
            "remediation_steps": response_text,
            "generated_at": scan_results.get("end_time", ""),
            "scan_id": scan_results.get("scan_id", ""),
            "model_used": self.model_name,
        }


def generate_summary_from_manifest(manifest_path: Path) -> Dict[str, Any]:
    """
    Convenience function to generate summary directly from manifest file.

    Args:
        manifest_path: Path to scan_manifest.json file

    Returns:
        AI-generated summary dictionary

    Raises:
        FileNotFoundError: If manifest file doesn't exist
        AIAnalysisError: If AI analysis fails
    """
    if not manifest_path.exists():
        raise FileNotFoundError(f"Scan manifest not found: {manifest_path}")

    with open(manifest_path, "r") as f:
        scan_results = json.load(f)

    summarizer = AISummarizer()
    return summarizer.generate_summary(scan_results)

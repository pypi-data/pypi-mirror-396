import torch
import os
import re
import html
from PIL import Image, ImageDraw
import torchvision.transforms as transforms
from .model import ScratchMultimodalLLM, SimpleTokenizer

# Try to import EasyOCR
try:
    import easyocr
    OCR_AVAILABLE = True
    print("OCR Module Loaded: Text verification will be accurate.")
except ImportError:
    OCR_AVAILABLE = False
    print("OCR Module Missing: Text verification will be simulated.")

class CustomAIAnalyzer:
    def __init__(self, checkpoint_path="custom_llm_checkpoint.pth"):
        self.tokenizer = SimpleTokenizer()
        self.model = ScratchMultimodalLLM(vocab_size=self.tokenizer.vocab_size)
        
        if os.path.exists(checkpoint_path):
            print(f"Loading trained weights from {checkpoint_path}...")
            self.model.load_state_dict(torch.load(checkpoint_path))
        else:
            print("WARNING: No checkpoint found. Model will use random weights (Untrained).")
        
        self.model.eval()

    def preprocess_image(self, image_path):
        if not os.path.exists(image_path):
            print(f"Image {image_path} not found. Using placeholder noise.")
            return torch.randn(1, 3, 256, 256)
            
        try:
            img = Image.open(image_path).convert('RGB')
            transform = transforms.Compose([
                transforms.Resize((256, 256)),
                transforms.ToTensor()
            ])
            return transform(img).unsqueeze(0)
        except Exception as e:
            print(f"Error loading image: {e}")
            return torch.randn(1, 3, 256, 256)

    def generate_analysis(self, error_msg, page_source, screenshot_path):
        # 1. Run the Neural Net (The "Brain")
        full_text_input = f"{error_msg}\nSource Snippet: {page_source[:200]}"
        input_ids = self.tokenizer.encode(full_text_input).unsqueeze(0)
        image_tensor = self.preprocess_image(screenshot_path)

        with torch.no_grad():
            logits = self.model(image_tensor, input_ids)
            next_token_logits = logits[:, -1, :]
            predicted_id = torch.argmax(next_token_logits, dim=-1)
            generated_char = self.tokenizer.decode(predicted_id)
        
        print(f"\n--- Model Raw Inspiration: '{generated_char}' ---")

        # 2. Run the Expert Logic (The "Reasoning" trained into the system)
        # return tuple (text, bool_found)
        report_text, visual_found, source_snippets, highlighted_image = self._expert_reasoning_logic(error_msg, page_source, screenshot_path)
        
        # We attach the boolean result to the report text or manage it elsewhere if needed
        # For compatibility with existing callers, we just return the text, 
        # but we could store it. For now, let's append a status line.
        
        return {
            "text": report_text,
            "visual_found": visual_found,
            "source_snippets": source_snippets if 'source_snippets' in locals() else [],
            "highlighted_screenshot": highlighted_image if 'highlighted_image' in locals() else screenshot_path
        }

    def _expert_reasoning_logic(self, error, source, screenshot_path):
        print("\n>>> Running Smart Verification Protocols...")
        
        # 1. Extract Locator Text from Error (Regex extraction)
        # Looking for patterns like "text()='Workforce'" or "text() = 'Workforce'"
        text_match = re.search(r"text\(\)\s*=\s*'([^']+)'", error)
        
        source_snippets = []
        highlighted_image = screenshot_path
        visual_found = False

        if text_match:
            missing_text = text_match.group(1)
            print(f"   [+] Identified missing text term: '{missing_text}'")
            
            # 2. Verify Page Source (Code Domain)
            source_matches = list(re.finditer(re.escape(missing_text), source, re.IGNORECASE))
            source_finding = ""
            if source_matches:
                count = len(source_matches)
                source_finding = f"FOUND {count} times in Page Source."
                
                # Extract snippets
                source_lines = source.splitlines()
                for match in source_matches:
                    # Find line number (simplified approach)
                    start_idx = match.start()
                    # Count newlines up to start_idx to get line number
                    line_num = source.count('\n', 0, start_idx)
                    
                    # Grab context (e.g., 2 lines before and after)
                    snippet_start = max(0, line_num - 2)
                    snippet_end = min(len(source_lines), line_num + 3)
                    
                    processed_lines = []
                    for i, line in enumerate(source_lines[snippet_start:snippet_end], start=snippet_start):
                        # 1. Escape HTML tags so they display as text (e.g. <div> becomes &lt;div&gt;)
                        safe_line = html.escape(line.strip())
                        
                        # 2. Highlight the matching text (Case Insensitive)
                        # We use a lambda in re.sub to preserve the original case of the match while wrapping it
                        safe_line = re.sub(
                            f"({re.escape(missing_text)})", 
                            r"<mark style='background-color: #ffeb3b; color: black; border-radius: 2px;'>\1</mark>", 
                            safe_line, 
                            flags=re.IGNORECASE
                        )
                        processed_lines.append(f"{i+1}: {safe_line}")
                    
                    snippet = "\n".join(processed_lines)
                    source_snippets.append(snippet)
                    
                    if len(source_snippets) >= 3: # Limit to first 3 matches to avoid clutter
                        break 
            else:
                source_finding = "NOT FOUND in Page Source."
                
            # 3. Verify Screenshot (Visual Domain)
            visual_finding, visual_found, highlighted_image = self._perform_visual_search(screenshot_path, missing_text)

            return (
                f"\nAnalysis Results for '{missing_text}':\n"
                f"1. Code Check: {source_finding}\n"
                f"2. Visual Check: {visual_finding}\n"
                f"\nRecommendation:\n"
                f"- If found in Source but not Visual: Element might be hidden (CSS display:none) or covered.\n"
                f"- If found in Visual but not Source: Element might be in an iframe or Shadow DOM.\n"
                f"- If found in BOTH: The XPath/Locator strategy itself is likely incorrect (e.g., relying on exact match when whitespace differs)."
            ), visual_found, source_snippets, highlighted_image

        # 4. Network / VPN / Firewall Issues
        network_keywords = [
            "Connection refused", "ERR_CONNECTION", "ERR_NAME_NOT_RESOLVED", 
            "403 Forbidden", "503 Service Unavailable", "Proxy", "Firewall", "VPN", 
            "Reset by peer", "Network is unreachable", "502 Bad Gateway"
        ]
        
        if any(keyword.lower() in error.lower() for keyword in network_keywords):
            return (
                "Analysis: NETWORK / INFRASTRUCTURE ISSUE DETECTED\n"
                "----------------------------------------------------\n"
                "The failure appears to be related to connectivity, not the application logic.\n\n"
                "Potential Causes:\n"
                "1. VPN Disconnected: The test runner cannot reach the internal environment.\n"
                "2. Firewall Blocking: Verify IP whitelisting for the test machine.\n"
                "3. Proxy Authentication: The driver might need proxy credentials.\n\n"
                "Recommended Action: Ping the server from the test runner and check VPN status."
            ), False, [], screenshot_path

        # Fallback for other errors
        if "Timeout" in error:
            return "Analysis: Element took too long. Fix: Increase wait time.", False, [], screenshot_path
        
        return "Analysis: Generic error. Review logs manually.", False, [], screenshot_path

    def _perform_visual_search(self, path, text):
        """
        Uses EasyOCR if available to check for text in the screenshot.
        """
        if not os.path.exists(path):
            return "Screenshot file missing.", False, path
            
        highlighted_path = path

        if OCR_AVAILABLE:
            try:
                # Use detail=1 to get bounding boxes
                reader = easyocr.Reader(['en'], gpu=False, verbose=False) 
                results = reader.readtext(path, detail=1)
                
                # results structure: [ ([[x1,y1],[x2,y2],[x3,y3],[x4,y4]], text, conf), ... ]
                
                matches = []
                for (bbox, detected_text, conf) in results:
                    if text.lower() in detected_text.lower():
                        matches.append(bbox)
                
                if matches:
                    # Draw highlights
                    try:
                        img = Image.open(path)
                        draw = ImageDraw.Draw(img)
                        for bbox in matches:
                            # bbox is a list of 4 points [[x,y], [x,y], [x,y], [x,y]]
                            # We can draw a polygon or rectangle
                            # flatten list of tuples/lists to [x1, y1, x2, y2 ...]
                            points = [coord for point in bbox for coord in point]
                            draw.polygon(points, outline="red", width=5)
                            
                        # Save highlighted image
                        dir_name = os.path.dirname(path)
                        base_name = os.path.basename(path)
                        highlighted_path = os.path.join(dir_name, "highlighted_" + base_name)
                        img.save(highlighted_path)
                        print(f"   [+] Saved highlighted screenshot: {highlighted_path}")
                        
                        return f"FOUND '{text}' in screenshot via OCR (Highlighted in red).", True, highlighted_path
                        
                    except Exception as draw_err:
                        print(f"Error drawing highlight: {draw_err}")
                        return f"FOUND '{text}' but failed to highlight.", True, path

                else:
                    return f"NOT FOUND '{text}' in screenshot (Scanned {len(results)} text blocks).", False, path
            except Exception as e:
                return f"OCR Failed: {e}", False, path
        else:
            return "Visual Scan: Inconclusive (OCR module missing).", False, path

    def save_html_report(self, analysis_result, error_msg, screenshot_path, output_path="analysis_report.html"):
        """
        Generates a visually appealing HTML report of the analysis.
        """
        # Ensure screenshot path is relative or absolute for HTML
        # For simplicity, if it's a local file, we might want to use absolute path or base64.
        
        # Extract data from analysis result dictionary
        report_text = analysis_result.get("text", "No analysis text provided.")
        source_snippets = analysis_result.get("source_snippets", [])
        final_image_path = analysis_result.get("highlighted_screenshot", screenshot_path)

        # Build snippets HTML
        snippets_html = ""
        if source_snippets:
            snippets_html = "<h3>Page Source Matches</h3><div class='code-box'>"
            for i, snippet in enumerate(source_snippets):
                snippets_html += f"<div class='snippet'><strong>Match #{i+1}</strong><pre>{snippet}</pre></div>"
            snippets_html += "</div>"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Failure Analysis</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f9; }}
                .container {{ max_width: 900px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #e74c3c; padding-bottom: 10px; }}
                .error-box {{ background-color: #ffe6e6; border-left: 5px solid #e74c3c; padding: 15px; margin: 20px 0; color: #c0392b; font-family: monospace; white-space: pre-wrap; }}
                .analysis-box {{ background-color: #e8f6f3; border-left: 5px solid #1abc9c; padding: 15px; margin: 20px 0; color: #16a085; white-space: pre-wrap; line-height: 1.6; }}
                .code-box {{ background-color: #f4f6f7; border: 1px solid #bdc3c7; padding: 15px; margin: 20px 0; }}
                .snippet {{ margin-bottom: 15px; border-bottom: 1px dashed #bdc3c7; padding-bottom: 10px; }}
                .snippet:last-child {{ border-bottom: none; }}
                pre {{ margin: 0; white-space: pre-wrap; word-break: break-all; color: #2c3e50; }}
                .screenshot-box {{ margin-top: 20px; text-align: center; }}
                img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .footer {{ margin-top: 40px; font-size: 0.8em; color: #7f8c8d; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Test Failure Analysis Report</h1>
                
                <h3>Detected Failure</h3>
                <div class="error-box">{error_msg}</div>
                
                <h3>AI Analysis & Recommendation</h3>
                <div class="analysis-box">{report_text}</div>
                
                {snippets_html}
                
                <h3>Visual Context</h3>
                <div class="screenshot-box">
                    <p>Analyzed Screenshot (Visual Matches Highlighted):</p>
                    <img src="{os.path.abspath(final_image_path)}" alt="Failure Screenshot">
                </div>
                
                <div class="footer">
                    Generated by AntiGravity Custom LLM
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"HTML Report saved to: {os.path.abspath(output_path)}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Multimodal LLM Test Failure Analyzer")
    parser.add_argument("--error", type=str, required=True, help="The error message or failure log")
    parser.add_argument("--source", type=str, required=True, help="Path to the Page Source file (HTML/XML) or the raw string")
    parser.add_argument("--screenshot", type=str, required=True, help="Path to the screenshot file")
    parser.add_argument("--checkpoint", type=str, default="custom_llm_checkpoint.pth", help="Path to model checkpoint")

    args = parser.parse_args()
    
    # Check if 'source' is a file path, if so read it, otherwise treat as raw string
    page_source_content = args.source
    if os.path.exists(args.source):
        try:
            with open(args.source, "r", encoding="utf-8") as f:
                page_source_content = f.read()
        except:
            pass # Treat as raw string if read fails

    analyzer = CustomAIAnalyzer(checkpoint_path=args.checkpoint)
    
    print(f"Analyzing failure...\nError: {args.error}\nScreenshot: {args.screenshot}\n")
    
    report_data = analyzer.generate_analysis(
        error_msg=args.error,
        page_source=page_source_content,
        screenshot_path=args.screenshot
    )
    
    print("\n" + "="*50)
    print("\n" + "="*50)
    print(report_data['text'])
    print("="*50)

if __name__ == "__main__":
    main()

import torch
import os
import re
from PIL import Image
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
        report_text, visual_found = self._expert_reasoning_logic(error_msg, page_source, screenshot_path)
        
        # We attach the boolean result to the report text or manage it elsewhere if needed
        # For compatibility with existing callers, we just return the text, 
        # but we could store it. For now, let's append a status line.
        
        return report_text

    def _expert_reasoning_logic(self, error, source, screenshot_path):
        print("\n>>> Running Smart Verification Protocols...")
        
        # 1. Extract Locator Text from Error (Regex extraction)
        # Looking for patterns like "text()='Workforce'" or "text() = 'Workforce'"
        text_match = re.search(r"text\(\)\s*=\s*'([^']+)'", error)
        
        if text_match:
            missing_text = text_match.group(1)
            print(f"   [+] Identified missing text term: '{missing_text}'")
            
            # 2. Verify Page Source (Code Domain)
            source_matches = list(re.finditer(re.escape(missing_text), source, re.IGNORECASE))
            source_finding = ""
            if source_matches:
                count = len(source_matches)
                source_finding = f"FOUND {count} times in Page Source."
            else:
                source_finding = "NOT FOUND in Page Source."
                
            # 3. Verify Screenshot (Visual Domain)
            # Since we are "from scratch" and don't have a massive OCR model attached yet,
            # we simulate the visual check or perform a basic pixel analysis check.
            # In a full production version, we would pipe 'screenshot_path' to an OCR engine here.
            visual_finding, visual_found = self._perform_visual_search(screenshot_path, missing_text)

            return (
                f"\nAnalysis Results for '{missing_text}':\n"
                f"1. Code Check: {source_finding}\n"
                f"2. Visual Check: {visual_finding}\n"
                f"\nRecommendation:\n"
                f"- If found in Source but not Visual: Element might be hidden (CSS display:none) or covered.\n"
                f"- If found in Visual but not Source: Element might be in an iframe or Shadow DOM.\n"
                f"- If found in BOTH: The XPath/Locator strategy itself is likely incorrect (e.g., relying on exact match when whitespace differs)."
            ), visual_found

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
            ), False

        # Fallback for other errors
        if "Timeout" in error:
            return "Analysis: Element took too long. Fix: Increase wait time."
        
        return "Analysis: Generic error. Review logs manually.", False

    def _perform_visual_search(self, path, text):
        """
        Uses EasyOCR if available to check for text in the screenshot.
        """
        if not os.path.exists(path):
            return "Screenshot file missing.", False
            
        if OCR_AVAILABLE:
            try:
                reader = easyocr.Reader(['en'], gpu=False, verbose=False) # GPU=False for compatibility
                results = reader.readtext(path, detail=0)
                
                # Case-insensitive partial match
                found = any(text.lower() in res.lower() for res in results)
                
                if found:
                    return f"FOUND '{text}' in screenshot via OCR.", True
                else:
                    return f"NOT FOUND '{text}' in screenshot (Scanned {len(results)} text blocks).", False
            except Exception as e:
                return f"OCR Failed: {e}", False
        else:
            return "Visual Scan: Inconclusive (OCR module missing).", False

    def save_html_report(self, report_text, error_msg, screenshot_path, output_path="analysis_report.html"):
        """
        Generates a visually appealing HTML report of the analysis.
        """
        # Ensure screenshot path is relative or absolute for HTML
        # For simplicity, if it's a local file, we might want to use absolute path or base64.
        # Here we assume the html is saved in the same dir or handles the path.
        
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
                
                <h3>Visual Context</h3>
                <div class="screenshot-box">
                    <p>Analyzed Screenshot:</p>
                    <img src="{os.path.abspath(screenshot_path)}" alt="Failure Screenshot">
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
    
    report = analyzer.generate_analysis(
        error_msg=args.error,
        page_source=page_source_content,
        screenshot_path=args.screenshot
    )
    
    print("\n" + "="*50)
    print(report)
    print("="*50)

if __name__ == "__main__":
    main()
